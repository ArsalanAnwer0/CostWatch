import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid

from ..models.alert import Alert, AlertRule, AlertSeverity, AlertType
from ..utils.database import get_db_connection, execute_query

logger = logging.getLogger(__name__)

class AlertEngine:
    """Engine for managing alert rules and checking conditions"""
    
    def __init__(self):
        self.operators = {
            'gt': lambda a, b: a > b,
            'gte': lambda a, b: a >= b,
            'lt': lambda a, b: a < b,
            'lte': lambda a, b: a <= b,
            'eq': lambda a, b: a == b,
            'ne': lambda a, b: a != b
        }
    
    def create_rule(self, rule: AlertRule) -> bool:
        """Create new alert rule in database"""
        try:
            query = """
                INSERT INTO alert_rules 
                (rule_id, name, condition, threshold, account_id, notification_channels, enabled, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            params = (
                rule.rule_id,
                rule.name,
                rule.condition,
                rule.threshold,
                rule.account_id,
                ','.join(rule.notification_channels),
                rule.enabled,
                rule.created_at,
                rule.updated_at
            )
            
            execute_query(query, params)
            logger.info(f"Created alert rule: {rule.rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create alert rule: {e}")
            return False
    
    def get_rule(self, rule_id: str) -> Optional[AlertRule]:
        """Get alert rule by ID"""
        try:
            query = "SELECT * FROM alert_rules WHERE rule_id = %s"
            result = execute_query(query, (rule_id,))
            
            if not result:
                return None
            
            row = result[0]
            return AlertRule(
                rule_id=row[0],
                name=row[1],
                condition=row[2],
                threshold=float(row[3]),
                account_id=row[4],
                notification_channels=row[5].split(',') if row[5] else [],
                enabled=bool(row[6]),
                created_at=row[7],
                updated_at=row[8]
            )
            
        except Exception as e:
            logger.error(f"Failed to get alert rule {rule_id}: {e}")
            return None
    
    def get_rules_for_account(self, account_id: str) -> List[AlertRule]:
        """Get all enabled alert rules for account"""
        try:
            query = "SELECT * FROM alert_rules WHERE account_id = %s AND enabled = true"
            result = execute_query(query, (account_id,))
            
            rules = []
            for row in result:
                rule = AlertRule(
                    rule_id=row[0],
                    name=row[1],
                    condition=row[2],
                    threshold=float(row[3]),
                    account_id=row[4],
                    notification_channels=row[5].split(',') if row[5] else [],
                    enabled=bool(row[6]),
                    created_at=row[7],
                    updated_at=row[8]
                )
                rules.append(rule)
            
            return rules
            
        except Exception as e:
            logger.error(f"Failed to get rules for account {account_id}: {e}")
            return []
    
    def check_rules(self, account_id: str, cost_data: Dict[str, Any]) -> List[Alert]:
        """Check if cost data triggers any alert rules"""
        triggered_alerts = []
        
        try:
            rules = self.get_rules_for_account(account_id)
            
            for rule in rules:
                alert = self._evaluate_rule(rule, cost_data)
                if alert:
                    triggered_alerts.append(alert)
            
            return triggered_alerts
            
        except Exception as e:
            logger.error(f"Failed to check rules for account {account_id}: {e}")
            return []
    
    def _evaluate_rule(self, rule: AlertRule, cost_data: Dict[str, Any]) -> Optional[Alert]:
        """Evaluate if a rule condition is met"""
        try:
            # Parse condition (e.g., "total_cost gt 1000")
            condition_parts = rule.condition.split()
            if len(condition_parts) != 3:
                logger.error(f"Invalid condition format: {rule.condition}")
                return None
            
            metric, operator, _ = condition_parts
            
            # Get the metric value from cost data
            metric_value = self._extract_metric_value(metric, cost_data)
            if metric_value is None:
                logger.warning(f"Metric {metric} not found in cost data")
                return None
            
            # Check if condition is met
            operator_func = self.operators.get(operator)
            if not operator_func:
                logger.error(f"Unknown operator: {operator}")
                return None
            
            if operator_func(metric_value, rule.threshold):
                # Create alert
                alert = Alert(
                    alert_id=str(uuid.uuid4()),
                    alert_type=self._determine_alert_type(metric),
                    severity=self._determine_severity(metric_value, rule.threshold, operator),
                    message=self._create_alert_message(rule, metric_value),
                    account_id=rule.account_id,
                    metadata={
                        'rule_id': rule.rule_id,
                        'rule_name': rule.name,
                        'metric': metric,
                        'metric_value': metric_value,
                        'threshold': rule.threshold,
                        'operator': operator,
                        'cost_data': cost_data
                    }
                )
                
                # Log the alert
                self._log_alert(alert)
                
                return alert
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to evaluate rule {rule.rule_id}: {e}")
            return None
    
    def _extract_metric_value(self, metric: str, cost_data: Dict[str, Any]) -> Optional[float]:
        """Extract metric value from cost data"""
        try:
            # Handle nested metrics with dot notation
            keys = metric.split('.')
            value = cost_data
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
            
            # Convert to float if possible
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                try:
                    return float(value)
                except ValueError:
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract metric {metric}: {e}")
            return None
    
    def _determine_alert_type(self, metric: str) -> str:
        """Determine alert type based on metric"""
        if 'budget' in metric.lower():
            return AlertType.BUDGET_EXCEEDED.value
        elif 'anomaly' in metric.lower():
            return AlertType.COST_ANOMALY.value
        elif 'forecast' in metric.lower():
            return AlertType.FORECAST_ALERT.value
        elif 'waste' in metric.lower():
            return AlertType.RESOURCE_WASTE.value
        else:
            return AlertType.COST_THRESHOLD.value
    
    def _determine_severity(self, metric_value: float, threshold: float, operator: str) -> str:
        """Determine alert severity based on how much threshold is exceeded"""
        try:
            if operator in ['gt', 'gte']:
                excess_ratio = metric_value / threshold
                if excess_ratio >= 2.0:
                    return AlertSeverity.CRITICAL.value
                elif excess_ratio >= 1.5:
                    return AlertSeverity.HIGH.value
                elif excess_ratio >= 1.2:
                    return AlertSeverity.MEDIUM.value
                else:
                    return AlertSeverity.LOW.value
            else:
                # For other operators, default to medium severity
                return AlertSeverity.MEDIUM.value
                
        except Exception:
            return AlertSeverity.MEDIUM.value
    
    def _create_alert_message(self, rule: AlertRule, metric_value: float) -> str:
        """Create human-readable alert message"""
        try:
            condition_parts = rule.condition.split()
            metric = condition_parts[0]
            operator = condition_parts[1]
            
            operator_text = {
                'gt': 'exceeded',
                'gte': 'reached or exceeded',
                'lt': 'fallen below',
                'lte': 'fallen to or below',
                'eq': 'equals',
                'ne': 'does not equal'
            }.get(operator, 'triggered')
            
            metric_display = metric.replace('_', ' ').title()
            
            return f"{metric_display} has {operator_text} the threshold. Current value: ${metric_value:,.2f}, Threshold: ${rule.threshold:,.2f}"
            
        except Exception:
            return f"Alert rule '{rule.name}' has been triggered for account {rule.account_id}"
    
    def _log_alert(self, alert: Alert) -> None:
        """Log alert to database"""
        try:
            query = """
                INSERT INTO alert_history 
                (alert_id, alert_type, severity, message, account_id, metadata, created_at, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            params = (
                alert.alert_id,
                alert.alert_type,
                alert.severity,
                alert.message,
                alert.account_id,
                str(alert.metadata),  # Convert dict to string for storage
                alert.created_at,
                alert.status
            )
            
            execute_query(query, params)
            logger.info(f"Logged alert: {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Failed to log alert {alert.alert_id}: {e}")
    
    def get_alert_history(self, account_id: str, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get alert history for account"""
        try:
            query = """
                SELECT alert_id, alert_type, severity, message, metadata, created_at, status
                FROM alert_history 
                WHERE account_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s OFFSET %s
            """
            
            result = execute_query(query, (account_id, limit, offset))
            
            history = []
            for row in result:
                history.append({
                    'alert_id': row[0],
                    'alert_type': row[1],
                    'severity': row[2],
                    'message': row[3],
                    'metadata': row[4],
                    'created_at': row[5].isoformat() if row[5] else None,
                    'status': row[6]
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get alert history for account {account_id}: {e}")
            return []
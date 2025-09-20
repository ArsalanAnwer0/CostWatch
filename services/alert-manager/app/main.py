from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import os
import logging
from typing import Dict, List, Optional
import asyncio
import json

import services.notification_service as notification_service_module
import services.alert_engine as alert_engine_module
import services.service_client as service_client_module
import models.alert as alert_models
import utils.auth as auth_utils

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Initialize services
    notification_service = notification_service_module.NotificationService()
    alert_engine = alert_engine_module.AlertEngine()
    service_client = service_client_module.ServiceClient()
    
    # AWS Account ID from environment
    AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID", "741448937760")
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            "status": "healthy",
            "service": "alert-manager",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        })
    
    @app.route('/ready', methods=['GET'])
    def readiness_check():
        """Readiness check endpoint"""
        try:
            # Check dependent services instead of database
            cost_analyzer_healthy = asyncio.run(service_client.health_check_cost_analyzer())
            analytics_healthy = asyncio.run(service_client.health_check_analytics_engine())
            sns_healthy = notification_service.check_sns_health()
            
            return jsonify({
                "status": "ready",
                "service": "alert-manager",
                "dependencies": {
                    "cost_analyzer": "healthy" if cost_analyzer_healthy else "unhealthy",
                    "analytics_engine": "healthy" if analytics_healthy else "unhealthy",
                    "aws_sns": "healthy" if sns_healthy else "unhealthy",
                    "database": "skipped"
                }
            })
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            return jsonify({"error": "Service not ready"}), 503
    
    @app.route('/alerts/send', methods=['POST'])
    def send_alert():
        """Send immediate alert via AWS SNS"""
        try:
            # Skip API key check for testing
            current_user = auth_utils.bypass_auth_for_testing()
            
            data = request.get_json()
            
            # Create alert object
            alert = alert_models.Alert(
                alert_id=data.get('alert_id'),
                alert_type=data.get('alert_type', 'cost_threshold'),
                severity=data.get('severity', 'medium'),
                message=data.get('message'),
                account_id=data.get('account_id', AWS_ACCOUNT_ID),
                metadata=data.get('metadata', {})
            )
            
            # Send notification via AWS SNS
            result = notification_service.send_alert(alert)
            
            return jsonify({
                "alert_id": alert.alert_id,
                "status": "sent",
                "channels": result.get('channels', []),
                "aws_sns_message_id": result.get('sns_message_id'),
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Alert sending failed: {e}")
            return jsonify({"error": f"Alert sending failed: {str(e)}"}), 500
    
    @app.route('/alerts/rules', methods=['POST'])
    def create_alert_rule():
        """Create new alert rule"""
        try:
            # Skip API key check for testing
            current_user = auth_utils.bypass_auth_for_testing()
            
            data = request.get_json()
            
            # Create alert rule
            rule = alert_models.AlertRule(
                rule_id=data.get('rule_id'),
                name=data.get('name'),
                condition=data.get('condition'),
                threshold=data.get('threshold'),
                account_id=data.get('account_id', AWS_ACCOUNT_ID),
                notification_channels=data.get('notification_channels', ['sns']),
                enabled=data.get('enabled', True)
            )
            
            # Save rule (in-memory for testing)
            success = alert_engine.create_rule(rule)
            
            if success:
                return jsonify({
                    "rule_id": rule.rule_id,
                    "status": "created",
                    "enabled": rule.enabled,
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                return jsonify({"error": "Failed to create rule"}), 500
            
        except Exception as e:
            logger.error(f"Alert rule creation failed: {e}")
            return jsonify({"error": f"Rule creation failed: {str(e)}"}), 500
    
    @app.route('/alerts/rules/<rule_id>', methods=['GET'])
    def get_alert_rule(rule_id):
        """Get alert rule by ID"""
        try:
            # Skip API key check for testing
            current_user = auth_utils.bypass_auth_for_testing()
            
            rule = alert_engine.get_rule(rule_id)
            if not rule:
                return jsonify({"error": "Rule not found"}), 404
            
            return jsonify(rule.to_dict())
            
        except Exception as e:
            logger.error(f"Alert rule retrieval failed: {e}")
            return jsonify({"error": f"Rule retrieval failed: {str(e)}"}), 500
    
    @app.route('/alerts/check', methods=['POST'])
    def check_cost_alerts():
        """Check if cost data triggers any alert rules"""
        try:
            # Skip API key check for testing
            current_user = auth_utils.bypass_auth_for_testing()
            
            data = request.get_json() or {}
            account_id = data.get('account_id', AWS_ACCOUNT_ID)
            
            # Get real cost data from cost-analyzer if not provided
            cost_data = data.get('cost_data')
            if not cost_data:
                end_date = datetime.utcnow().date()
                start_date = end_date - timedelta(days=1)  # Last 24 hours
                
                cost_data = asyncio.run(service_client.get_cost_analysis(
                    account_id,
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                ))
            
            # Check all rules for this account
            triggered_alerts = alert_engine.check_rules(account_id, cost_data)
            
            # Send alerts for triggered rules via AWS SNS
            sent_alerts = []
            for alert in triggered_alerts:
                result = notification_service.send_alert(alert)
                sent_alerts.append({
                    "alert_id": alert.alert_id,
                    "rule_id": alert.metadata.get('rule_id'),
                    "status": "sent",
                    "sns_message_id": result.get('sns_message_id'),
                    "channels": result.get('channels', [])
                })
            
            return jsonify({
                "account_id": account_id,
                "alerts_triggered": len(triggered_alerts),
                "alerts_sent": sent_alerts,
                "cost_data_source": "aws_cost_explorer" if cost_data else "none",
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Cost alert check failed: {e}")
            return jsonify({"error": f"Alert check failed: {str(e)}"}), 500
    
    @app.route('/alerts/monitor', methods=['POST'])
    def start_cost_monitoring():
        """Start continuous cost monitoring with real-time alerts"""
        try:
            # Skip API key check for testing
            current_user = auth_utils.bypass_auth_for_testing()
            
            data = request.get_json() or {}
            account_id = data.get('account_id', AWS_ACCOUNT_ID)
            check_interval = data.get('interval_minutes', 60)  # Default 1 hour
            
            # Get current cost data
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=7)  # Last week for trend analysis
            
            cost_data = asyncio.run(service_client.get_cost_analysis(
                account_id,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            ))
            
            # Get analytics insights
            insights_data = asyncio.run(service_client.get_analytics_insights(
                account_id,
                'cost_optimization'
            ))
            
            # Create monitoring alerts based on current data
            monitoring_alerts = alert_engine.create_monitoring_alerts(cost_data, insights_data)
            
            # Send initial monitoring setup notification
            setup_alert = alert_models.Alert(
                alert_id=f"monitor_{account_id}_{int(datetime.utcnow().timestamp())}",
                alert_type='monitoring_started',
                severity='info',
                message=f"Cost monitoring started for account {account_id}. Checking every {check_interval} minutes.",
                account_id=account_id,
                metadata={
                    'monitoring_enabled': True,
                    'check_interval': check_interval,
                    'rules_count': len(monitoring_alerts),
                    'cost_data_source': 'aws_cost_explorer'
                }
            )
            
            notification_service.send_alert(setup_alert)
            
            return jsonify({
                "account_id": account_id,
                "monitoring_status": "started",
                "check_interval_minutes": check_interval,
                "monitoring_rules": len(monitoring_alerts),
                "initial_cost_data": {
                    "total_cost": cost_data.get('analysis', {}).get('total_cost', 0) if cost_data else 0,
                    "trend": cost_data.get('analysis', {}).get('cost_trend', 'unknown') if cost_data else 'unknown'
                },
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Cost monitoring setup failed: {e}")
            return jsonify({"error": f"Monitoring setup failed: {str(e)}"}), 500
    
    @app.route('/alerts/anomalies/check', methods=['POST'])
    def check_cost_anomalies():
        """Check for cost anomalies using analytics engine"""
        try:
            # Skip API key check for testing
            current_user = auth_utils.bypass_auth_for_testing()
            
            data = request.get_json() or {}
            account_id = data.get('account_id', AWS_ACCOUNT_ID)
            sensitivity = data.get('sensitivity', 'medium')
            
            # Get anomaly detection from analytics engine
            anomalies = asyncio.run(service_client.get_anomaly_detection(
                account_id,
                sensitivity=sensitivity
            ))
            
            # Create alerts for detected anomalies
            anomaly_alerts = []
            if anomalies and anomalies.get('anomalies'):
                for anomaly in anomalies['anomalies']:
                    if anomaly.get('severity') in ['high', 'critical', 'medium']:
                        alert = alert_models.Alert(
                            alert_id=f"anomaly_{account_id}_{int(datetime.utcnow().timestamp())}",
                            alert_type='cost_anomaly',
                            severity=anomaly.get('severity', 'medium'),
                            message=f"Cost anomaly detected: {anomaly.get('message', 'Unknown anomaly')}",
                            account_id=account_id,
                            metadata={
                                'anomaly_type': anomaly.get('type'),
                                'anomaly_data': anomaly,
                                'detection_method': 'analytics_engine'
                            }
                        )
                        
                        # Send anomaly alert
                        result = notification_service.send_alert(alert)
                        anomaly_alerts.append({
                            "alert_id": alert.alert_id,
                            "anomaly_type": anomaly.get('type'),
                            "severity": alert.severity,
                            "sns_message_id": result.get('sns_message_id')
                        })
            
            return jsonify({
                "account_id": account_id,
                "anomalies_detected": len(anomalies.get('anomalies', [])) if anomalies else 0,
                "alerts_sent": len(anomaly_alerts),
                "anomaly_alerts": anomaly_alerts,
                "sensitivity": sensitivity,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Anomaly check failed: {e}")
            return jsonify({"error": f"Anomaly check failed: {str(e)}"}), 500
    
    @app.route('/alerts/history/<account_id>', methods=['GET'])
    def get_alert_history(account_id):
        """Get alert history for account"""
        try:
            # Skip API key check for testing
            current_user = auth_utils.bypass_auth_for_testing()
            
            # Get query parameters
            limit = request.args.get('limit', 50, type=int)
            offset = request.args.get('offset', 0, type=int)
            
            history = alert_engine.get_alert_history(account_id, limit, offset)
            
            return jsonify({
                "account_id": account_id,
                "alerts": history,
                "count": len(history),
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Alert history retrieval failed: {e}")
            return jsonify({"error": f"History retrieval failed: {str(e)}"}), 500
    
    @app.route('/services/health', methods=['GET'])
    def check_services_health():
        """Check health of all dependent services"""
        try:
            current_user = auth_utils.bypass_auth_for_testing()
            
            cost_analyzer_healthy = asyncio.run(service_client.health_check_cost_analyzer())
            analytics_healthy = asyncio.run(service_client.health_check_analytics_engine())
            sns_healthy = notification_service.check_sns_health()
            
            all_healthy = cost_analyzer_healthy and analytics_healthy and sns_healthy
            
            return jsonify({
                "timestamp": datetime.utcnow().isoformat(),
                "services": {
                    "alert_manager": "healthy",
                    "cost_analyzer": "healthy" if cost_analyzer_healthy else "unhealthy",
                    "analytics_engine": "healthy" if analytics_healthy else "unhealthy",
                    "aws_sns": "healthy" if sns_healthy else "unhealthy"
                },
                "overall_status": "healthy" if all_healthy else "degraded",
                "checked_by": current_user
            })
            
        except Exception as e:
            logger.error(f"Failed to check services health: {e}")
            return jsonify({
                "timestamp": datetime.utcnow().isoformat(),
                "services": {
                    "alert_manager": "healthy",
                    "cost_analyzer": "unknown",
                    "analytics_engine": "unknown",
                    "aws_sns": "unknown"
                },
                "overall_status": "unknown",
                "error": str(e),
                "checked_by": "test-user"
            })
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 8004)),  # Use port 8004 to avoid conflicts
        debug=os.getenv('ENVIRONMENT') == 'development'
    )
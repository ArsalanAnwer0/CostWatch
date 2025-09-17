from flask import Flask, request, jsonify
from datetime import datetime
import os
import logging
from typing import Dict, List, Optional

from .services.notification_service import NotificationService
from .services.alert_engine import AlertEngine
from .models.alert import Alert, AlertRule
from .utils.database import get_db_connection
from .utils.auth import verify_api_key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Initialize services
    notification_service = NotificationService()
    alert_engine = AlertEngine()
    
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
            # Check database connection
            db = get_db_connection()
            db.execute("SELECT 1")
            db.close()
            
            return jsonify({
                "status": "ready",
                "service": "alert-manager",
                "database": "connected"
            })
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            return jsonify({"error": "Service not ready"}), 503
    
    @app.route('/alerts/send', methods=['POST'])
    def send_alert():
        """Send immediate alert"""
        try:
            # Verify API key
            api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not verify_api_key(api_key):
                return jsonify({"error": "Unauthorized"}), 401
            
            data = request.get_json()
            
            # Create alert object
            alert = Alert(
                alert_id=data.get('alert_id'),
                alert_type=data.get('alert_type'),
                severity=data.get('severity', 'medium'),
                message=data.get('message'),
                account_id=data.get('account_id'),
                metadata=data.get('metadata', {})
            )
            
            # Send notification
            result = notification_service.send_alert(alert)
            
            return jsonify({
                "alert_id": alert.alert_id,
                "status": "sent",
                "channels": result.get('channels', []),
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Alert sending failed: {e}")
            return jsonify({"error": f"Alert sending failed: {str(e)}"}), 500
    
    @app.route('/alerts/rules', methods=['POST'])
    def create_alert_rule():
        """Create new alert rule"""
        try:
            # Verify API key
            api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not verify_api_key(api_key):
                return jsonify({"error": "Unauthorized"}), 401
            
            data = request.get_json()
            
            # Create alert rule
            rule = AlertRule(
                rule_id=data.get('rule_id'),
                name=data.get('name'),
                condition=data.get('condition'),
                threshold=data.get('threshold'),
                account_id=data.get('account_id'),
                notification_channels=data.get('notification_channels', []),
                enabled=data.get('enabled', True)
            )
            
            # Save rule to database
            alert_engine.create_rule(rule)
            
            return jsonify({
                "rule_id": rule.rule_id,
                "status": "created",
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Alert rule creation failed: {e}")
            return jsonify({"error": f"Rule creation failed: {str(e)}"}), 500
    
    @app.route('/alerts/rules/<rule_id>', methods=['GET'])
    def get_alert_rule(rule_id):
        """Get alert rule by ID"""
        try:
            # Verify API key
            api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not verify_api_key(api_key):
                return jsonify({"error": "Unauthorized"}), 401
            
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
            # Verify API key
            api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not verify_api_key(api_key):
                return jsonify({"error": "Unauthorized"}), 401
            
            data = request.get_json()
            account_id = data.get('account_id')
            cost_data = data.get('cost_data', {})
            
            # Check all rules for this account
            triggered_alerts = alert_engine.check_rules(account_id, cost_data)
            
            # Send alerts for triggered rules
            sent_alerts = []
            for alert in triggered_alerts:
                result = notification_service.send_alert(alert)
                sent_alerts.append({
                    "alert_id": alert.alert_id,
                    "rule_id": alert.metadata.get('rule_id'),
                    "status": "sent",
                    "channels": result.get('channels', [])
                })
            
            return jsonify({
                "account_id": account_id,
                "alerts_triggered": len(triggered_alerts),
                "alerts_sent": sent_alerts,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Cost alert check failed: {e}")
            return jsonify({"error": f"Alert check failed: {str(e)}"}), 500
    
    @app.route('/alerts/history/<account_id>', methods=['GET'])
    def get_alert_history(account_id):
        """Get alert history for account"""
        try:
            # Verify API key
            api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not verify_api_key(api_key):
                return jsonify({"error": "Unauthorized"}), 401
            
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
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5001)),
        debug=os.getenv('ENVIRONMENT') == 'development'
    )
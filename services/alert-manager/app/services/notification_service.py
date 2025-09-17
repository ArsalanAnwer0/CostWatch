import logging
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any
import os
import json
from datetime import datetime

from ..models.alert import Alert, NotificationChannel

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for sending notifications through multiple channels"""
    
    def __init__(self):
        self.channels = {
            'slack': self._send_slack_notification,
            'email': self._send_email_notification,
            'teams': self._send_teams_notification,
            'webhook': self._send_webhook_notification
        }
    
    def send_alert(self, alert: Alert) -> Dict[str, Any]:
        """Send alert through configured notification channels"""
        results = {
            'alert_id': alert.alert_id,
            'channels': [],
            'success_count': 0,
            'failure_count': 0,
            'errors': []
        }
        
        try:
            # Get notification channels for this alert type/severity
            channels = self._get_notification_channels(alert)
            
            for channel in channels:
                try:
                    # Send notification through specific channel
                    result = self._send_notification(alert, channel)
                    
                    if result.get('success'):
                        results['channels'].append({
                            'channel': channel.name,
                            'type': channel.channel_type,
                            'status': 'sent',
                            'timestamp': datetime.utcnow().isoformat()
                        })
                        results['success_count'] += 1
                    else:
                        results['channels'].append({
                            'channel': channel.name,
                            'type': channel.channel_type,
                            'status': 'failed',
                            'error': result.get('error'),
                            'timestamp': datetime.utcnow().isoformat()
                        })
                        results['failure_count'] += 1
                        results['errors'].append(f"{channel.name}: {result.get('error')}")
                
                except Exception as e:
                    logger.error(f"Failed to send notification via {channel.name}: {e}")
                    results['failure_count'] += 1
                    results['errors'].append(f"{channel.name}: {str(e)}")
            
            return results
            
        except Exception as e:
            logger.error(f"Notification service error: {e}")
            results['errors'].append(f"Service error: {str(e)}")
            return results
    
    def _send_notification(self, alert: Alert, channel: NotificationChannel) -> Dict[str, Any]:
        """Send notification through specific channel"""
        try:
            handler = self.channels.get(channel.channel_type)
            if not handler:
                return {'success': False, 'error': f"Unsupported channel type: {channel.channel_type}"}
            
            return handler(alert, channel)
            
        except Exception as e:
            logger.error(f"Channel notification error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _send_slack_notification(self, alert: Alert, channel: NotificationChannel) -> Dict[str, Any]:
        """Send Slack notification"""
        try:
            webhook_url = channel.config.get('webhook_url')
            if not webhook_url:
                return {'success': False, 'error': 'Slack webhook URL not configured'}
            
            # Create Slack message
            color = self._get_alert_color(alert.severity)
            message = {
                "attachments": [
                    {
                        "color": color,
                        "title": f"CostWatch Alert - {alert.alert_type.replace('_', ' ').title()}",
                        "text": alert.message,
                        "fields": [
                            {
                                "title": "Account ID",
                                "value": alert.account_id,
                                "short": True
                            },
                            {
                                "title": "Severity",
                                "value": alert.severity.upper(),
                                "short": True
                            },
                            {
                                "title": "Alert ID",
                                "value": alert.alert_id,
                                "short": True
                            },
                            {
                                "title": "Timestamp",
                                "value": alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC'),
                                "short": True
                            }
                        ],
                        "footer": "CostWatch Alert Manager"
                    }
                ]
            }
            
            # Add metadata fields if available
            if alert.metadata:
                for key, value in alert.metadata.items():
                    if key not in ['rule_id', 'internal']:
                        message["attachments"][0]["fields"].append({
                            "title": key.replace('_', ' ').title(),
                            "value": str(value),
                            "short": True
                        })
            
            # Send to Slack
            response = requests.post(webhook_url, json=message, timeout=10)
            response.raise_for_status()
            
            return {'success': True, 'response': response.text}
            
        except Exception as e:
            logger.error(f"Slack notification failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _send_email_notification(self, alert: Alert, channel: NotificationChannel) -> Dict[str, Any]:
        """Send email notification"""
        try:
            smtp_config = channel.config
            required_fields = ['smtp_host', 'smtp_port', 'username', 'password', 'recipients']
            
            for field in required_fields:
                if field not in smtp_config:
                    return {'success': False, 'error': f'Email config missing: {field}'}
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = smtp_config['username']
            msg['To'] = ', '.join(smtp_config['recipients'])
            msg['Subject'] = f"CostWatch Alert: {alert.alert_type.replace('_', ' ').title()}"
            
            # Create HTML body
            html_body = self._create_email_html(alert)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(smtp_config['smtp_host'], smtp_config['smtp_port']) as server:
                server.starttls()
                server.login(smtp_config['username'], smtp_config['password'])
                server.send_message(msg)
            
            return {'success': True, 'recipients': smtp_config['recipients']}
            
        except Exception as e:
            logger.error(f"Email notification failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _send_teams_notification(self, alert: Alert, channel: NotificationChannel) -> Dict[str, Any]:
        """Send Microsoft Teams notification"""
        try:
            webhook_url = channel.config.get('webhook_url')
            if not webhook_url:
                return {'success': False, 'error': 'Teams webhook URL not configured'}
            
            # Create Teams message
            color = self._get_alert_color(alert.severity)
            message = {
                "@type": "MessageCard",
                "@context": "https://schema.org/extensions",
                "summary": f"CostWatch Alert - {alert.alert_type}",
                "themeColor": color.replace('#', ''),
                "sections": [
                    {
                        "activityTitle": f"CostWatch Alert - {alert.alert_type.replace('_', ' ').title()}",
                        "activitySubtitle": f"Severity: {alert.severity.upper()}",
                        "text": alert.message,
                        "facts": [
                            {"name": "Account ID", "value": alert.account_id},
                            {"name": "Alert ID", "value": alert.alert_id},
                            {"name": "Timestamp", "value": alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}
                        ]
                    }
                ]
            }
            
            # Add metadata facts
            if alert.metadata:
                for key, value in alert.metadata.items():
                    if key not in ['rule_id', 'internal']:
                        message["sections"][0]["facts"].append({
                            "name": key.replace('_', ' ').title(),
                            "value": str(value)
                        })
            
            # Send to Teams
            response = requests.post(webhook_url, json=message, timeout=10)
            response.raise_for_status()
            
            return {'success': True, 'response': response.text}
            
        except Exception as e:
            logger.error(f"Teams notification failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _send_webhook_notification(self, alert: Alert, channel: NotificationChannel) -> Dict[str, Any]:
        """Send webhook notification"""
        try:
            webhook_url = channel.config.get('url')
            if not webhook_url:
                return {'success': False, 'error': 'Webhook URL not configured'}
            
            headers = channel.config.get('headers', {'Content-Type': 'application/json'})
            payload = {
                'alert': alert.to_dict(),
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'costwatch-alert-manager'
            }
            
            response = requests.post(webhook_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            return {'success': True, 'status_code': response.status_code}
            
        except Exception as e:
            logger.error(f"Webhook notification failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_notification_channels(self, alert: Alert) -> List[NotificationChannel]:
        """Get notification channels for alert"""
        # This would typically query the database for configured channels
        # For now, return default channels based on environment variables
        channels = []
        
        # Slack channel
        if os.getenv('SLACK_WEBHOOK_URL'):
            channels.append(NotificationChannel(
                channel_id='default-slack',
                channel_type='slack',
                name='Default Slack',
                config={'webhook_url': os.getenv('SLACK_WEBHOOK_URL')}
            ))
        
        # Email channel
        if all(os.getenv(key) for key in ['SMTP_HOST', 'SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD', 'EMAIL_RECIPIENTS']):
            channels.append(NotificationChannel(
                channel_id='default-email',
                channel_type='email',
                name='Default Email',
                config={
                    'smtp_host': os.getenv('SMTP_HOST'),
                    'smtp_port': int(os.getenv('SMTP_PORT', 587)),
                    'username': os.getenv('SMTP_USERNAME'),
                    'password': os.getenv('SMTP_PASSWORD'),
                    'recipients': os.getenv('EMAIL_RECIPIENTS').split(',')
                }
            ))
        
        return channels
    
    def _get_alert_color(self, severity: str) -> str:
        """Get color code for alert severity"""
        colors = {
            'low': '#36a64f',      # Green
            'medium': '#ff9500',   # Orange
            'high': '#ff0000',     # Red
            'critical': '#8B0000'  # Dark Red
        }
        return colors.get(severity.lower(), '#808080')  # Default gray
    
    def _create_email_html(self, alert: Alert) -> str:
        """Create HTML email body"""
        severity_color = self._get_alert_color(alert.severity)
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px;">
            <div style="background-color: {severity_color}; color: white; padding: 15px; border-radius: 5px;">
                <h2 style="margin: 0;">CostWatch Alert - {alert.alert_type.replace('_', ' ').title()}</h2>
                <p style="margin: 5px 0;">Severity: {alert.severity.upper()}</p>
            </div>
            
            <div style="padding: 20px; border: 1px solid #ddd; border-radius: 5px; margin-top: 10px;">
                <h3>Alert Details</h3>
                <p><strong>Message:</strong> {alert.message}</p>
                <p><strong>Account ID:</strong> {alert.account_id}</p>
                <p><strong>Alert ID:</strong> {alert.alert_id}</p>
                <p><strong>Timestamp:</strong> {alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                
                {self._format_metadata_html(alert.metadata) if alert.metadata else ''}
            </div>
            
            <div style="margin-top: 20px; font-size: 12px; color: #666;">
                <p>This alert was generated by CostWatch Alert Manager.</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _format_metadata_html(self, metadata: Dict[str, Any]) -> str:
        """Format metadata for HTML email"""
        if not metadata:
            return ""
        
        html = "<h4>Additional Information</h4><ul>"
        for key, value in metadata.items():
            if key not in ['rule_id', 'internal']:
                html += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>"
        html += "</ul>"
        
        return html
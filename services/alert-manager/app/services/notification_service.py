import logging
import boto3
from botocore.exceptions import ClientError
from typing import Dict, List, Optional, Any
import os
import json
from datetime import datetime

from models.alert import Alert

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for sending notifications through AWS SNS and other channels"""
    
    def __init__(self):
        # Initialize AWS SNS client
        try:
            self.sns_client = boto3.client('sns')
            self.sns_topic_arn = os.getenv('SNS_TOPIC_ARN')
            logger.info("AWS SNS client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SNS client: {e}")
            self.sns_client = None
            self.sns_topic_arn = None
    
    def send_alert(self, alert: Alert) -> Dict[str, Any]:
        """Send alert through AWS SNS"""
        results = {
            'alert_id': alert.alert_id,
            'channels': [],
            'success_count': 0,
            'failure_count': 0,
            'errors': [],
            'sns_message_id': None
        }
        
        try:
            # Send via AWS SNS
            sns_result = self._send_sns_notification(alert)
            
            if sns_result.get('success'):
                results['channels'].append({
                    'channel': 'aws_sns',
                    'type': 'sns',
                    'status': 'sent',
                    'message_id': sns_result.get('message_id'),
                    'timestamp': datetime.utcnow().isoformat()
                })
                results['success_count'] += 1
                results['sns_message_id'] = sns_result.get('message_id')
            else:
                results['channels'].append({
                    'channel': 'aws_sns',
                    'type': 'sns',
                    'status': 'failed',
                    'error': sns_result.get('error'),
                    'timestamp': datetime.utcnow().isoformat()
                })
                results['failure_count'] += 1
                results['errors'].append(f"SNS: {sns_result.get('error')}")
            
            # Also try email if configured (fallback)
            if os.getenv('BACKUP_EMAIL'):
                email_result = self._send_simple_email(alert)
                if email_result.get('success'):
                    results['channels'].append({
                        'channel': 'backup_email',
                        'type': 'email',
                        'status': 'sent',
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    results['success_count'] += 1
            
            return results
            
        except Exception as e:
            logger.error(f"Notification service error: {e}")
            results['errors'].append(f"Service error: {str(e)}")
            return results
    
    def _send_sns_notification(self, alert: Alert) -> Dict[str, Any]:
        """Send notification via AWS SNS"""
        try:
            if not self.sns_client:
                return {'success': False, 'error': 'SNS client not initialized'}
            
            if not self.sns_topic_arn:
                # Try to send to a default topic or create one
                topic_name = os.getenv('SNS_TOPIC_NAME', 'costwatch-alerts')
                topic_arn = self._get_or_create_topic(topic_name)
                if not topic_arn:
                    return {'success': False, 'error': 'No SNS topic configured'}
                self.sns_topic_arn = topic_arn
            
            # Create SNS message
            message = self._create_sns_message(alert)
            subject = f"CostWatch Alert: {alert.alert_type.replace('_', ' ').title()}"
            
            # Send to SNS topic
            response = self.sns_client.publish(
                TopicArn=self.sns_topic_arn,
                Message=message,
                Subject=subject,
                MessageAttributes={
                    'alert_type': {
                        'DataType': 'String',
                        'StringValue': alert.alert_type
                    },
                    'severity': {
                        'DataType': 'String',
                        'StringValue': alert.severity
                    },
                    'account_id': {
                        'DataType': 'String',
                        'StringValue': alert.account_id
                    }
                }
            )
            
            message_id = response.get('MessageId')
            logger.info(f"SNS notification sent successfully: {message_id}")
            
            return {
                'success': True,
                'message_id': message_id,
                'topic_arn': self.sns_topic_arn
            }
            
        except ClientError as e:
            error_msg = f"AWS SNS error: {e.response['Error']['Message']}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
        except Exception as e:
            error_msg = f"SNS notification failed: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
    
    def _create_sns_message(self, alert: Alert) -> str:
        """Create formatted SNS message"""
        try:
            # Create structured message for SNS
            message_data = {
                'alert_id': alert.alert_id,
                'alert_type': alert.alert_type,
                'severity': alert.severity.upper(),
                'message': alert.message,
                'account_id': alert.account_id,
                'timestamp': alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC'),
                'metadata': alert.metadata or {}
            }
            
            # Create human-readable message
            formatted_message = f"""
CostWatch Alert Notification

Alert Type: {alert.alert_type.replace('_', ' ').title()}
Severity: {alert.severity.upper()}
Account ID: {alert.account_id}
Alert ID: {alert.alert_id}

Message: {alert.message}

Timestamp: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}

Additional Details:
{self._format_metadata(alert.metadata)}

---
This alert was generated by CostWatch Alert Manager.
For more information, check your CostWatch dashboard.
            """.strip()
            
            return formatted_message
            
        except Exception as e:
            logger.error(f"Failed to create SNS message: {e}")
            return f"CostWatch Alert: {alert.message}"
    
    def _format_metadata(self, metadata: Optional[Dict[str, Any]]) -> str:
        """Format metadata for display"""
        if not metadata:
            return "No additional details available."
        
        formatted = []
        for key, value in metadata.items():
            if key not in ['internal', 'raw_data']:
                display_key = key.replace('_', ' ').title()
                if isinstance(value, dict):
                    formatted.append(f"{display_key}: {json.dumps(value, indent=2)}")
                else:
                    formatted.append(f"{display_key}: {value}")
        
        return '\n'.join(formatted) if formatted else "No additional details available."
    
    def _get_or_create_topic(self, topic_name: str) -> Optional[str]:
        """Get existing SNS topic or create a new one"""
        try:
            if not self.sns_client:
                return None
            
            # Try to create topic (idempotent operation)
            response = self.sns_client.create_topic(Name=topic_name)
            topic_arn = response['TopicArn']
            
            logger.info(f"Using SNS topic: {topic_arn}")
            return topic_arn
            
        except Exception as e:
            logger.error(f"Failed to get/create SNS topic: {e}")
            return None
    
    def _send_simple_email(self, alert: Alert) -> Dict[str, Any]:
        """Send simple email notification (fallback)"""
        try:
            backup_email = os.getenv('BACKUP_EMAIL')
            if not backup_email:
                return {'success': False, 'error': 'No backup email configured'}
            
            # Use AWS SES if available, otherwise skip
            try:
                ses_client = boto3.client('ses')
                
                email_body = f"""
CostWatch Alert

Alert: {alert.alert_type.replace('_', ' ').title()}
Severity: {alert.severity.upper()}
Account: {alert.account_id}
Message: {alert.message}
Time: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}

Alert ID: {alert.alert_id}
                """.strip()
                
                response = ses_client.send_email(
                    Source=backup_email,
                    Destination={'ToAddresses': [backup_email]},
                    Message={
                        'Subject': {'Data': f"CostWatch Alert: {alert.alert_type}"},
                        'Body': {'Text': {'Data': email_body}}
                    }
                )
                
                return {'success': True, 'message_id': response['MessageId']}
                
            except Exception as e:
                logger.warning(f"SES email fallback failed: {e}")
                return {'success': False, 'error': 'SES not available'}
            
        except Exception as e:
            logger.error(f"Email fallback failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def check_sns_health(self) -> bool:
        """Check if SNS service is available"""
        try:
            if not self.sns_client:
                return False
            
            # Simple SNS health check
            self.sns_client.list_topics()
            return True
            
        except Exception as e:
            logger.error(f"SNS health check failed: {e}")
            return False
    
    def setup_sns_subscription(self, topic_arn: str, protocol: str, endpoint: str) -> Dict[str, Any]:
        """Set up SNS subscription for notifications"""
        try:
            if not self.sns_client:
                return {'success': False, 'error': 'SNS client not available'}
            
            response = self.sns_client.subscribe(
                TopicArn=topic_arn,
                Protocol=protocol,  # 'email', 'sms', 'http', 'https'
                Endpoint=endpoint
            )
            
            subscription_arn = response.get('SubscriptionArn')
            
            return {
                'success': True,
                'subscription_arn': subscription_arn,
                'topic_arn': topic_arn,
                'protocol': protocol,
                'endpoint': endpoint
            }
            
        except Exception as e:
            logger.error(f"Failed to set up SNS subscription: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_test_alert(self, account_id: str) -> Dict[str, Any]:
        """Send a test alert to verify SNS integration"""
        try:
            test_alert = Alert(
                alert_id=f"test_{int(datetime.utcnow().timestamp())}",
                alert_type='test_alert',
                severity='info',
                message='This is a test alert to verify SNS integration is working correctly.',
                account_id=account_id,
                metadata={
                    'test': True,
                    'integration_check': 'aws_sns',
                    'service': 'alert-manager'
                }
            )
            
            result = self.send_alert(test_alert)
            
            return {
                'test_successful': result['success_count'] > 0,
                'alert_id': test_alert.alert_id,
                'result': result
            }
            
        except Exception as e:
            logger.error(f"Test alert failed: {e}")
            return {
                'test_successful': False,
                'error': str(e)
            }
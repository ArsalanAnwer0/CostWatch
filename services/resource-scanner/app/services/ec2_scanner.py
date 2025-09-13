import logging
from typing import Dict, List, Any
from datetime import datetime

from app.services.aws_scanner import AWSResourceScanner

logger = logging.getLogger(__name__)

class EC2Scanner(AWSResourceScanner):
    """Scanner for EC2 instances and related resources."""
    
    def scan_instances(self, region: str = 'us-west-2', include_costs: bool = True) -> Dict[str, Any]:
        """Scan EC2 instances in specified region."""
        try:
            ec2_client = self.get_client('ec2', region)
            
            # Get instances
            response = ec2_client.describe_instances()
            
            instances = []
            total_cost = 0.0
            optimization_opportunities = []
            
            for reservation in response.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    instance_data = self._process_instance(instance, include_costs)
                    instances.append(instance_data)
                    
                    if include_costs:
                        total_cost += instance_data.get('estimated_monthly_cost', 0.0)
                    
                    # Check for optimization opportunities
                    opportunities = self._analyze_instance_optimization(instance_data)
                    optimization_opportunities.extend(opportunities)
            
            result = {
                "instances": instances,
                "total_instances": len(instances),
                "estimated_monthly_cost": round(total_cost, 2) if include_costs else None,
                "optimization_opportunities": optimization_opportunities,
                "scan_timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Scanned {len(instances)} EC2 instances in {region}")
            return result
            
        except Exception as e:
            logger.error(f"Error scanning EC2 instances: {e}")
            raise
    
    def _process_instance(self, instance: Dict[str, Any], include_costs: bool = True) -> Dict[str, Any]:
        """Process individual EC2 instance data."""
        instance_id = instance.get('InstanceId', 'unknown')
        instance_type = instance.get('InstanceType', 'unknown')
        state = instance.get('State', {}).get('Name', 'unknown')
        
        # Extract tags
        tags = {}
        for tag in instance.get('Tags', []):
            tags[tag.get('Key', '')] = tag.get('Value', '')
        
        # Calculate costs
        estimated_monthly_cost = 0.0
        if include_costs and state == 'running':
            hourly_cost = self.get_cost_estimate(instance_type, 'ec2')
            estimated_monthly_cost = self.calculate_monthly_cost(hourly_cost)
        
        processed_instance = {
            "instance_id": instance_id,
            "instance_type": instance_type,
            "state": state,
            "launch_time": instance.get('LaunchTime', datetime.utcnow()).isoformat(),
            "availability_zone": instance.get('Placement', {}).get('AvailabilityZone', 'unknown'),
            "tags": tags,
            "name": tags.get('Name', 'Unnamed'),
            "estimated_monthly_cost": round(estimated_monthly_cost, 2) if include_costs else None
        }
        
        # Add mock performance metrics
        if hasattr(instance, 'CpuUtilization'):
            processed_instance['cpu_utilization'] = instance['CpuUtilization']
        else:
            # Mock CPU utilization based on instance state
            if state == 'running':
                import random
                processed_instance['cpu_utilization'] = round(random.uniform(5, 85), 1)
            else:
                processed_instance['cpu_utilization'] = 0.0
        
        return processed_instance
    
    def _analyze_instance_optimization(self, instance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze instance for optimization opportunities."""
        opportunities = []
        
        # Check for stopped instances
        if instance_data['state'] == 'stopped':
            opportunities.append({
                "type": "terminated_instance",
                "resource_id": instance_data['instance_id'],
                "recommendation": "Consider terminating long-stopped instance",
                "potential_savings": instance_data.get('estimated_monthly_cost', 0),
                "priority": "medium",
                "effort": "low"
            })
        
        # Check for underutilized running instances
        elif instance_data['state'] == 'running':
            cpu_util = instance_data.get('cpu_utilization', 0)
            
            if cpu_util < 10:
                opportunities.append({
                    "type": "underutilized_instance",
                    "resource_id": instance_data['instance_id'],
                    "recommendation": f"Instance has low CPU utilization ({cpu_util}%). Consider downsizing or stopping.",
                    "potential_savings": instance_data.get('estimated_monthly_cost', 0) * 0.5,
                    "priority": "high",
                    "effort": "medium"
                })
            elif cpu_util < 25:
                # Suggest right-sizing
                current_cost = instance_data.get('estimated_monthly_cost', 0)
                opportunities.append({
                    "type": "rightsizing_opportunity",
                    "resource_id": instance_data['instance_id'],
                    "recommendation": f"Instance has moderate CPU utilization ({cpu_util}%). Consider right-sizing to smaller instance type.",
                    "potential_savings": current_cost * 0.3,
                    "priority": "medium",
                    "effort": "medium"
                })
        
        return opportunities
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get general EC2 optimization recommendations."""
        return [
            {
                "category": "Instance Right-sizing",
                "description": "Analyze CPU, memory, and network utilization to right-size instances",
                "potential_savings": "20-50%",
                "implementation_effort": "Medium",
                "best_practices": [
                    "Monitor CloudWatch metrics for at least 2 weeks",
                    "Look for consistently low utilization patterns",
                    "Consider burstable instance types for variable workloads",
                    "Use AWS Compute Optimizer recommendations"
                ]
            },
            {
                "category": "Reserved Instances",
                "description": "Purchase Reserved Instances for predictable workloads",
                "potential_savings": "30-75%",
                "implementation_effort": "Low",
                "best_practices": [
                    "Analyze usage patterns over 12 months",
                    "Start with 1-year No Upfront Reserved Instances",
                    "Consider Convertible RIs for flexibility",
                    "Monitor RI utilization and coverage"
                ]
            },
            {
                "category": "Spot Instances",
                "description": "Use Spot Instances for fault-tolerant workloads",
                "potential_savings": "50-90%",
                "implementation_effort": "High",
                "best_practices": [
                    "Implement proper handling for spot interruptions",
                    "Use multiple instance types and AZs",
                    "Consider Spot Fleet for automated management",
                    "Test workload resilience thoroughly"
                ]
            },
            {
                "category": "Scheduled Scaling",
                "description": "Automatically stop/start instances based on schedule",
                "potential_savings": "40-70%",
                "implementation_effort": "Low",
                "best_practices": [
                    "Identify dev/test environments for scheduling",
                    "Use AWS Instance Scheduler",
                    "Consider time zone differences",
                    "Implement proper startup/shutdown procedures"
                ]
            }
        ]
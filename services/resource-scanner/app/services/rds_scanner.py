import logging
from typing import Dict, List, Any
from datetime import datetime

from .aws_scanner import AWSResourceScanner

logger = logging.getLogger(__name__)

class RDSScanner(AWSResourceScanner):
    """Scanner for RDS instances and related resources."""
    
    def scan_databases(self, region: str = 'us-west-2', include_costs: bool = True) -> Dict[str, Any]:
        """Scan RDS instances in specified region."""
        try:
            rds_client = self.get_client('rds', region)
            
            # Get RDS instances
            response = rds_client.describe_db_instances()
            
            databases = []
            total_cost = 0.0
            optimization_opportunities = []
            
            for db_instance in response.get('DBInstances', []):
                db_data = self._process_database(db_instance, include_costs)
                databases.append(db_data)
                
                if include_costs:
                    total_cost += db_data.get('estimated_monthly_cost', 0.0)
                
                # Check for optimization opportunities
                opportunities = self._analyze_database_optimization(db_data)
                optimization_opportunities.extend(opportunities)
            
            result = {
                "databases": databases,
                "total_databases": len(databases),
                "estimated_monthly_cost": round(total_cost, 2) if include_costs else None,
                "optimization_opportunities": optimization_opportunities,
                "scan_timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Scanned {len(databases)} RDS instances in {region}")
            return result
            
        except Exception as e:
            logger.error(f"Error scanning RDS instances: {e}")
            raise
    
    def _process_database(self, db_instance: Dict[str, Any], include_costs: bool = True) -> Dict[str, Any]:
        """Process individual RDS instance data."""
        db_identifier = db_instance.get('DBInstanceIdentifier', 'unknown')
        db_class = db_instance.get('DBInstanceClass', 'unknown')
        status = db_instance.get('DBInstanceStatus', 'unknown')
        engine = db_instance.get('Engine', 'unknown')
        
        # Calculate costs
        estimated_monthly_cost = 0.0
        if include_costs and status == 'available':
            hourly_cost = self.get_cost_estimate(db_class, 'rds')
            estimated_monthly_cost = self.calculate_monthly_cost(hourly_cost)
            
            # Add storage costs
            allocated_storage = db_instance.get('AllocatedStorage', 0)
            storage_cost = allocated_storage * 0.115  # GP2 storage cost per GB/month
            estimated_monthly_cost += storage_cost
        
        processed_db = {
            "db_identifier": db_identifier,
            "db_instance_class": db_class,
            "status": status,
            "engine": engine,
            "engine_version": db_instance.get('EngineVersion', 'unknown'),
            "creation_time": db_instance.get('InstanceCreateTime', datetime.utcnow()).isoformat(),
            "availability_zone": db_instance.get('AvailabilityZone', 'unknown'),
            "multi_az": db_instance.get('MultiAZ', False),
            "storage_encrypted": db_instance.get('StorageEncrypted', False),
            "allocated_storage_gb": db_instance.get('AllocatedStorage', 0),
            "estimated_monthly_cost": round(estimated_monthly_cost, 2) if include_costs else None
        }
        
        # Add mock performance metrics
        if hasattr(db_instance, 'CpuUtilization'):
            processed_db['cpu_utilization'] = db_instance['CpuUtilization']
        else:
            # Mock CPU utilization
            if status == 'available':
                import random
                processed_db['cpu_utilization'] = round(random.uniform(10, 80), 1)
            else:
                processed_db['cpu_utilization'] = 0.0
        
        return processed_db
    
    def _analyze_database_optimization(self, db_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze database for optimization opportunities."""
        opportunities = []
        
        if db_data['status'] != 'available':
            return opportunities
        
        # Check for underutilized databases
        cpu_util = db_data.get('cpu_utilization', 0)
        
        if cpu_util < 15:
            opportunities.append({
                "type": "underutilized_database",
                "resource_id": db_data['db_identifier'],
                "recommendation": f"Database has low CPU utilization ({cpu_util}%). Consider downsizing instance class.",
                "potential_savings": db_data.get('estimated_monthly_cost', 0) * 0.4,
                "priority": "high",
                "effort": "medium"
            })
        
        # Check for unencrypted databases
        if not db_data.get('storage_encrypted', False):
            opportunities.append({
                "type": "security_improvement",
                "resource_id": db_data['db_identifier'],
                "recommendation": "Enable encryption at rest for better security compliance.",
                "potential_savings": 0,  # Security improvement, not cost savings
                "priority": "medium",
                "effort": "high",
                "category": "security"
            })
        
        # Check for single-AZ production databases
        if not db_data.get('multi_az', False) and 'prod' in db_data['db_identifier'].lower():
            opportunities.append({
                "type": "availability_improvement",
                "resource_id": db_data['db_identifier'],
                "recommendation": "Enable Multi-AZ for production database to improve availability.",
                "potential_savings": 0,  # Availability improvement
                "priority": "high",
                "effort": "medium",
                "category": "availability"
            })
        
        # Check for old engine versions
        engine = db_data.get('engine', '')
        if engine in ['mysql', 'postgres'] and db_data.get('engine_version', '').startswith('5.'):
            opportunities.append({
                "type": "maintenance_improvement",
                "resource_id": db_data['db_identifier'],
                "recommendation": "Upgrade to newer engine version for better performance and security.",
                "potential_savings": 0,
                "priority": "medium",
                "effort": "high",
                "category": "maintenance"
            })
        
        return opportunities
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get general RDS optimization recommendations."""
        return [
            {
                "category": "Instance Right-sizing",
                "description": "Optimize RDS instance classes based on actual usage patterns",
                "potential_savings": "25-50%",
                "implementation_effort": "Medium",
                "best_practices": [
                    "Monitor CloudWatch metrics for CPU, memory, and IOPS",
                    "Analyze connection patterns and query performance",
                    "Consider burstable instance types for variable workloads",
                    "Test performance after downsizing"
                ]
            },
            {
                "category": "Reserved Instances",
                "description": "Purchase RDS Reserved Instances for steady-state workloads",
                "potential_savings": "30-60%",
                "implementation_effort": "Low",
                "best_practices": [
                    "Analyze usage patterns over 6-12 months",
                    "Start with 1-year terms for flexibility",
                    "Consider size-flexible RIs",
                    "Monitor RI utilization regularly"
                ]
            },
            {
                "category": "Storage Optimization",
                "description": "Optimize storage type and allocation",
                "potential_savings": "20-40%",
                "implementation_effort": "Low",
                "best_practices": [
                    "Use GP3 storage for better price/performance",
                    "Monitor storage utilization and right-size",
                    "Enable storage autoscaling where appropriate",
                    "Consider archiving old data"
                ]
            },
            {
                "category": "Automated Backups",
                "description": "Optimize backup retention and scheduling",
                "potential_savings": "10-30%",
                "implementation_effort": "Low",
                "best_practices": [
                    "Set appropriate backup retention periods",
                    "Use automated backup windows during low-usage periods",
                    "Consider cross-region backup only when necessary",
                    "Implement lifecycle policies for snapshots"
                ]
            }
        ]
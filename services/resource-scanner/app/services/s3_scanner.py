import logging
from typing import Dict, List, Any
from datetime import datetime

from app.services.aws_scanner import AWSResourceScanner

logger = logging.getLogger(__name__)

class S3Scanner(AWSResourceScanner):
    """Scanner for S3 buckets and storage optimization."""
    
    def scan_buckets(self, include_costs: bool = True) -> Dict[str, Any]:
        """Scan S3 buckets globally."""
        try:
            s3_client = self.get_client('s3', 'us-east-1')  # S3 is global
            
            # Get buckets
            response = s3_client.list_buckets()
            
            buckets = []
            total_cost = 0.0
            optimization_opportunities = []
            
            for bucket in response.get('Buckets', []):
                bucket_data = self._process_bucket(bucket, include_costs)
                buckets.append(bucket_data)
                
                if include_costs:
                    total_cost += bucket_data.get('estimated_monthly_cost', 0.0)
                
                # Check for optimization opportunities
                opportunities = self._analyze_bucket_optimization(bucket_data)
                optimization_opportunities.extend(opportunities)
            
            result = {
                "buckets": buckets,
                "total_buckets": len(buckets),
                "estimated_monthly_cost": round(total_cost, 2) if include_costs else None,
                "optimization_opportunities": optimization_opportunities,
                "scan_timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Scanned {len(buckets)} S3 buckets")
            return result
            
        except Exception as e:
            logger.error(f"Error scanning S3 buckets: {e}")
            raise
    
    def _process_bucket(self, bucket: Dict[str, Any], include_costs: bool = True) -> Dict[str, Any]:
        """Process individual S3 bucket data."""
        bucket_name = bucket.get('Name', 'unknown')
        creation_date = bucket.get('CreationDate', datetime.utcnow())
        
        # Mock bucket size and object count (in production, use CloudWatch metrics)
        import random
        size_gb = bucket.get('Size', random.randint(1, 1000))  # Size in bytes, convert to GB
        if isinstance(size_gb, int) and size_gb > 1024*1024*1024:
            size_gb = size_gb / (1024*1024*1024)  # Convert bytes to GB
        else:
            size_gb = random.uniform(0.1, 500)  # Random size for demo
            
        object_count = bucket.get('ObjectCount', random.randint(10, 100000))
        storage_class = bucket.get('StorageClass', 'STANDARD')
        
        # Calculate costs
        estimated_monthly_cost = 0.0
        if include_costs:
            # S3 pricing (simplified)
            if storage_class == 'STANDARD':
                cost_per_gb = 0.023  # $0.023 per GB/month
            elif storage_class == 'GLACIER':
                cost_per_gb = 0.004  # $0.004 per GB/month
            elif storage_class == 'DEEP_ARCHIVE':
                cost_per_gb = 0.00099  # $0.00099 per GB/month
            else:
                cost_per_gb = 0.023  # Default to STANDARD
                
            estimated_monthly_cost = size_gb * cost_per_gb
            
            # Add request costs (simplified)
            request_cost = object_count * 0.0004 / 1000  # $0.0004 per 1,000 requests
            estimated_monthly_cost += request_cost
        
        processed_bucket = {
            "bucket_name": bucket_name,
            "creation_date": creation_date.isoformat(),
            "size_gb": round(size_gb, 2),
            "object_count": object_count,
            "storage_class": storage_class,
            "estimated_monthly_cost": round(estimated_monthly_cost, 2) if include_costs else None
        }
        
        # Add mock lifecycle policy status
        processed_bucket['has_lifecycle_policy'] = random.choice([True, False])
        processed_bucket['versioning_enabled'] = random.choice([True, False])
        processed_bucket['encryption_enabled'] = random.choice([True, False])
        
        return processed_bucket
    
    def _analyze_bucket_optimization(self, bucket_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze bucket for optimization opportunities."""
        opportunities = []
        
        bucket_name = bucket_data['bucket_name']
        size_gb = bucket_data.get('size_gb', 0)
        storage_class = bucket_data.get('storage_class', 'STANDARD')
        
        # Check for lifecycle policy
        if not bucket_data.get('has_lifecycle_policy', False) and size_gb > 10:
            opportunities.append({
                "type": "lifecycle_optimization",
                "resource_id": bucket_name,
                "recommendation": "Implement lifecycle policies to automatically transition objects to cheaper storage classes.",
                "potential_savings": bucket_data.get('estimated_monthly_cost', 0) * 0.6,
                "priority": "high",
                "effort": "low"
            })
        
        # Check for large buckets in expensive storage
        if storage_class == 'STANDARD' and size_gb > 100:
            opportunities.append({
                "type": "storage_class_optimization",
                "resource_id": bucket_name,
                "recommendation": f"Large bucket ({size_gb:.1f} GB) in STANDARD storage. Consider transitioning infrequently accessed data to IA or Glacier.",
                "potential_savings": bucket_data.get('estimated_monthly_cost', 0) * 0.4,
                "priority": "medium",
                "effort": "medium"
            })
        
        # Check for unencrypted buckets
        if not bucket_data.get('encryption_enabled', False):
            opportunities.append({
                "type": "security_improvement",
                "resource_id": bucket_name,
                "recommendation": "Enable default encryption for better security compliance.",
                "potential_savings": 0,  # Security improvement
                "priority": "medium",
                "effort": "low",
                "category": "security"
            })
        
        # Check for versioning without lifecycle
        if bucket_data.get('versioning_enabled', False) and not bucket_data.get('has_lifecycle_policy', False):
            opportunities.append({
                "type": "versioning_optimization",
                "resource_id": bucket_name,
                "recommendation": "Versioning is enabled but no lifecycle policy found. Old versions may be accumulating costs.",
                "potential_savings": bucket_data.get('estimated_monthly_cost', 0) * 0.3,
                "priority": "medium",
                "effort": "low"
            })
        
        return opportunities
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get general S3 optimization recommendations."""
        return [
            {
                "category": "Storage Class Optimization",
                "description": "Use appropriate storage classes for different access patterns",
                "potential_savings": "40-80%",
                "implementation_effort": "Low",
                "best_practices": [
                    "Use S3 Intelligent-Tiering for unknown access patterns",
                    "Transition infrequently accessed data to IA after 30 days",
                    "Archive old data to Glacier or Deep Archive",
                    "Monitor access patterns with S3 Storage Lens"
                ]
            },
            {
                "category": "Lifecycle Policies",
                "description": "Automate data lifecycle management",
                "potential_savings": "50-90%",
                "implementation_effort": "Low",
                "best_practices": [
                    "Create policies based on business requirements",
                    "Start with conservative transition periods",
                    "Delete incomplete multipart uploads",
                    "Manage object versions automatically"
                ]
            },
            {
                "category": "Request Optimization",
                "description": "Optimize request patterns and costs",
                "potential_savings": "20-60%",
                "implementation_effort": "Medium",
                "best_practices": [
                    "Use CloudFront for frequently accessed content",
                    "Batch operations when possible",
                    "Use appropriate request types (GET vs LIST)",
                    "Implement caching strategies"
                ]
            },
            {
                "category": "Data Transfer Optimization",
                "description": "Minimize data transfer costs",
                "potential_savings": "30-70%",
                "implementation_effort": "Medium",
                "best_practices": [
                    "Use CloudFront for global content delivery",
                    "Keep data in the same region as compute resources",
                    "Use S3 Transfer Acceleration when needed",
                    "Compress data before uploading"
                ]
            }
        ]
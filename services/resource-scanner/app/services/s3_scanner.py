import boto3
import logging
from typing import Dict, List, Any
from datetime import datetime
import os

from .aws_scanner import AWSResourceScanner

logger = logging.getLogger(__name__)

class S3Scanner(AWSResourceScanner):
    """Scanner for S3 buckets and storage optimization."""
    
    def scan_buckets(self, include_costs: bool = True) -> Dict[str, Any]:
        """Scan S3 buckets globally."""
        try:
            s3_client = self.get_client('s3', 'us-east-1')  # S3 is global
            
            # Get real buckets from AWS
            response = s3_client.list_buckets()
            
            buckets = []
            total_cost = 0.0
            optimization_opportunities = []
            
            for bucket in response.get('Buckets', []):
                bucket_data = self._process_bucket(bucket, s3_client, include_costs)
                buckets.append(bucket_data)
                
                if include_costs:
                    total_cost += bucket_data.get('estimated_monthly_cost', 0.0)
                
                # Check for optimization opportunities
                opportunities = self._analyze_bucket_optimization(bucket_data)
                optimization_opportunities.extend(opportunities)
            
            result = {
                "resources": buckets,  # Changed from "buckets" to match your Flask app
                "total_buckets": len(buckets),
                "estimated_monthly_cost": round(total_cost, 2) if include_costs else None,
                "optimization_opportunities": optimization_opportunities,
                "scan_timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Scanned {len(buckets)} S3 buckets")
            return result
            
        except Exception as e:
            logger.error(f"Error scanning S3 buckets: {e}")
            # Return error structure that matches your Flask app expectations
            return {
                "resources": [],
                "total_buckets": 0,
                "estimated_monthly_cost": 0.0,
                "optimization_opportunities": [],
                "error": str(e)
            }
    
    def _process_bucket(self, bucket: Dict[str, Any], s3_client, include_costs: bool = True) -> Dict[str, Any]:
        """Process individual S3 bucket data with real AWS data."""
        bucket_name = bucket.get('Name', 'unknown')
        creation_date = bucket.get('CreationDate', datetime.utcnow())
        
        # Get real bucket information
        try:
            # Get bucket location
            location_response = s3_client.get_bucket_location(Bucket=bucket_name)
            region = location_response.get('LocationConstraint') or 'us-east-1'
            
            # Get bucket versioning status
            try:
                versioning_response = s3_client.get_bucket_versioning(Bucket=bucket_name)
                versioning_enabled = versioning_response.get('Status') == 'Enabled'
            except:
                versioning_enabled = False
            
            # Get bucket encryption status
            try:
                s3_client.get_bucket_encryption(Bucket=bucket_name)
                encryption_enabled = True
            except:
                encryption_enabled = False
            
            # Get lifecycle policy status
            try:
                s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
                has_lifecycle_policy = True
            except:
                has_lifecycle_policy = False
            
            # For now, use estimated size and object count (getting real metrics requires CloudWatch)
            # In production, you'd use CloudWatch metrics or S3 Inventory
            size_gb = 5.5  # Default estimate
            object_count = 100  # Default estimate
            
        except Exception as e:
            logger.warning(f"Could not get detailed info for bucket {bucket_name}: {e}")
            region = 'us-east-1'
            versioning_enabled = False
            encryption_enabled = False
            has_lifecycle_policy = False
            size_gb = 1.0
            object_count = 10
        
        # Calculate estimated costs
        estimated_monthly_cost = 0.0
        if include_costs:
            # S3 Standard storage pricing (simplified)
            cost_per_gb = 0.023  # $0.023 per GB/month for Standard
            estimated_monthly_cost = size_gb * cost_per_gb
            
            # Add request costs (simplified)
            request_cost = object_count * 0.0004 / 1000  # $0.0004 per 1,000 requests
            estimated_monthly_cost += request_cost
        
        processed_bucket = {
            "bucket_name": bucket_name,
            "creation_date": creation_date.isoformat(),
            "region": region,
            "size_gb": round(size_gb, 2),
            "object_count": object_count,
            "storage_class": "STANDARD",  # Default, would need CloudWatch for real data
            "estimated_monthly_cost": round(estimated_monthly_cost, 2) if include_costs else None,
            "has_lifecycle_policy": has_lifecycle_policy,
            "versioning_enabled": versioning_enabled,
            "encryption_enabled": encryption_enabled
        }
        
        return processed_bucket
    
    def _analyze_bucket_optimization(self, bucket_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze bucket for optimization opportunities."""
        opportunities = []
        
        bucket_name = bucket_data['bucket_name']
        size_gb = bucket_data.get('size_gb', 0)
        
        # Check for lifecycle policy
        if not bucket_data.get('has_lifecycle_policy', False) and size_gb > 1:
            opportunities.append({
                "type": "lifecycle_optimization",
                "resource_id": bucket_name,
                "recommendation": "Implement lifecycle policies to automatically transition objects to cheaper storage classes.",
                "potential_savings": bucket_data.get('estimated_monthly_cost', 0) * 0.6,
                "priority": "high",
                "effort": "low"
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
                    "Archive old data to Glacier or Deep Archive"
                ]
            }
        ]
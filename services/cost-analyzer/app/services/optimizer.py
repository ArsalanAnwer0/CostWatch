import logging
from typing import List, Dict, Optional
from decimal import Decimal
from datetime import datetime  # ADD THIS IMPORT
import boto3

from ..models.cost_analysis import OptimizationRecommendation
from ..models.resource import Resource, EC2Resource, RDSResource
from ..utils.database import get_db_connection

logger = logging.getLogger(__name__)

class ResourceOptimizer:
    """Optimize cloud resources for cost efficiency"""
    
    def __init__(self):
        self.ec2_client = boto3.client('ec2')
        self.rds_client = boto3.client('rds')
        self.cloudwatch = boto3.client('cloudwatch')
    
    async def get_recommendations(self, account_id: str, resource_types: List[str]) -> List[OptimizationRecommendation]:
        """Get optimization recommendations for specified resource types"""
        recommendations = []
        
        try:
            for resource_type in resource_types:
                if resource_type == "ec2":
                    ec2_recommendations = await self._optimize_ec2_instances(account_id)
                    recommendations.extend(ec2_recommendations)
                
                elif resource_type == "rds":
                    rds_recommendations = await self._optimize_rds_instances(account_id)
                    recommendations.extend(rds_recommendations)
                
                elif resource_type == "ebs":
                    ebs_recommendations = await self._optimize_ebs_volumes(account_id)
                    recommendations.extend(ebs_recommendations)
                
                elif resource_type == "s3":
                    s3_recommendations = await self._optimize_s3_buckets(account_id)
                    recommendations.extend(s3_recommendations)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Optimization recommendations failed: {e}")
            raise
    
    async def _optimize_ec2_instances(self, account_id: str) -> List[OptimizationRecommendation]:
        """Optimize EC2 instances"""
        recommendations = []
        
        try:
            # Get EC2 instances (placeholder - would integrate with actual data)
            instances = await self._get_ec2_instances(account_id)
            
            for instance in instances:
                # Check if instance is underutilized
                if instance.cpu_utilization < 10:  # Less than 10% CPU
                    recommendations.append(OptimizationRecommendation(
                        resource_id=instance.resource_id,
                        resource_type="ec2",
                        current_cost=instance.current_cost,
                        recommended_action="Stop or downsize instance",
                        monthly_savings=instance.current_cost * Decimal('0.8'),
                        confidence_score=0.9,
                        description=f"Instance {instance.resource_id} has low CPU utilization ({instance.cpu_utilization}%)",
                        implementation_effort="low",
                        risk_level="low"
                    ))
                
                elif instance.cpu_utilization < 30:  # 10-30% CPU
                    recommendations.append(OptimizationRecommendation(
                        resource_id=instance.resource_id,
                        resource_type="ec2",
                        current_cost=instance.current_cost,
                        recommended_action="Downsize to smaller instance type",
                        monthly_savings=instance.current_cost * Decimal('0.4'),
                        confidence_score=0.7,
                        description=f"Instance {instance.resource_id} could be downsized",
                        implementation_effort="medium",
                        risk_level="medium"
                    ))
            
            return recommendations
            
        except Exception as e:
            logger.error(f"EC2 optimization failed: {e}")
            raise
    
    async def _optimize_rds_instances(self, account_id: str) -> List[OptimizationRecommendation]:
        """Optimize RDS instances"""
        recommendations = []
        
        try:
            # Placeholder recommendations for RDS
            recommendations.append(OptimizationRecommendation(
                resource_id="db-instance-1",
                resource_type="rds",
                current_cost=Decimal('120.00'),
                recommended_action="Enable automated backups optimization",
                monthly_savings=Decimal('15.00'),
                confidence_score=0.8,
                description="Optimize backup retention and storage",
                implementation_effort="low",
                risk_level="low"
            ))
            
            return recommendations
            
        except Exception as e:
            logger.error(f"RDS optimization failed: {e}")
            raise
    
    async def _optimize_ebs_volumes(self, account_id: str) -> List[OptimizationRecommendation]:
        """Optimize EBS volumes"""
        recommendations = []
        
        try:
            # Placeholder recommendations for EBS
            recommendations.append(OptimizationRecommendation(
                resource_id="vol-unattached-1",
                resource_type="ebs",
                current_cost=Decimal('25.00'),
                recommended_action="Delete unattached volume",
                monthly_savings=Decimal('25.00'),
                confidence_score=0.95,
                description="Volume is unattached and can be safely deleted",
                implementation_effort="low",
                risk_level="low"
            ))
            
            return recommendations
            
        except Exception as e:
            logger.error(f"EBS optimization failed: {e}")
            raise
    
    async def _optimize_s3_buckets(self, account_id: str) -> List[OptimizationRecommendation]:
        """Optimize S3 storage"""
        recommendations = []
        
        try:
            # Placeholder recommendations for S3
            recommendations.append(OptimizationRecommendation(
                resource_id="bucket-old-data",
                resource_type="s3",
                current_cost=Decimal('50.00'),
                recommended_action="Configure lifecycle policies",
                monthly_savings=Decimal('30.00'),
                confidence_score=0.85,
                description="Move old data to cheaper storage classes",
                implementation_effort="medium",
                risk_level="low"
            ))
            
            return recommendations
            
        except Exception as e:
            logger.error(f"S3 optimization failed: {e}")
            raise
    
    async def _get_ec2_instances(self, account_id: str) -> List[EC2Resource]:
        """Get EC2 instances for account (placeholder)"""
        # This would integrate with actual resource scanner data
        return [
            EC2Resource(
                resource_id="i-1234567890abcdef0",
                resource_type="ec2",
                account_id=account_id,
                region="us-west-2",
                service="EC2",
                current_cost=Decimal('75.50'),
                utilization_metrics={"cpu": 5.2, "memory": 15.3},
                tags={"Environment": "dev", "Project": "test"},
                last_updated=datetime.utcnow(),
                status="running",
                instance_type="t3.medium",
                cpu_utilization=5.2
            )
        ]

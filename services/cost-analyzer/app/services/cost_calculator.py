import boto3
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
import json

from ..models.cost_analysis import CostAnalysis, CostForecast
from ..models.resource import Resource
from ..utils.database import get_db_connection

logger = logging.getLogger(__name__)

class CostCalculator:
    """Calculate and analyze AWS costs"""
    
    def __init__(self):
        self.ce_client = boto3.client('ce')  # Cost Explorer
        self.pricing_client = boto3.client('pricing', region_name='us-east-1')
    
    async def calculate_costs(self, account_id: str, start_date: str, end_date: str) -> CostAnalysis:
        """Calculate comprehensive cost analysis"""
        try:
            # Get cost data from AWS Cost Explorer
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity='DAILY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                    {'Type': 'DIMENSION', 'Key': 'REGION'}
                ]
            )
            
            # Process cost data
            total_cost = Decimal('0')
            service_breakdown = {}
            region_breakdown = {}
            daily_costs = []
            
            for result in response['ResultsByTime']:
                daily_cost = Decimal(result['Total']['BlendedCost']['Amount'])
                daily_costs.append(daily_cost)
                total_cost += daily_cost
                
                # Process groups for breakdown
                for group in result['Groups']:
                    service = group['Keys'][0]
                    region = group['Keys'][1]
                    cost = Decimal(group['Metrics']['BlendedCost']['Amount'])
                    
                    service_breakdown[service] = service_breakdown.get(service, Decimal('0')) + cost
                    region_breakdown[region] = region_breakdown.get(region, Decimal('0')) + cost
            
            # Calculate daily average
            days = len(daily_costs)
            daily_average = total_cost / days if days > 0 else Decimal('0')
            
            # Determine cost trend
            cost_trend = self._analyze_cost_trend(daily_costs)
            
            return CostAnalysis(
                account_id=account_id,
                total_cost=total_cost,
                daily_average=daily_average,
                service_breakdown=service_breakdown,
                region_breakdown=region_breakdown,
                cost_trend=cost_trend,
                period_start=datetime.fromisoformat(start_date),
                period_end=datetime.fromisoformat(end_date)
            )
            
        except Exception as e:
            logger.error(f"Cost calculation failed: {e}")
            raise
    
    async def calculate_savings_opportunities(self, account_id: str) -> Dict:
        """Calculate potential savings opportunities"""
        try:
            savings_summary = {
                "total_potential_savings": Decimal('0'),
                "opportunities": []
            }
            
            # Get unused EC2 instances
            unused_ec2_savings = await self._calculate_unused_ec2_savings(account_id)
            savings_summary["opportunities"].append({
                "category": "Unused EC2 Instances",
                "potential_savings": unused_ec2_savings,
                "description": "Stop or terminate unused EC2 instances"
            })
            
            # Get unattached EBS volumes
            unattached_ebs_savings = await self._calculate_unattached_ebs_savings(account_id)
            savings_summary["opportunities"].append({
                "category": "Unattached EBS Volumes",
                "potential_savings": unattached_ebs_savings,
                "description": "Delete unattached EBS volumes"
            })
            
            # Get underutilized RDS instances
            underutilized_rds_savings = await self._calculate_underutilized_rds_savings(account_id)
            savings_summary["opportunities"].append({
                "category": "Underutilized RDS",
                "potential_savings": underutilized_rds_savings,
                "description": "Right-size underutilized RDS instances"
            })
            
            # Calculate total
            savings_summary["total_potential_savings"] = sum(
                opp["potential_savings"] for opp in savings_summary["opportunities"]
            )
            
            return savings_summary
            
        except Exception as e:
            logger.error(f"Savings calculation failed: {e}")
            raise
    
    async def generate_monthly_report(self, account_id: str, month: str) -> Dict:
        """Generate comprehensive monthly cost report"""
        try:
            # Parse month (YYYY-MM)
            year, month_num = month.split('-')
            start_date = f"{year}-{month_num}-01"
            
            # Calculate end date
            if month_num == "12":
                end_date = f"{int(year)+1}-01-01"
            else:
                end_date = f"{year}-{int(month_num)+1:02d}-01"
            
            # Get cost analysis
            cost_analysis = await self.calculate_costs(account_id, start_date, end_date)
            
            # Get savings opportunities
            savings = await self.calculate_savings_opportunities(account_id)
            
            report = {
                "account_id": account_id,
                "report_month": month,
                "cost_analysis": cost_analysis.dict(),
                "savings_opportunities": savings,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Monthly report generation failed: {e}")
            raise
    
    def _analyze_cost_trend(self, daily_costs: List[Decimal]) -> str:
        """Analyze cost trend from daily cost data"""
        if len(daily_costs) < 2:
            return "stable"
        
        # Calculate trend using simple linear regression
        n = len(daily_costs)
        x_sum = sum(range(n))
        y_sum = sum(daily_costs)
        xy_sum = sum(i * cost for i, cost in enumerate(daily_costs))
        x2_sum = sum(i * i for i in range(n))
        
        # Calculate slope
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        
        # Determine trend
        if slope > Decimal('0.05'):  # Threshold for increasing
            return "increasing"
        elif slope < Decimal('-0.05'):  # Threshold for decreasing
            return "decreasing"
        else:
            return "stable"
    
    async def _calculate_unused_ec2_savings(self, account_id: str) -> Decimal:
        """Calculate savings from unused EC2 instances"""
        # Placeholder implementation - would integrate with actual AWS data
        return Decimal('150.00')  # Monthly savings estimate
    
    async def _calculate_unattached_ebs_savings(self, account_id: str) -> Decimal:
        """Calculate savings from unattached EBS volumes"""
        # Placeholder implementation
        return Decimal('75.00')  # Monthly savings estimate
    
    async def _calculate_underutilized_rds_savings(self, account_id: str) -> Decimal:
        """Calculate savings from underutilized RDS instances"""
        # Placeholder implementation
        return Decimal('200.00')  # Monthly savings estimate
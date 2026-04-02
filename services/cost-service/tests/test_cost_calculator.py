import pytest
import asyncio
from unittest.mock import patch, MagicMock
from decimal import Decimal
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.cost_calculator import CostCalculator

@pytest.fixture
def cost_calculator():
    return CostCalculator()

@patch('boto3.client')
@pytest.mark.asyncio
async def test_calculate_costs(mock_boto3, cost_calculator):
    """Test cost calculation"""
    # Mock AWS Cost Explorer response
    mock_ce = MagicMock()
    mock_boto3.return_value = mock_ce
    
    mock_ce.get_cost_and_usage.return_value = {
        'ResultsByTime': [
            {
                'Total': {'BlendedCost': {'Amount': '100.50'}},
                'Groups': [
                    {
                        'Keys': ['EC2', 'us-west-2'],
                        'Metrics': {'BlendedCost': {'Amount': '75.25'}}
                    },
                    {
                        'Keys': ['RDS', 'us-west-2'],
                        'Metrics': {'BlendedCost': {'Amount': '25.25'}}
                    }
                ]
            }
        ]
    }
    
    # Test calculation
    result = await cost_calculator.calculate_costs("123456789", "2024-01-01", "2024-01-31")
    
    assert result.account_id == "123456789"
    assert result.total_cost == Decimal('100.50')

@pytest.mark.asyncio
async def test_calculate_savings_opportunities(cost_calculator):
    """Test savings opportunities calculation"""
    with patch.object(cost_calculator, '_calculate_unused_ec2_savings', return_value=Decimal('100.00')):
        with patch.object(cost_calculator, '_calculate_unattached_ebs_savings', return_value=Decimal('50.00')):
            with patch.object(cost_calculator, '_calculate_underutilized_rds_savings', return_value=Decimal('75.00')):
                
                result = await cost_calculator.calculate_savings_opportunities("123456789")
                
                assert result["total_potential_savings"] == Decimal('225.00')
                assert len(result["opportunities"]) == 3

def test_analyze_cost_trend(cost_calculator):
    """Test cost trend analysis"""
    # Test increasing trend
    increasing_costs = [Decimal(str(100 + i * 5)) for i in range(10)]
    trend = cost_calculator._analyze_cost_trend(increasing_costs)
    assert trend == "increasing"
    
    # Test stable trend
    stable_costs = [Decimal('100.0')] * 10
    trend = cost_calculator._analyze_cost_trend(stable_costs)
    assert trend == "stable"
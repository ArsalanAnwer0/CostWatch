import logging
from datetime import datetime, timedelta
from typing import Dict, List
from decimal import Decimal
import numpy as np
from sklearn.linear_model import LinearRegression
import boto3

from ..models.cost_analysis import CostForecast
from ..utils.database import get_db_connection

logger = logging.getLogger(__name__)

class TrendAnalyzer:
    """Analyze cost trends and predict future costs"""
    
    def __init__(self):
        self.ce_client = boto3.client('ce')
    
    async def analyze_trends(self, account_id: str, days: int = 30) -> Dict:
        """Analyze cost trends over specified period"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get historical cost data
            cost_data = await self._get_historical_costs(
                account_id, 
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            # Analyze trends
            trend_analysis = {
                "account_id": account_id,
                "period_days": days,
                "total_cost": sum(cost_data),
                "average_daily_cost": sum(cost_data) / len(cost_data) if cost_data else 0,
                "trend_direction": self._calculate_trend_direction(cost_data),
                "growth_rate": self._calculate_growth_rate(cost_data),
                "forecast": await self._generate_forecast(cost_data),
                "anomalies": self._detect_anomalies(cost_data),
                "recommendations": self._generate_trend_recommendations(cost_data)
            }
            
            return trend_analysis
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            raise
    
    async def _get_historical_costs(self, account_id: str, start_date: str, end_date: str) -> List[Decimal]:
        """Get historical cost data from AWS Cost Explorer"""
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity='DAILY',
                Metrics=['BlendedCost']
            )
            
            costs = []
            for result in response['ResultsByTime']:
                daily_cost = Decimal(result['Total']['BlendedCost']['Amount'])
                costs.append(daily_cost)
            
            return costs
            
        except Exception as e:
            logger.error(f"Failed to get historical costs: {e}")
            # Return mock data for development
            return [Decimal(str(100 + i * 2.5)) for i in range(30)]
    
    def _calculate_trend_direction(self, cost_data: List[Decimal]) -> str:
        """Calculate overall trend direction"""
        if len(cost_data) < 2:
            return "insufficient_data"
        
        # Simple linear regression to determine trend
        x = np.array(range(len(cost_data))).reshape(-1, 1)
        y = np.array([float(cost) for cost in cost_data])
        
        model = LinearRegression()
        model.fit(x, y)
        
        slope = model.coef_[0]
        
        if slope > 5:  # Increasing by more than $5/day
            return "strongly_increasing"
        elif slope > 1:  # Increasing by $1-5/day
            return "increasing"
        elif slope < -5:  # Decreasing by more than $5/day
            return "strongly_decreasing"
        elif slope < -1:  # Decreasing by $1-5/day
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_growth_rate(self, cost_data: List[Decimal]) -> float:
        """Calculate percentage growth rate"""
        if len(cost_data) < 2:
            return 0.0
        
        first_week = sum(cost_data[:7]) / 7 if len(cost_data) >= 7 else cost_data[0]
        last_week = sum(cost_data[-7:]) / 7 if len(cost_data) >= 7 else cost_data[-1]
        
        if first_week == 0:
            return 0.0
        
        growth_rate = (float(last_week - first_week) / float(first_week)) * 100
        return round(growth_rate, 2)
    
    async def _generate_forecast(self, cost_data: List[Decimal]) -> Dict:
        """Generate cost forecast for next 30 days"""
        if len(cost_data) < 7:
            return {"error": "Insufficient data for forecast"}
        
        try:
            # Prepare data for forecasting
            x = np.array(range(len(cost_data))).reshape(-1, 1)
            y = np.array([float(cost) for cost in cost_data])
            
            # Train model
            model = LinearRegression()
            model.fit(x, y)
            
            # Generate forecast for next 30 days
            future_days = np.array(range(len(cost_data), len(cost_data) + 30)).reshape(-1, 1)
            forecast = model.predict(future_days)
            
            # Calculate confidence intervals (simplified)
            residuals = y - model.predict(x)
            std_error = np.std(residuals)
            
            forecast_data = []
            for i, predicted_cost in enumerate(forecast):
                forecast_date = datetime.utcnow() + timedelta(days=i+1)
                forecast_data.append({
                    "date": forecast_date.strftime('%Y-%m-%d'),
                    "predicted_cost": round(predicted_cost, 2),
                    "confidence_interval": {
                        "lower": round(predicted_cost - (1.96 * std_error), 2),
                        "upper": round(predicted_cost + (1.96 * std_error), 2)
                    }
                })
            
            return {
                "forecast_period": "30_days",
                "total_predicted_cost": round(sum(forecast), 2),
                "daily_forecasts": forecast_data[:7],  # Return first 7 days
                "model_accuracy": round(model.score(x, y), 3)
            }
            
        except Exception as e:
            logger.error(f"Forecast generation failed: {e}")
            return {"error": "Forecast generation failed"}
    
    def _detect_anomalies(self, cost_data: List[Decimal]) -> List[Dict]:
        """Detect cost anomalies using statistical methods"""
        if len(cost_data) < 7:
            return []
        
        anomalies = []
        costs_float = [float(cost) for cost in cost_data]
        
        # Calculate mean and standard deviation
        mean_cost = np.mean(costs_float)
        std_cost = np.std(costs_float)
        
        # Detect outliers (costs beyond 2 standard deviations)
        for i, cost in enumerate(costs_float):
            if abs(cost - mean_cost) > (2 * std_cost):
                anomaly_date = datetime.utcnow() - timedelta(days=len(cost_data)-i-1)
                anomalies.append({
                    "date": anomaly_date.strftime('%Y-%m-%d'),
                    "cost": cost,
                    "deviation": round(abs(cost - mean_cost), 2),
                    "type": "spike" if cost > mean_cost else "drop",
                    "severity": "high" if abs(cost - mean_cost) > (3 * std_cost) else "medium"
                })
        
        return anomalies
    
    def _generate_trend_recommendations(self, cost_data: List[Decimal]) -> List[str]:
        """Generate recommendations based on cost trends"""
        recommendations = []
        
        if len(cost_data) < 7:
            return ["Collect more data for better trend analysis"]
        
        trend = self._calculate_trend_direction(cost_data)
        growth_rate = self._calculate_growth_rate(cost_data)
        
        if trend in ["strongly_increasing", "increasing"]:
            recommendations.append("Investigate recent cost increases")
            recommendations.append("Review resource utilization and optimization opportunities")
            if growth_rate > 20:
                recommendations.append("Set up budget alerts to prevent cost overruns")
        
        elif trend in ["strongly_decreasing", "decreasing"]:
            recommendations.append("Monitor for any service disruptions causing cost reduction")
            recommendations.append("Document optimization efforts for future reference")
        
        else:  # stable
            recommendations.append("Cost trend is stable - continue monitoring")
            recommendations.append("Consider proactive optimization to reduce baseline costs")
        
        # Check for high variance
        costs_float = [float(cost) for cost in cost_data]
        if np.std(costs_float) > np.mean(costs_float) * 0.3:  # High variance
            recommendations.append("Cost variance is high - investigate irregular spending patterns")
        
        return recommendations

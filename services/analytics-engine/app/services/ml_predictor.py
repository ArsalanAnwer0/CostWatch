import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import uuid

from ..models.analytics import PredictionRequest, Prediction, Anomaly

logger = logging.getLogger(__name__)

class MLPredictor:
    """Machine learning service for predictions and anomaly detection"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.anomaly_detectors = {}
    
    def predict(self, request: PredictionRequest) -> Dict[str, Any]:
        """Generate ML-based predictions"""
        try:
            if request.prediction_type == 'cost_forecast':
                return self._predict_cost_forecast(request)
            elif request.prediction_type == 'capacity_planning':
                return self._predict_capacity_needs(request)
            elif request.prediction_type == 'budget_projection':
                return self._predict_budget_projection(request)
            else:
                raise ValueError(f"Unsupported prediction type: {request.prediction_type}")
                
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise
    
    def detect_anomalies(self, account_id: str, days: int, sensitivity: str) -> List[Dict[str, Any]]:
        """Detect cost anomalies using ML algorithms"""
        try:
            # Get historical data
            historical_data = self._get_cost_data(account_id, days)
            
            # Prepare features
            features = self._prepare_anomaly_features(historical_data)
            
            # Configure anomaly detector
            contamination = self._get_contamination_rate(sensitivity)
            detector = IsolationForest(contamination=contamination, random_state=42)
            
            # Detect anomalies
            anomaly_scores = detector.fit_predict(features)
            anomaly_indices = np.where(anomaly_scores == -1)[0]
            
            # Generate anomaly reports
            anomalies = []
            for idx in anomaly_indices:
                anomaly = self._create_anomaly_report(historical_data.iloc[idx], account_id, features[idx])
                anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            raise
    
    def _predict_cost_forecast(self, request: PredictionRequest) -> Dict[str, Any]:
        """Predict future costs using time series forecasting"""
        try:
            # Prepare historical data
            historical_data = pd.DataFrame(request.historical_data.get('daily_costs', []))
            if historical_data.empty:
                # Generate sample data for demonstration
                dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
                costs = np.random.normal(1000, 200, 30) + np.arange(30) * 10  # Trending upward
                historical_data = pd.DataFrame({'date': dates, 'cost': costs})
            
            # Prepare features for time series
            historical_data['days_since_start'] = range(len(historical_data))
            X = historical_data[['days_since_start']].values
            y = historical_data['cost'].values
            
            # Train linear regression model
            model = LinearRegression()
            model.fit(X, y)
            
            # Generate predictions
            future_days = np.arange(len(historical_data), len(historical_data) + request.time_horizon).reshape(-1, 1)
            predictions = model.predict(future_days)
            
            # Calculate confidence intervals (simplified)
            residuals = y - model.predict(X)
            std_error = np.std(residuals)
            
            # Format predictions
            prediction_data = []
            for i, pred in enumerate(predictions):
                date = datetime.now() + timedelta(days=i+1)
                prediction_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'predicted_cost': round(pred, 2),
                    'confidence_interval': {
                        'lower': round(pred - 1.96 * std_error, 2),
                        'upper': round(pred + 1.96 * std_error, 2)
                    }
                })
            
            return {
                'prediction_id': str(uuid.uuid4()),
                'model_type': 'linear_regression',
                'predictions': prediction_data,
                'total_predicted_cost': round(sum(predictions), 2),
                'model_accuracy': round(model.score(X, y), 3),
                'trend_direction': 'increasing' if model.coef_[0] > 0 else 'decreasing'
            }
            
        except Exception as e:
            logger.error(f"Cost forecast prediction failed: {e}")
            raise
    
    def _predict_capacity_needs(self, request: PredictionRequest) -> Dict[str, Any]:
        """Predict future capacity requirements"""
        try:
            # Simplified capacity prediction
            current_usage = request.historical_data.get('current_usage', {})
            growth_rate = request.historical_data.get('growth_rate', 0.15)  # 15% monthly growth
            
            predictions = []
            for month in range(1, 13):  # 12 months
                for resource_type, current_value in current_usage.items():
                    predicted_value = current_value * (1 + growth_rate) ** month
                    predictions.append({
                        'month': month,
                        'resource_type': resource_type,
                        'predicted_usage': round(predicted_value, 2),
                        'recommended_capacity': round(predicted_value * 1.2, 2)  # 20% buffer
                    })
            
            return {
                'prediction_id': str(uuid.uuid4()),
                'model_type': 'exponential_growth',
                'capacity_predictions': predictions,
                'recommendations': [
                    'Plan for 20% capacity buffer above predicted usage',
                    'Review capacity quarterly to adjust for actual growth',
                    'Consider auto-scaling for variable workloads'
                ]
            }
            
        except Exception as e:
            logger.error(f"Capacity prediction failed: {e}")
            raise
    
    def _predict_budget_projection(self, request: PredictionRequest) -> Dict[str, Any]:
        """Predict budget requirements and variances"""
        try:
            current_budget = request.historical_data.get('current_budget', 10000)
            historical_variance = request.historical_data.get('variance_history', [])
            
            # Calculate variance statistics
            if not historical_variance:
                historical_variance = np.random.normal(0, 0.1, 12)  # Sample data
            
            mean_variance = np.mean(historical_variance)
            std_variance = np.std(historical_variance)
            
            # Project future budget needs
            projections = []
            for month in range(1, 13):
                base_budget = current_budget * (1.05 ** month)  # 5% annual growth
                expected_variance = np.random.normal(mean_variance, std_variance)
                projected_actual = base_budget * (1 + expected_variance)
                
                projections.append({
                    'month': month,
                    'budget_recommendation': round(base_budget, 2),
                    'projected_actual': round(projected_actual, 2),
                    'variance_probability': abs(expected_variance),
                    'confidence_level': 'high' if abs(expected_variance) < 0.1 else 'medium'
                })
            
            return {
                'prediction_id': str(uuid.uuid4()),
                'model_type': 'budget_variance',
                'budget_projections': projections,
                'summary': {
                    'annual_budget_recommendation': round(sum(p['budget_recommendation'] for p in projections), 2),
                    'expected_variance_range': f"{mean_variance-std_variance:.1%} to {mean_variance+std_variance:.1%}",
                    'risk_level': 'low' if std_variance < 0.05 else 'medium'
                }
            }
            
        except Exception as e:
            logger.error(f"Budget projection failed: {e}")
            raise
    
    def _get_cost_data(self, account_id: str, days: int) -> pd.DataFrame:
        """Get historical cost data for anomaly detection"""
        try:
            # Generate sample data for demonstration
            dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
            
            # Create normal cost pattern with some anomalies
            base_costs = np.random.normal(1000, 100, days)
            
            # Add some artificial anomalies
            anomaly_days = np.random.choice(days, size=max(1, days//10), replace=False)
            for day in anomaly_days:
                base_costs[day] *= np.random.choice([0.3, 2.5])  # Either much lower or much higher
            
            data = pd.DataFrame({
                'date': dates,
                'total_cost': base_costs,
                'service_costs': np.random.normal(500, 50, days),
                'cpu_utilization': np.random.normal(60, 15, days),
                'memory_utilization': np.random.normal(70, 20, days)
            })
            
            return data
            
        except Exception as e:
            logger.error(f"Cost data retrieval failed: {e}")
            raise
    
    def _prepare_anomaly_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features for anomaly detection"""
        try:
            # Select numeric columns for anomaly detection
            feature_columns = ['total_cost', 'service_costs', 'cpu_utilization', 'memory_utilization']
            features = data[feature_columns].values
            
            # Normalize features
            scaler = StandardScaler()
            normalized_features = scaler.fit_transform(features)
            
            return normalized_features
            
        except Exception as e:
            logger.error(f"Feature preparation failed: {e}")
            raise
    
    def _get_contamination_rate(self, sensitivity: str) -> float:
        """Get contamination rate based on sensitivity setting"""
        sensitivity_map = {
            'low': 0.05,    # 5% of data considered anomalies
            'medium': 0.1,  # 10% of data considered anomalies
            'high': 0.15    # 15% of data considered anomalies
        }
        return sensitivity_map.get(sensitivity, 0.1)
    
    def _create_anomaly_report(self, data_point: pd.Series, account_id: str, features: np.ndarray) -> Dict[str, Any]:
        """Create detailed anomaly report"""
        try:
            # Determine anomaly type based on which feature is most extreme
            feature_names = ['total_cost', 'service_costs', 'cpu_utilization', 'memory_utilization']
            anomaly_scores = np.abs(features)
            most_anomalous_feature = feature_names[np.argmax(anomaly_scores)]
            
            # Determine severity
            max_score = np.max(anomaly_scores)
            if max_score > 3:
                severity = 'critical'
            elif max_score > 2:
                severity = 'high'
            else:
                severity = 'medium'
            
            return {
                'anomaly_id': str(uuid.uuid4()),
                'account_id': account_id,
                'date': data_point['date'].strftime('%Y-%m-%d'),
                'anomaly_type': most_anomalous_feature,
                'severity': severity,
                'description': f"Unusual {most_anomalous_feature.replace('_', ' ')} detected",
                'actual_value': float(data_point[most_anomalous_feature]),
                'anomaly_score': float(max_score),
                'affected_metrics': [most_anomalous_feature],
                'recommended_actions': self._get_anomaly_recommendations(most_anomalous_feature, severity)
            }
            
        except Exception as e:
            logger.error(f"Anomaly report creation failed: {e}")
            return {}
    
    def _get_anomaly_recommendations(self, anomaly_type: str, severity: str) -> List[str]:
        """Get recommendations based on anomaly type and severity"""
        base_recommendations = {
            'total_cost': [
                'Review recent resource provisioning changes',
                'Check for unscheduled workloads',
                'Verify cost allocation tags'
            ],
            'service_costs': [
                'Investigate specific service usage spikes',
                'Review service configuration changes',
                'Check for data transfer anomalies'
            ],
            'cpu_utilization': [
                'Investigate workload changes',
                'Check for resource contention',
                'Review auto-scaling policies'
            ],
            'memory_utilization': [
                'Check for memory leaks',
                'Review application performance',
                'Investigate memory-intensive processes'
            ]
        }
        
        recommendations = base_recommendations.get(anomaly_type, ['Investigate the anomaly further'])
        
        if severity == 'critical':
            recommendations.insert(0, 'Immediate investigation required')
            recommendations.append('Consider emergency response procedures')
        
        return recommendations
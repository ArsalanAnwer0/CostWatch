import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import uuid

from models.analytics import PredictionRequest, Prediction, Anomaly

logger = logging.getLogger(__name__)

class MLPredictor:
    """Machine learning service for predictions and anomaly detection"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.prediction_cache = {}
    
    def predict(self, request: PredictionRequest) -> Dict[str, Any]:
        """Generate ML-based predictions using historical data"""
        try:
            logger.info(f"Generating predictions for account {request.account_id}")
            
            # Extract cost data from historical_data
            if request.historical_data and request.historical_data.get('analysis'):
                analysis = request.historical_data['analysis']
                daily_costs = analysis.get('daily_costs', [])
                cost_values = [day['cost'] for day in daily_costs]
            else:
                # Use fallback data
                cost_values = [0.0] * 30
            
            if request.prediction_type == 'cost_forecast':
                return self._generate_cost_forecast(cost_values, request.time_horizon, request.account_id)
            elif request.prediction_type == 'trend_prediction':
                return self._generate_trend_prediction(cost_values, request.time_horizon)
            elif request.prediction_type == 'anomaly_forecast':
                return self._generate_anomaly_forecast(cost_values, request.time_horizon)
            else:
                return self._generate_cost_forecast(cost_values, request.time_horizon, request.account_id)
                
        except Exception as e:
            logger.error(f"Prediction generation failed: {e}")
            return self._generate_fallback_prediction(request)
    
    def detect_anomalies(self, account_id: str, cost_data: Optional[Dict[str, Any]], sensitivity: str = 'medium') -> List[Dict[str, Any]]:
        """Detect cost anomalies using ML algorithms on real AWS data"""
        try:
            logger.info(f"Detecting anomalies for account {account_id}")
            
            # Extract cost values from the cost_data
            if cost_data and cost_data.get('analysis'):
                analysis = cost_data['analysis']
                daily_costs = analysis.get('daily_costs', [])
                cost_values = [day['cost'] for day in daily_costs]
                dates = [day['date'] for day in daily_costs]
            else:
                # Fallback data
                cost_values = [0.0] * 30
                dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(29, -1, -1)]
            
            if len(cost_values) < 7:
                return [{
                    'type': 'insufficient_data',
                    'message': 'Need at least 7 days of data for anomaly detection',
                    'severity': 'info',
                    'account_id': account_id
                }]
            
            # Handle all-zero costs (common in free tier)
            if np.all(np.array(cost_values) == 0):
                return [{
                    'type': 'no_anomalies',
                    'message': 'No cost anomalies detected - all costs are zero',
                    'severity': 'info',
                    'account_id': account_id,
                    'analysis_period': f"{dates[0]} to {dates[-1]}",
                    'data_points': len(cost_values),
                    'sensitivity': sensitivity
                }]
            
            # Detect anomalies using multiple methods
            anomalies = []
            
            # Statistical method (Z-score)
            statistical_anomalies = self._detect_statistical_anomalies(cost_values, dates, sensitivity)
            anomalies.extend(statistical_anomalies)
            
            # Isolation Forest method (if we have enough variation)
            if len(set(cost_values)) > 1:  # Only if we have varying costs
                ml_anomalies = self._detect_ml_anomalies(cost_values, dates, sensitivity)
                anomalies.extend(ml_anomalies)
            
            # Trend-based anomalies
            trend_anomalies = self._detect_trend_anomalies(cost_values, dates, sensitivity)
            anomalies.extend(trend_anomalies)
            
            # Remove duplicates and sort by severity
            unique_anomalies = self._deduplicate_anomalies(anomalies)
            
            if not unique_anomalies:
                return [{
                    'type': 'no_significant_anomalies',
                    'message': 'No significant cost anomalies detected in the analysis period',
                    'severity': 'info',
                    'account_id': account_id,
                    'analysis_period': f"{dates[0]} to {dates[-1]}",
                    'data_points': len(cost_values),
                    'sensitivity': sensitivity
                }]
            
            return unique_anomalies[:10]  # Return top 10 anomalies
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return [{
                'type': 'error',
                'message': f'Anomaly detection failed: {str(e)}',
                'severity': 'error',
                'account_id': account_id
            }]
    
    def _generate_cost_forecast(self, cost_values: List[float], time_horizon: int, account_id: str) -> Dict[str, Any]:
        """Generate cost forecast using linear regression"""
        try:
            if len(cost_values) < 3:
                return self._generate_simple_forecast(cost_values, time_horizon)
            
            # Prepare data for forecasting
            X = np.array(range(len(cost_values))).reshape(-1, 1)
            y = np.array(cost_values)
            
            # Handle all-zero costs
            if np.all(y == 0):
                return {
                    'forecast_type': 'zero_cost',
                    'predictions': [{'day': i+1, 'predicted_cost': 0.0, 'confidence': 0.95} for i in range(time_horizon)],
                    'total_predicted_cost': 0.0,
                    'confidence': 0.95,
                    'model_type': 'constant_zero',
                    'trend': 'stable'
                }
            
            # Train linear regression model
            model = LinearRegression()
            model.fit(X, y)
            
            # Generate future predictions
            future_X = np.array(range(len(cost_values), len(cost_values) + time_horizon)).reshape(-1, 1)
            future_predictions = model.predict(future_X)
            
            # Ensure non-negative predictions
            future_predictions = np.maximum(future_predictions, 0)
            
            # Calculate confidence based on model performance
            train_predictions = model.predict(X)
            mae = np.mean(np.abs(y - train_predictions))
            confidence = max(0.5, min(0.95, 1 - (mae / (np.mean(y) + 0.001))))
            
            # Determine trend
            slope = model.coef_[0]
            if slope > 0.01:
                trend = 'increasing'
            elif slope < -0.01:
                trend = 'decreasing'
            else:
                trend = 'stable'
            
            predictions = []
            for i, pred in enumerate(future_predictions):
                predictions.append({
                    'day': i + 1,
                    'predicted_cost': round(pred, 2),
                    'confidence': round(confidence, 2),
                    'date': (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d')
                })
            
            return {
                'forecast_type': 'linear_regression',
                'predictions': predictions,
                'total_predicted_cost': round(np.sum(future_predictions), 2),
                'confidence': round(confidence, 2),
                'model_type': 'linear_regression',
                'trend': trend,
                'model_performance': {
                    'mean_absolute_error': round(mae, 3),
                    'r_squared': round(model.score(X, y), 3)
                }
            }
            
        except Exception as e:
            logger.error(f"Cost forecast generation failed: {e}")
            return self._generate_simple_forecast(cost_values, time_horizon)
    
    def _generate_trend_prediction(self, cost_values: List[float], time_horizon: int) -> Dict[str, Any]:
        """Generate trend predictions"""
        try:
            if len(cost_values) < 3:
                return {'trend': 'stable', 'confidence': 0.5}
            
            # Calculate trend using linear regression
            X = np.array(range(len(cost_values))).reshape(-1, 1)
            y = np.array(cost_values)
            
            model = LinearRegression()
            model.fit(X, y)
            
            slope = model.coef_[0]
            r_squared = model.score(X, y)
            
            if slope > 0.01:
                trend = 'increasing'
                magnitude = 'strong' if abs(slope) > 0.1 else 'moderate'
            elif slope < -0.01:
                trend = 'decreasing'
                magnitude = 'strong' if abs(slope) > 0.1 else 'moderate'
            else:
                trend = 'stable'
                magnitude = 'stable'
            
            return {
                'trend': trend,
                'magnitude': magnitude,
                'slope': round(slope, 4),
                'confidence': round(r_squared, 2),
                'time_horizon_days': time_horizon
            }
            
        except Exception as e:
            logger.error(f"Trend prediction failed: {e}")
            return {'trend': 'stable', 'confidence': 0.5}
    
    def _generate_anomaly_forecast(self, cost_values: List[float], time_horizon: int) -> Dict[str, Any]:
        """Generate anomaly likelihood forecast"""
        try:
            # Calculate historical volatility
            if len(cost_values) < 2:
                volatility = 0
            else:
                cost_array = np.array(cost_values)
                volatility = np.std(cost_array) / (np.mean(cost_array) + 0.001)
            
            # Predict anomaly likelihood based on volatility
            if volatility < 0.1:
                anomaly_likelihood = 'low'
                probability = 0.1
            elif volatility < 0.3:
                anomaly_likelihood = 'medium'
                probability = 0.3
            else:
                anomaly_likelihood = 'high'
                probability = 0.6
            
            return {
                'anomaly_likelihood': anomaly_likelihood,
                'probability': probability,
                'volatility_score': round(volatility, 3),
                'time_horizon_days': time_horizon,
                'recommendations': self._get_anomaly_prevention_recommendations(anomaly_likelihood)
            }
            
        except Exception as e:
            logger.error(f"Anomaly forecast failed: {e}")
            return {'anomaly_likelihood': 'unknown', 'probability': 0.5}
    
    def _detect_statistical_anomalies(self, cost_values: List[float], dates: List[str], sensitivity: str) -> List[Dict[str, Any]]:
        """Detect anomalies using statistical methods (Z-score)"""
        try:
            cost_array = np.array(cost_values)
            mean_cost = np.mean(cost_array)
            std_cost = np.std(cost_array)
            
            if std_cost == 0:  # No variation
                return []
            
            # Set threshold based on sensitivity
            threshold_map = {'low': 3.0, 'medium': 2.5, 'high': 2.0}
            threshold = threshold_map.get(sensitivity, 2.5)
            
            anomalies = []
            z_scores = np.abs((cost_array - mean_cost) / std_cost)
            
            for i, z_score in enumerate(z_scores):
                if z_score > threshold:
                    severity = 'critical' if z_score > 3.5 else 'high' if z_score > 3.0 else 'medium'
                    anomalies.append({
                        'type': 'statistical_anomaly',
                        'date': dates[i],
                        'actual_cost': round(cost_values[i], 2),
                        'expected_cost': round(mean_cost, 2),
                        'deviation': round(z_score, 2),
                        'severity': severity,
                        'method': 'z_score'
                    })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Statistical anomaly detection failed: {e}")
            return []
    
    def _detect_ml_anomalies(self, cost_values: List[float], dates: List[str], sensitivity: str) -> List[Dict[str, Any]]:
        """Detect anomalies using Isolation Forest"""
        try:
            cost_array = np.array(cost_values).reshape(-1, 1)
            
            # Set contamination based on sensitivity
            contamination_map = {'low': 0.05, 'medium': 0.1, 'high': 0.15}
            contamination = contamination_map.get(sensitivity, 0.1)
            
            # Train Isolation Forest
            iso_forest = IsolationForest(contamination=contamination, random_state=42)
            anomaly_labels = iso_forest.fit_predict(cost_array)
            anomaly_scores = iso_forest.decision_function(cost_array)
            
            anomalies = []
            for i, (label, score) in enumerate(zip(anomaly_labels, anomaly_scores)):
                if label == -1:  # Anomaly detected
                    severity = 'high' if score < -0.5 else 'medium'
                    anomalies.append({
                        'type': 'ml_anomaly',
                        'date': dates[i],
                        'actual_cost': round(cost_values[i], 2),
                        'anomaly_score': round(abs(score), 3),
                        'severity': severity,
                        'method': 'isolation_forest'
                    })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"ML anomaly detection failed: {e}")
            return []
    
    def _detect_trend_anomalies(self, cost_values: List[float], dates: List[str], sensitivity: str) -> List[Dict[str, Any]]:
        """Detect trend-based anomalies"""
        try:
            if len(cost_values) < 5:
                return []
            
            # Calculate moving average
            window_size = min(7, len(cost_values) // 2)
            moving_avg = pd.Series(cost_values).rolling(window=window_size, center=True).mean()
            
            # Set threshold based on sensitivity
            threshold_map = {'low': 0.5, 'medium': 0.3, 'high': 0.2}
            threshold = threshold_map.get(sensitivity, 0.3)
            
            anomalies = []
            for i in range(len(cost_values)):
                if pd.notna(moving_avg.iloc[i]):
                    deviation = abs(cost_values[i] - moving_avg.iloc[i]) / (moving_avg.iloc[i] + 0.001)
                    if deviation > threshold:
                        severity = 'high' if deviation > 0.8 else 'medium'
                        anomalies.append({
                            'type': 'trend_anomaly',
                            'date': dates[i],
                            'actual_cost': round(cost_values[i], 2),
                            'expected_cost': round(moving_avg.iloc[i], 2),
                            'deviation_percent': round(deviation * 100, 1),
                            'severity': severity,
                            'method': 'moving_average'
                        })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Trend anomaly detection failed: {e}")
            return []
    
    def _deduplicate_anomalies(self, anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate anomalies and sort by severity"""
        try:
            # Group by date and keep the highest severity
            date_anomalies = {}
            for anomaly in anomalies:
                date = anomaly.get('date')
                if date:
                    if date not in date_anomalies or self._get_severity_score(anomaly['severity']) > self._get_severity_score(date_anomalies[date]['severity']):
                        date_anomalies[date] = anomaly
            
            # Sort by severity and date
            sorted_anomalies = sorted(date_anomalies.values(), 
                                    key=lambda x: (self._get_severity_score(x['severity']), x['date']), 
                                    reverse=True)
            
            return sorted_anomalies
            
        except Exception as e:
            logger.error(f"Anomaly deduplication failed: {e}")
            return anomalies
    
    def _get_severity_score(self, severity: str) -> int:
        """Convert severity to numeric score for sorting"""
        severity_map = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1, 'info': 0}
        return severity_map.get(severity, 0)
    
    def _generate_simple_forecast(self, cost_values: List[float], time_horizon: int) -> Dict[str, Any]:
        """Generate simple forecast for insufficient data"""
        avg_cost = np.mean(cost_values) if cost_values else 0.0
        
        predictions = []
        for i in range(time_horizon):
            predictions.append({
                'day': i + 1,
                'predicted_cost': round(avg_cost, 2),
                'confidence': 0.6,
                'date': (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d')
            })
        
        return {
            'forecast_type': 'simple_average',
            'predictions': predictions,
            'total_predicted_cost': round(avg_cost * time_horizon, 2),
            'confidence': 0.6,
            'model_type': 'simple_average',
            'trend': 'stable'
        }
    
    def _generate_fallback_prediction(self, request: PredictionRequest) -> Dict[str, Any]:
        """Generate fallback prediction when main prediction fails"""
        return {
            'forecast_type': 'fallback',
            'predictions': [{'day': i+1, 'predicted_cost': 0.0, 'confidence': 0.5} for i in range(request.time_horizon)],
            'total_predicted_cost': 0.0,
            'confidence': 0.5,
            'model_type': 'fallback',
            'trend': 'unknown',
            'error': 'Prediction generation failed - using fallback'
        }
    
    def _get_anomaly_prevention_recommendations(self, likelihood: str) -> List[str]:
        """Get recommendations for preventing anomalies"""
        base_recommendations = [
            'Monitor cost trends regularly',
            'Set up cost alerts and budgets',
            'Review resource usage patterns'
        ]
        
        if likelihood == 'high':
            base_recommendations.extend([
                'Implement stricter cost controls',
                'Review auto-scaling policies',
                'Consider cost optimization strategies'
            ])
        elif likelihood == 'medium':
            base_recommendations.extend([
                'Increase monitoring frequency',
                'Review resource allocation'
            ])
        
        return base_recommendations
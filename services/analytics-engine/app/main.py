from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import os
import logging
from typing import Dict, List, Optional, Any
import json

from .services.analytics_service import AnalyticsService
from .services.ml_predictor import MLPredictor
from .services.report_generator import ReportGenerator
from .models.analytics import AnalyticsQuery, PredictionRequest, ReportRequest
from .utils.database import get_db_connection
from .utils.auth import verify_api_key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Initialize services
    analytics_service = AnalyticsService()
    ml_predictor = MLPredictor()
    report_generator = ReportGenerator()
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            "status": "healthy",
            "service": "analytics-engine",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        })
    
    @app.route('/ready', methods=['GET'])
    def readiness_check():
        """Readiness check endpoint"""
        try:
            # Check database connection
            db = get_db_connection()
            db.execute("SELECT 1")
            db.close()
            
            return jsonify({
                "status": "ready",
                "service": "analytics-engine",
                "database": "connected"
            })
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            return jsonify({"error": "Service not ready"}), 503
    
    @app.route('/analytics/trends', methods=['POST'])
    def analyze_trends():
        """Analyze cost trends and patterns"""
        try:
            # Verify API key
            api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not verify_api_key(api_key):
                return jsonify({"error": "Unauthorized"}), 401
            
            data = request.get_json()
            
            query = AnalyticsQuery(
                account_id=data.get('account_id'),
                start_date=data.get('start_date'),
                end_date=data.get('end_date'),
                metrics=data.get('metrics', ['total_cost', 'daily_cost']),
                filters=data.get('filters', {})
            )
            
            # Perform trend analysis
            result = analytics_service.analyze_trends(query)
            
            return jsonify({
                "account_id": query.account_id,
                "analysis_period": {
                    "start": query.start_date,
                    "end": query.end_date
                },
                "trends": result,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return jsonify({"error": f"Analysis failed: {str(e)}"}), 500
    
    @app.route('/analytics/predictions', methods=['POST'])
    def generate_predictions():
        """Generate ML-based cost predictions"""
        try:
            # Verify API key
            api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not verify_api_key(api_key):
                return jsonify({"error": "Unauthorized"}), 401
            
            data = request.get_json()
            
            request_obj = PredictionRequest(
                account_id=data.get('account_id'),
                prediction_type=data.get('prediction_type', 'cost_forecast'),
                time_horizon=data.get('time_horizon', 30),
                historical_data=data.get('historical_data', {}),
                features=data.get('features', [])
            )
            
            # Generate predictions
            predictions = ml_predictor.predict(request_obj)
            
            return jsonify({
                "account_id": request_obj.account_id,
                "prediction_type": request_obj.prediction_type,
                "time_horizon_days": request_obj.time_horizon,
                "predictions": predictions,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Prediction generation failed: {e}")
            return jsonify({"error": f"Prediction failed: {str(e)}"}), 500
    
    @app.route('/analytics/insights', methods=['POST'])
    def generate_insights():
        """Generate business insights from cost data"""
        try:
            # Verify API key
            api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not verify_api_key(api_key):
                return jsonify({"error": "Unauthorized"}), 401
            
            data = request.get_json()
            account_id = data.get('account_id')
            analysis_type = data.get('analysis_type', 'cost_optimization')
            
            # Generate insights
            insights = analytics_service.generate_insights(account_id, analysis_type, data)
            
            return jsonify({
                "account_id": account_id,
                "analysis_type": analysis_type,
                "insights": insights,
                "generated_at": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            return jsonify({"error": f"Insight generation failed: {str(e)}"}), 500
    
    @app.route('/reports/generate', methods=['POST'])
    def generate_report():
        """Generate comprehensive analytics reports"""
        try:
            # Verify API key
            api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not verify_api_key(api_key):
                return jsonify({"error": "Unauthorized"}), 401
            
            data = request.get_json()
            
            report_request = ReportRequest(
                account_id=data.get('account_id'),
                report_type=data.get('report_type', 'executive_summary'),
                period=data.get('period', 'monthly'),
                include_predictions=data.get('include_predictions', True),
                custom_metrics=data.get('custom_metrics', [])
            )
            
            # Generate report
            report = report_generator.generate_report(report_request)
            
            return jsonify({
                "report_id": report.get('report_id'),
                "account_id": report_request.account_id,
                "report_type": report_request.report_type,
                "report_data": report,
                "generated_at": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return jsonify({"error": f"Report generation failed: {str(e)}"}), 500
    
    @app.route('/analytics/dashboard/<account_id>', methods=['GET'])
    def get_dashboard_data(account_id):
        """Get dashboard data for account"""
        try:
            # Verify API key
            api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not verify_api_key(api_key):
                return jsonify({"error": "Unauthorized"}), 401
            
            # Get query parameters
            period = request.args.get('period', 'last_30_days')
            include_forecasts = request.args.get('include_forecasts', 'true').lower() == 'true'
            
            # Get dashboard data
            dashboard_data = analytics_service.get_dashboard_data(account_id, period, include_forecasts)
            
            return jsonify({
                "account_id": account_id,
                "period": period,
                "dashboard_data": dashboard_data,
                "last_updated": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Dashboard data retrieval failed: {e}")
            return jsonify({"error": f"Dashboard data failed: {str(e)}"}), 500
    
    @app.route('/analytics/benchmarks/<account_id>', methods=['GET'])
    def get_benchmarks(account_id):
        """Get industry benchmarks and comparisons"""
        try:
            # Verify API key
            api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not verify_api_key(api_key):
                return jsonify({"error": "Unauthorized"}), 401
            
            industry = request.args.get('industry', 'technology')
            company_size = request.args.get('company_size', 'medium')
            
            benchmarks = analytics_service.get_benchmarks(account_id, industry, company_size)
            
            return jsonify({
                "account_id": account_id,
                "industry": industry,
                "company_size": company_size,
                "benchmarks": benchmarks,
                "comparison_date": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Benchmark retrieval failed: {e}")
            return jsonify({"error": f"Benchmark retrieval failed: {str(e)}"}), 500
    
    @app.route('/analytics/anomalies/<account_id>', methods=['GET'])
    def detect_anomalies(account_id):
        """Detect cost anomalies using ML algorithms"""
        try:
            # Verify API key
            api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not verify_api_key(api_key):
                return jsonify({"error": "Unauthorized"}), 401
            
            days = request.args.get('days', 30, type=int)
            sensitivity = request.args.get('sensitivity', 'medium')
            
            anomalies = ml_predictor.detect_anomalies(account_id, days, sensitivity)
            
            return jsonify({
                "account_id": account_id,
                "analysis_period_days": days,
                "sensitivity": sensitivity,
                "anomalies": anomalies,
                "detected_at": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return jsonify({"error": f"Anomaly detection failed: {str(e)}"}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5002)),
        debug=os.getenv('ENVIRONMENT') == 'development'
    )
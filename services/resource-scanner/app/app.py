from flask import Flask, jsonify, request
import os
import logging
from datetime import datetime
from typing import Dict, List, Any

from app.services.aws_scanner import AWSResourceScanner
from app.services.ec2_scanner import EC2Scanner
from app.services.rds_scanner import RDSScanner
from app.services.s3_scanner import S3Scanner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Configure app
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Initialize scanners
aws_scanner = AWSResourceScanner()
ec2_scanner = EC2Scanner()
rds_scanner = RDSScanner()
s3_scanner = S3Scanner()

@app.route('/')
def root() -> Dict[str, str]:
    """Root endpoint providing service information."""
    return jsonify({
        "service": "CostWatch Resource Scanner",
        "version": "1.0.0",
        "status": "operational",
        "description": "AWS resource discovery and cost analysis service"
    })

@app.route('/health')
def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "costwatch-resource-scanner",
        "version": "1.0.0"
    })

@app.route('/scan/all', methods=['POST'])
def scan_all_resources() -> Dict[str, Any]:
    """Scan all AWS resources across all services."""
    try:
        logger.info("Starting comprehensive resource scan...")
        
        # Get scan parameters
        data = request.get_json() or {}
        regions = data.get('regions', ['us-west-2'])
        include_costs = data.get('include_costs', True)
        
        results = {
            "scan_id": f"scan_{int(datetime.utcnow().timestamp())}",
            "timestamp": datetime.utcnow().isoformat(),
            "regions": regions,
            "services": {},
            "summary": {
                "total_resources": 0,
                "total_estimated_cost": 0.0,
                "optimization_opportunities": 0
            }
        }
        
        # Scan each service
        for region in regions:
            logger.info(f"Scanning region: {region}")
            
            # EC2 instances
            ec2_results = ec2_scanner.scan_instances(region, include_costs)
            results["services"][f"ec2_{region}"] = ec2_results
            
            # RDS instances
            rds_results = rds_scanner.scan_databases(region, include_costs)
            results["services"][f"rds_{region}"] = rds_results
            
            # S3 buckets (global, but process once)
            if region == regions[0]:  # Only scan S3 once
                s3_results = s3_scanner.scan_buckets(include_costs)
                results["services"]["s3_global"] = s3_results
        
        # Calculate summary
        total_resources = 0
        total_cost = 0.0
        optimization_opportunities = 0
        
        for service_data in results["services"].values():
            total_resources += len(service_data.get("resources", []))
            total_cost += service_data.get("estimated_monthly_cost", 0.0)
            optimization_opportunities += len(service_data.get("optimization_opportunities", []))
        
        results["summary"]["total_resources"] = total_resources
        results["summary"]["total_estimated_cost"] = round(total_cost, 2)
        results["summary"]["optimization_opportunities"] = optimization_opportunities
        
        logger.info(f"Scan completed. Found {total_resources} resources with ${total_cost:.2f} estimated monthly cost")
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error during resource scan: {str(e)}")
        return jsonify({
            "error": "Scan failed",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/scan/ec2', methods=['POST'])
def scan_ec2_resources() -> Dict[str, Any]:
    """Scan EC2 instances only."""
    try:
        data = request.get_json() or {}
        region = data.get('region', 'us-west-2')
        include_costs = data.get('include_costs', True)
        
        logger.info(f"Scanning EC2 resources in region: {region}")
        results = ec2_scanner.scan_instances(region, include_costs)
        
        return jsonify({
            "scan_type": "ec2",
            "region": region,
            "timestamp": datetime.utcnow().isoformat(),
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Error scanning EC2 resources: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/scan/rds', methods=['POST'])
def scan_rds_resources() -> Dict[str, Any]:
    """Scan RDS instances only."""
    try:
        data = request.get_json() or {}
        region = data.get('region', 'us-west-2')
        include_costs = data.get('include_costs', True)
        
        logger.info(f"Scanning RDS resources in region: {region}")
        results = rds_scanner.scan_databases(region, include_costs)
        
        return jsonify({
            "scan_type": "rds",
            "region": region,
            "timestamp": datetime.utcnow().isoformat(),
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Error scanning RDS resources: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/scan/s3', methods=['POST'])
def scan_s3_resources() -> Dict[str, Any]:
    """Scan S3 buckets only."""
    try:
        data = request.get_json() or {}
        include_costs = data.get('include_costs', True)
        
        logger.info("Scanning S3 buckets globally")
        results = s3_scanner.scan_buckets(include_costs)
        
        return jsonify({
            "scan_type": "s3",
            "scope": "global",
            "timestamp": datetime.utcnow().isoformat(),
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Error scanning S3 resources: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/optimize/<resource_type>')
def get_optimization_recommendations(resource_type: str) -> Dict[str, Any]:
    """Get optimization recommendations for specific resource type."""
    try:
        if resource_type == "ec2":
            recommendations = ec2_scanner.get_optimization_recommendations()
        elif resource_type == "rds":
            recommendations = rds_scanner.get_optimization_recommendations()
        elif resource_type == "s3":
            recommendations = s3_scanner.get_optimization_recommendations()
        else:
            return jsonify({"error": f"Unsupported resource type: {resource_type}"}), 400
        
        return jsonify({
            "resource_type": resource_type,
            "timestamp": datetime.utcnow().isoformat(),
            "recommendations": recommendations
        })
        
    except Exception as e:
        logger.error(f"Error getting recommendations for {resource_type}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/metrics')
def get_metrics() -> Dict[str, Any]:
    """Get service metrics for monitoring."""
    return jsonify({
        "service": "resource-scanner",
        "uptime": "healthy",
        "last_scan": datetime.utcnow().isoformat(),
        "total_scans_today": 42,  # Mock metric
        "average_scan_duration": "15.3s",  # Mock metric
        "cache_hit_rate": "78%"  # Mock metric
    })

@app.errorhandler(404)
def not_found(error) -> tuple:
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found",
        "message": "The requested resource was not found on this server",
        "available_endpoints": [
            "/",
            "/health",
            "/scan/all",
            "/scan/ec2",
            "/scan/rds",
            "/scan/s3",
            "/optimize/<resource_type>",
            "/metrics"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error) -> tuple:
    """Handle 500 errors."""
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred while processing your request"
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Resource Scanner service on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
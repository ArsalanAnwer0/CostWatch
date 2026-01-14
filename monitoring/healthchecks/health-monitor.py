#!/usr/bin/env python3
"""
Health Monitor Script for CostWatch Services
Checks all service endpoints, database, and Redis connectivity
"""

import requests
import psycopg2
import redis
import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Tuple

# Service endpoints
SERVICES = {
    "api-gateway": os.getenv("API_GATEWAY_URL", "http://localhost:8000"),
    "cost-analyzer": os.getenv("COST_ANALYZER_URL", "http://localhost:8001"),
    "resource-scanner": os.getenv("RESOURCE_SCANNER_URL", "http://localhost:8002"),
    "analytics-engine": os.getenv("ANALYTICS_ENGINE_URL", "http://localhost:8003"),
    "alert-manager": os.getenv("ALERT_MANAGER_URL", "http://localhost:8004"),
}

# Database config
DB_CONFIG = {
    "host": os.getenv("DATABASE_HOST", "localhost"),
    "port": int(os.getenv("DATABASE_PORT", "5432")),
    "database": os.getenv("DATABASE_NAME", "costwatch_db"),
    "user": os.getenv("DATABASE_USER", "costwatch_user"),
    "password": os.getenv("DATABASE_PASSWORD", ""),
}

# Redis config
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


def check_service_health(service_name: str, url: str) -> Tuple[bool, str]:
    """Check health endpoint of a service."""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            return True, "healthy"
        else:
            return False, f"status_code: {response.status_code}"
    except requests.exceptions.Timeout:
        return False, "timeout"
    except requests.exceptions.ConnectionError:
        return False, "connection_refused"
    except Exception as e:
        return False, f"error: {str(e)}"


def check_database_health() -> Tuple[bool, str]:
    """Check PostgreSQL database connectivity."""
    try:
        conn = psycopg2.connect(**DB_CONFIG, connect_timeout=5)
        cur = conn.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result and result[0] == 1:
            return True, "connected"
        else:
            return False, "query_failed"
    except psycopg2.OperationalError as e:
        return False, f"connection_error: {str(e)}"
    except Exception as e:
        return False, f"error: {str(e)}"


def check_redis_health() -> Tuple[bool, str]:
    """Check Redis connectivity."""
    try:
        r = redis.from_url(REDIS_URL, socket_timeout=5)
        r.ping()
        return True, "connected"
    except redis.exceptions.ConnectionError:
        return False, "connection_refused"
    except redis.exceptions.TimeoutError:
        return False, "timeout"
    except Exception as e:
        return False, f"error: {str(e)}"


def run_health_checks() -> Dict:
    """Run all health checks and return results."""
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "services": {},
        "database": {},
        "redis": {},
        "overall_status": "healthy"
    }

    # Check services
    print("Checking services...")
    for service_name, url in SERVICES.items():
        healthy, status = check_service_health(service_name, url)
        results["services"][service_name] = {
            "healthy": healthy,
            "status": status,
            "url": url
        }
        print(f"  {service_name}: {'✓' if healthy else '✗'} {status}")

        if not healthy:
            results["overall_status"] = "degraded"

    # Check database
    print("\nChecking database...")
    db_healthy, db_status = check_database_health()
    results["database"] = {
        "healthy": db_healthy,
        "status": db_status,
        "host": DB_CONFIG["host"]
    }
    print(f"  PostgreSQL: {'✓' if db_healthy else '✗'} {db_status}")

    if not db_healthy:
        results["overall_status"] = "critical"

    # Check Redis
    print("\nChecking Redis...")
    redis_healthy, redis_status = check_redis_health()
    results["redis"] = {
        "healthy": redis_healthy,
        "status": redis_status,
        "url": REDIS_URL
    }
    print(f"  Redis: {'✓' if redis_healthy else '✗'} {redis_status}")

    if not redis_healthy:
        results["overall_status"] = "degraded"

    return results


def main():
    """Main function."""
    print("="*60)
    print("CostWatch Health Monitor")
    print("="*60)
    print()

    results = run_health_checks()

    print("\n" + "="*60)
    print(f"Overall Status: {results['overall_status'].upper()}")
    print("="*60)

    # Output JSON for automated parsing
    if "--json" in sys.argv:
        print(json.dumps(results, indent=2))

    # Exit with appropriate code
    if results["overall_status"] == "critical":
        sys.exit(2)
    elif results["overall_status"] == "degraded":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

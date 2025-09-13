import pytest
import asyncio
import time
import statistics
from typing import List, Dict, Any
import httpx
from tests.utils.api_client import CostWatchAPIClient
from tests.utils.test_helpers import generate_test_user

@pytest.mark.asyncio
class TestLoadPerformance:
    """Load testing for CostWatch services."""
    
    async def test_concurrent_authentication(self):
        """Test concurrent user authentication performance."""
        concurrent_users = 10
        test_users = [generate_test_user() for _ in range(concurrent_users)]
        
        # Register all users first
        for user in test_users:
            client = CostWatchAPIClient()
            await client.register_user(**user)
        
        # Test concurrent logins
        start_time = time.time()
        login_tasks = [
            self._authenticate_user(user) 
            for user in test_users
        ]
        
        results = await asyncio.gather(*login_tasks, return_exceptions=True)
        end_time = time.time()
        
        # Analyze results
        successful_logins = sum(1 for result in results if result is True)
        total_time = end_time - start_time
        avg_time_per_login = total_time / concurrent_users
        
        assert successful_logins >= concurrent_users * 0.9  # At least 90% success
        assert avg_time_per_login < 2.0  # Average login time under 2 seconds
        assert total_time < 10.0  # Total time under 10 seconds
        
        print(f"Concurrent logins: {successful_logins}/{concurrent_users}")
        print(f"Total time: {total_time:.2f}s")
        print(f"Average time per login: {avg_time_per_login:.2f}s")
    
    async def _authenticate_user(self, user_data: Dict[str, str]) -> bool:
        """Authenticate a single user."""
        try:
            client = CostWatchAPIClient()
            return await client.authenticate(user_data["email"], user_data["password"])
        except Exception:
            return False
    
    async def test_api_response_times(self):
        """Test API response times under normal load."""
        client = CostWatchAPIClient()
        test_user = generate_test_user()
        
        # Setup
        await client.register_user(**test_user)
        await client.authenticate(test_user["email"], test_user["password"])
        
        # Test endpoints with timing
        endpoints = [
            ("Cost Summary", lambda: client.get_cost_summary()),
            ("Analytics Dashboard", lambda: client.get_analytics_dashboard()),
            ("Services Health", lambda: client.check_services_health()),
            ("EC2 Optimization", lambda: client.get_optimization_recommendations("ec2")),
            ("RDS Optimization", lambda: client.get_optimization_recommendations("rds")),
        ]
        
        response_times = {}
        
        for endpoint_name, endpoint_func in endpoints:
            times = []
            
            # Test each endpoint 5 times
            for _ in range(5):
                start_time = time.time()
                result = await endpoint_func()
                end_time = time.time()
                
                assert result["status_code"] == 200
                times.append(end_time - start_time)
            
            response_times[endpoint_name] = {
                "avg": statistics.mean(times),
                "min": min(times),
                "max": max(times),
                "median": statistics.median(times)
            }
        
        # Assert performance requirements
        for endpoint_name, metrics in response_times.items():
            assert metrics["avg"] < 2.0, f"{endpoint_name} average response time too high: {metrics['avg']:.2f}s"
            assert metrics["max"] < 5.0, f"{endpoint_name} max response time too high: {metrics['max']:.2f}s"
            
            print(f"{endpoint_name}: avg={metrics['avg']:.3f}s, max={metrics['max']:.3f}s")
    
    async def test_resource_scanning_performance(self):
        """Test resource scanning performance."""
        client = CostWatchAPIClient()
        test_user = generate_test_user()
        
        # Setup
        await client.register_user(**test_user)
        await client.authenticate(test_user["email"], test_user["password"])
        
        # Test single region scan
        start_time = time.time()
        scan_result = await client.trigger_resource_scan(regions=["us-west-2"])
        end_time = time.time()
        
        assert scan_result["status_code"] == 200
        scan_time = end_time - start_time
        
        # Scan should complete within reasonable time
        assert scan_time < 30.0, f"Single region scan took too long: {scan_time:.2f}s"
        
        # Test multi-region scan
        start_time = time.time()
        multi_scan_result = await client.trigger_resource_scan(
            regions=["us-west-2", "us-east-1", "eu-west-1"]
        )
        end_time = time.time()
        
        assert multi_scan_result["status_code"] == 200
        multi_scan_time = end_time - start_time
        
        # Multi-region scan should still be reasonable
        assert multi_scan_time < 60.0, f"Multi-region scan took too long: {multi_scan_time:.2f}s"
        
        print(f"Single region scan: {scan_time:.2f}s")
        print(f"Multi-region scan: {multi_scan_time:.2f}s")
    
    async def test_concurrent_resource_scans(self):
        """Test concurrent resource scanning."""
        concurrent_scans = 5
        clients = []
        
        # Setup multiple authenticated clients
        for i in range(concurrent_scans):
            client = CostWatchAPIClient()
            user = generate_test_user()
            await client.register_user(**user)
            await client.authenticate(user["email"], user["password"])
            clients.append(client)
        
        # Trigger concurrent scans
        start_time = time.time()
        scan_tasks = [
            client.trigger_resource_scan(regions=["us-west-2"])
            for client in clients
        ]
        
        results = await asyncio.gather(*scan_tasks, return_exceptions=True)
        end_time = time.time()
        
        # Analyze results
        successful_scans = sum(
            1 for result in results 
            if not isinstance(result, Exception) and result.get("status_code") == 200
        )
        total_time = end_time - start_time
        
        assert successful_scans >= concurrent_scans * 0.8  # At least 80% success
        assert total_time < 45.0  # Should handle concurrent load efficiently
        
        print(f"Concurrent scans: {successful_scans}/{concurrent_scans}")
        print(f"Total time: {total_time:.2f}s")
    
    async def test_database_performance(self):
        """Test database performance under load."""
        # This would test database query performance
        # For now, we'll test through API endpoints that hit the database
        
        client = CostWatchAPIClient()
        test_user = generate_test_user()
        
        await client.register_user(**test_user)
        await client.authenticate(test_user["email"], test_user["password"])
        
        # Test rapid sequential requests
        request_count = 20
        start_time = time.time()
        
        for _ in range(request_count):
            result = await client.get_cost_summary()
            assert result["status_code"] == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / request_count
        
        # Database-backed requests should be fast
        assert avg_time < 0.5, f"Database queries too slow: {avg_time:.3f}s average"
        assert total_time < 10.0, f"Total time for {request_count} requests too high: {total_time:.2f}s"
        
        print(f"Database performance: {request_count} requests in {total_time:.2f}s")
        print(f"Average response time: {avg_time:.3f}s")
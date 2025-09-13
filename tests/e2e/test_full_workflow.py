import pytest
import asyncio
from tests.utils.api_client import CostWatchAPIClient
from tests.utils.test_helpers import generate_test_user, wait_for_condition

@pytest.mark.asyncio
class TestFullWorkflow:
    """End-to-end tests for complete user workflows."""
    
    async def test_complete_user_journey(self):
        """Test complete user journey from registration to optimization."""
        client = CostWatchAPIClient()
        test_user = generate_test_user()
        
        # Step 1: Register user
        register_result = await client.register_user(
            email=test_user["email"],
            password=test_user["password"],
            full_name=test_user["full_name"],
            company=test_user["company"]
        )
        assert register_result["status_code"] in [200, 400]  # 400 if user exists
        
        # Step 2: Authenticate
        auth_success = await client.authenticate(test_user["email"], test_user["password"])
        assert auth_success, "Authentication failed"
        
        # Step 3: Get initial cost summary
        cost_summary = await client.get_cost_summary()
        assert cost_summary["status_code"] == 200
        initial_data = cost_summary["data"]
        assert "total_cost" in initial_data
        
        # Step 4: Trigger resource scan
        scan_result = await client.trigger_resource_scan()
        assert scan_result["status_code"] == 200
        scan_data = scan_result["data"]
        scan_id = scan_data["scan_id"]
        
        # Step 5: Monitor scan progress
        scan_completed = await wait_for_condition(
            self._check_scan_completed,
            timeout=60.0,
            check_interval=2.0,
            client=client,
            scan_id=scan_id
        )
        assert scan_completed, "Scan did not complete within timeout"
        
        # Step 6: Get optimization recommendations
        for resource_type in ["ec2", "rds", "s3"]:
            recommendations = await client.get_optimization_recommendations(resource_type)
            assert recommendations["status_code"] == 200
            rec_data = recommendations["data"]
            assert "recommendations" in rec_data
        
        # Step 7: Check analytics dashboard
        dashboard = await client.get_analytics_dashboard()
        assert dashboard["status_code"] == 200
        dashboard_data = dashboard["data"]
        assert "cost_overview" in dashboard_data
        assert "optimization_summary" in dashboard_data
        
        # Step 8: Check services health
        health = await client.check_services_health()
        assert health["status_code"] == 200
        health_data = health["data"]
        assert "overall_status" in health_data
    
    async def _check_scan_completed(self, client: CostWatchAPIClient, scan_id: str) -> bool:
        """Check if scan is completed."""
        status_result = await client.get_scan_status(scan_id)
        if status_result["status_code"] != 200:
            return False
        
        status_data = status_result["data"]
        return status_data.get("status") == "completed"
    
    async def test_multi_region_scanning_workflow(self):
        """Test scanning across multiple regions."""
        client = CostWatchAPIClient()
        test_user = generate_test_user()
        
        # Setup user
        await client.register_user(**test_user)
        await client.authenticate(test_user["email"], test_user["password"])
        
        # Trigger multi-region scan
        regions = ["us-west-2", "us-east-1", "eu-west-1"]
        scan_result = await client.trigger_resource_scan(regions=regions)
        assert scan_result["status_code"] == 200
        
        scan_data = scan_result["data"]
        assert scan_data["regions_scanned"] == regions
        assert "details" in scan_data
        
        # Verify scan covered all regions
        details = scan_data["details"]
        assert details["total_resources"] >= 0
        assert details["estimated_cost"] >= 0
    
    async def test_error_handling_workflow(self):
        """Test error handling in various scenarios."""
        client = CostWatchAPIClient()
        
        # Test unauthenticated access
        try:
            await client.get_cost_summary()
            assert False, "Should have raised ValueError for missing auth"
        except ValueError:
            pass  # Expected
        
        # Test invalid authentication
        auth_success = await client.authenticate("invalid@email.com", "wrongpassword")
        assert not auth_success
        
        # Test with valid user
        test_user = generate_test_user()
        await client.register_user(**test_user)
        await client.authenticate(test_user["email"], test_user["password"])
        
        # Test invalid optimization type
        invalid_rec = await client.get_optimization_recommendations("invalid_type")
        assert invalid_rec["status_code"] == 400
    
    async def test_concurrent_operations(self):
        """Test concurrent operations don't interfere."""
        client1 = CostWatchAPIClient()
        client2 = CostWatchAPIClient()
        
        user1 = generate_test_user()
        user2 = generate_test_user()
        
        # Setup both users
        await client1.register_user(**user1)
        await client2.register_user(**user2)
        await client1.authenticate(user1["email"], user1["password"])
        await client2.authenticate(user2["email"], user2["password"])
        
        # Trigger concurrent scans
        scan1_task = client1.trigger_resource_scan(regions=["us-west-2"])
        scan2_task = client2.trigger_resource_scan(regions=["us-east-1"])
        
        scan1_result, scan2_result = await asyncio.gather(scan1_task, scan2_task)
        
        # Both should succeed
        assert scan1_result["status_code"] == 200
        assert scan2_result["status_code"] == 200
        
        # Should have different scan IDs
        scan1_id = scan1_result["data"]["scan_id"]
        scan2_id = scan2_result["data"]["scan_id"]
        assert scan1_id != scan2_id
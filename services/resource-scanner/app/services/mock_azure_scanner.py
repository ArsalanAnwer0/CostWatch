"""
Mock Azure Resource Scanner
Generates realistic mock data for Azure resources
"""

from datetime import datetime, timedelta
import random
from typing import List, Dict, Any

from app.models.multi_cloud_resource import (
    ComputeInstance,
    DatabaseInstance,
    StorageContainer,
    CloudProvider,
    ResourceStatus
)


class MockAzureScanner:
    """Generate mock Azure resources for demo/testing"""

    REGIONS = [
        'eastus', 'eastus2', 'westus', 'westus2', 'centralus',
        'northeurope', 'westeurope', 'uksouth', 'ukwest',
        'southeastasia', 'eastasia', 'australiaeast', 'australiasoutheast'
    ]

    VM_SIZES = [
        'Standard_B1s', 'Standard_B2s', 'Standard_D2s_v3', 'Standard_D4s_v3',
        'Standard_E2s_v3', 'Standard_E4s_v3', 'Standard_F2s_v2', 'Standard_F4s_v2'
    ]

    SQL_TIERS = [
        'Basic', 'Standard_S0', 'Standard_S1', 'Standard_S2',
        'Premium_P1', 'Premium_P2', 'GeneralPurpose_Gen5_2', 'GeneralPurpose_Gen5_4'
    ]

    STORAGE_TIERS = ['Hot', 'Cool', 'Archive']

    @staticmethod
    def generate_vm_instances(count: int = 5) -> List[ComputeInstance]:
        """Generate mock Azure Virtual Machines"""
        instances = []

        for i in range(count):
            region = random.choice(MockAzureScanner.REGIONS)
            vm_size = random.choice(MockAzureScanner.VM_SIZES)
            status = random.choice([ResourceStatus.RUNNING, ResourceStatus.STOPPED])

            # Determine specs based on VM size
            vcpus, memory_gb, monthly_cost = MockAzureScanner._get_vm_specs(vm_size)

            # If stopped, cost is much lower (only storage)
            if status == ResourceStatus.STOPPED:
                monthly_cost *= 0.1

            instance = ComputeInstance(
                resource_id=f"/subscriptions/sub123/resourceGroups/rg{i}/providers/Microsoft.Compute/virtualMachines/vm-{region}-{i:02d}",
                provider=CloudProvider.AZURE,
                name=f"vm-{region}-{i:02d}",
                region=region,
                status=status,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365)),
                instance_type=vm_size,
                vcpus=vcpus,
                memory_gb=memory_gb,
                availability_zone=f"{region}-{random.randint(1, 3)}",
                cpu_utilization=random.uniform(5, 85) if status == ResourceStatus.RUNNING else 0.0,
                estimated_monthly_cost=monthly_cost,
                tags={
                    'Environment': random.choice(['Production', 'Development', 'Staging']),
                    'Application': random.choice(['WebApp', 'API', 'Database', 'Analytics']),
                    'Owner': random.choice(['TeamA', 'TeamB', 'TeamC'])
                },
                provider_metadata={
                    'os_type': random.choice(['Linux', 'Windows']),
                    'disk_type': random.choice(['Premium_LRS', 'Standard_LRS', 'StandardSSD_LRS']),
                    'public_ip': f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}" if status == ResourceStatus.RUNNING else None,
                }
            )
            instances.append(instance)

        return instances

    @staticmethod
    def generate_sql_databases(count: int = 3) -> List[DatabaseInstance]:
        """Generate mock Azure SQL Databases"""
        databases = []

        for i in range(count):
            region = random.choice(MockAzureScanner.REGIONS)
            tier = random.choice(MockAzureScanner.SQL_TIERS)
            engine = random.choice(['SQLServer', 'MySQL', 'PostgreSQL'])

            storage_gb = random.choice([32, 64, 128, 256, 512])
            monthly_cost = MockAzureScanner._get_sql_cost(tier, storage_gb)

            database = DatabaseInstance(
                resource_id=f"/subscriptions/sub123/resourceGroups/rg{i}/providers/Microsoft.Sql/servers/sqlserver{i}/databases/db{i}",
                provider=CloudProvider.AZURE,
                name=f"sqldb-{region}-{i:02d}",
                region=region,
                status=ResourceStatus.RUNNING,
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 730)),
                db_engine=engine,
                db_version='12.0' if engine == 'SQLServer' else '8.0',
                db_instance_class=tier,
                storage_gb=storage_gb,
                storage_type='Premium_LRS',
                multi_az=random.choice([True, False]),
                encrypted=True,
                backup_retention_days=random.choice([7, 14, 30]),
                estimated_monthly_cost=monthly_cost,
                tags={
                    'Environment': random.choice(['Production', 'Development']),
                    'Application': random.choice(['WebApp', 'API', 'Analytics']),
                    'CostCenter': f"CC{random.randint(1000, 9999)}"
                },
                provider_metadata={
                    'tier': tier.split('_')[0],
                    'collation': 'SQL_Latin1_General_CP1_CI_AS',
                    'max_size_gb': storage_gb,
                }
            )
            databases.append(database)

        return databases

    @staticmethod
    def generate_blob_containers(count: int = 4) -> List[StorageContainer]:
        """Generate mock Azure Blob Storage Containers"""
        containers = []

        for i in range(count):
            region = random.choice(MockAzureScanner.REGIONS)
            tier = random.choice(MockAzureScanner.STORAGE_TIERS)

            size_gb = random.uniform(10, 5000)
            object_count = random.randint(100, 100000)
            monthly_cost = MockAzureScanner._get_storage_cost(size_gb, tier)

            container = StorageContainer(
                resource_id=f"/subscriptions/sub123/resourceGroups/rg{i}/providers/Microsoft.Storage/storageAccounts/storage{i}/blobServices/default/containers/container{i}",
                provider=CloudProvider.AZURE,
                name=f"blob-{region}-{i:02d}",
                region=region,
                status=ResourceStatus.RUNNING,
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 1095)),
                size_gb=size_gb,
                object_count=object_count,
                storage_class=tier,
                versioning_enabled=random.choice([True, False]),
                lifecycle_policy=random.choice([True, False]),
                public_access=False,
                estimated_monthly_cost=monthly_cost,
                tags={
                    'DataType': random.choice(['Backups', 'Logs', 'Media', 'Documents']),
                    'Retention': random.choice(['30days', '90days', '1year', '7years'])
                },
                provider_metadata={
                    'redundancy': random.choice(['LRS', 'GRS', 'RA-GRS', 'ZRS']),
                    'access_tier': tier,
                }
            )
            containers.append(container)

        return containers

    @staticmethod
    def _get_vm_specs(vm_size: str) -> tuple:
        """Get VM specs based on size"""
        specs = {
            'Standard_B1s': (1, 1, 10.0),
            'Standard_B2s': (2, 4, 40.0),
            'Standard_D2s_v3': (2, 8, 96.0),
            'Standard_D4s_v3': (4, 16, 192.0),
            'Standard_E2s_v3': (2, 16, 145.0),
            'Standard_E4s_v3': (4, 32, 290.0),
            'Standard_F2s_v2': (2, 4, 85.0),
            'Standard_F4s_v2': (4, 8, 169.0),
        }
        return specs.get(vm_size, (2, 4, 50.0))

    @staticmethod
    def _get_sql_cost(tier: str, storage_gb: int) -> float:
        """Calculate SQL Database cost"""
        base_costs = {
            'Basic': 5,
            'Standard_S0': 15,
            'Standard_S1': 30,
            'Standard_S2': 75,
            'Premium_P1': 465,
            'Premium_P2': 930,
            'GeneralPurpose_Gen5_2': 560,
            'GeneralPurpose_Gen5_4': 1120,
        }
        base = base_costs.get(tier, 50)
        storage_cost = (storage_gb / 100) * 10
        return base + storage_cost

    @staticmethod
    def _get_storage_cost(size_gb: float, tier: str) -> float:
        """Calculate blob storage cost"""
        costs_per_gb = {
            'Hot': 0.0184,
            'Cool': 0.01,
            'Archive': 0.002,
        }
        return size_gb * costs_per_gb.get(tier, 0.015)

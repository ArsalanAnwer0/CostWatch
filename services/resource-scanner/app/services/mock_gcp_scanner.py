"""
Mock GCP Resource Scanner
Generates realistic mock data for Google Cloud Platform resources
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


class MockGCPScanner:
    """Generate mock GCP resources for demo/testing"""

    REGIONS = [
        'us-central1', 'us-east1', 'us-west1', 'us-west2', 'us-west3',
        'europe-west1', 'europe-west2', 'europe-west3', 'europe-north1',
        'asia-east1', 'asia-east2', 'asia-southeast1', 'asia-northeast1'
    ]

    MACHINE_TYPES = [
        'e2-micro', 'e2-small', 'e2-medium', 'e2-standard-2', 'e2-standard-4',
        'n1-standard-1', 'n1-standard-2', 'n1-standard-4', 'n1-standard-8',
        'n2-standard-2', 'n2-standard-4', 'c2-standard-4', 'c2-standard-8'
    ]

    SQL_TIERS = [
        'db-f1-micro', 'db-g1-small', 'db-n1-standard-1', 'db-n1-standard-2',
        'db-n1-standard-4', 'db-n1-highmem-2', 'db-n1-highmem-4'
    ]

    STORAGE_CLASSES = ['STANDARD', 'NEARLINE', 'COLDLINE', 'ARCHIVE']

    @staticmethod
    def generate_compute_instances(count: int = 5) -> List[ComputeInstance]:
        """Generate mock GCP Compute Engine instances"""
        instances = []

        for i in range(count):
            region = random.choice(MockGCPScanner.REGIONS)
            zone = f"{region}-{random.choice(['a', 'b', 'c'])}"
            machine_type = random.choice(MockGCPScanner.MACHINE_TYPES)
            status = random.choice([ResourceStatus.RUNNING, ResourceStatus.STOPPED])

            # Determine specs based on machine type
            vcpus, memory_gb, monthly_cost = MockGCPScanner._get_machine_specs(machine_type)

            # If stopped, no compute cost (only persistent disk)
            if status == ResourceStatus.STOPPED:
                monthly_cost *= 0.05

            instance = ComputeInstance(
                resource_id=f"projects/project-123/zones/{zone}/instances/instance-{i:03d}",
                provider=CloudProvider.GCP,
                name=f"gce-{region}-{i:02d}",
                region=region,
                status=status,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365)),
                instance_type=machine_type,
                vcpus=vcpus,
                memory_gb=memory_gb,
                availability_zone=zone,
                cpu_utilization=random.uniform(5, 80) if status == ResourceStatus.RUNNING else 0.0,
                estimated_monthly_cost=monthly_cost,
                tags={
                    'env': random.choice(['prod', 'dev', 'staging']),
                    'app': random.choice(['web', 'api', 'worker', 'database']),
                    'team': random.choice(['platform', 'data', 'product'])
                },
                provider_metadata={
                    'preemptible': random.choice([True, False]),
                    'network_tier': random.choice(['PREMIUM', 'STANDARD']),
                    'boot_disk_type': random.choice(['pd-standard', 'pd-ssd', 'pd-balanced']),
                    'boot_disk_size_gb': random.choice([10, 20, 50, 100]),
                }
            )
            instances.append(instance)

        return instances

    @staticmethod
    def generate_cloud_sql_instances(count: int = 3) -> List[DatabaseInstance]:
        """Generate mock GCP Cloud SQL instances"""
        databases = []

        for i in range(count):
            region = random.choice(MockGCPScanner.REGIONS)
            tier = random.choice(MockGCPScanner.SQL_TIERS)
            engine = random.choice(['POSTGRES', 'MYSQL', 'SQLSERVER'])

            storage_gb = random.choice([10, 50, 100, 250, 500, 1000])
            monthly_cost = MockGCPScanner._get_sql_cost(tier, storage_gb, engine)

            database = DatabaseInstance(
                resource_id=f"projects/project-123/instances/cloudsql-{region}-{i:02d}",
                provider=CloudProvider.GCP,
                name=f"cloudsql-{region}-{i:02d}",
                region=region,
                status=ResourceStatus.RUNNING,
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 730)),
                db_engine=engine.lower(),
                db_version='14' if engine == 'POSTGRES' else '8.0' if engine == 'MYSQL' else '2019',
                db_instance_class=tier,
                storage_gb=storage_gb,
                storage_type=random.choice(['PD_SSD', 'PD_HDD']),
                multi_az=random.choice([True, False]),  # High availability
                encrypted=True,  # Always encrypted in GCP
                backup_retention_days=random.choice([7, 14, 30, 365]),
                estimated_monthly_cost=monthly_cost,
                tags={
                    'environment': random.choice(['production', 'development']),
                    'app': random.choice(['webapp', 'api', 'analytics']),
                    'cost-center': f"cc-{random.randint(1000, 9999)}"
                },
                provider_metadata={
                    'database_version': f"{engine}_{random.randint(12, 15)}",
                    'connection_name': f"project-123:{region}:cloudsql-{region}-{i:02d}",
                    'ipv4_enabled': True,
                }
            )
            databases.append(database)

        return databases

    @staticmethod
    def generate_storage_buckets(count: int = 4) -> List[StorageContainer]:
        """Generate mock GCP Cloud Storage buckets"""
        buckets = []

        for i in range(count):
            region = random.choice(MockGCPScanner.REGIONS)
            storage_class = random.choice(MockGCPScanner.STORAGE_CLASSES)

            size_gb = random.uniform(5, 10000)
            object_count = random.randint(50, 500000)
            monthly_cost = MockGCPScanner._get_storage_cost(size_gb, storage_class)

            bucket = StorageContainer(
                resource_id=f"bucket-{region}-{i:04d}",
                provider=CloudProvider.GCP,
                name=f"bucket-{region}-{i:04d}",
                region=region,
                status=ResourceStatus.RUNNING,
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 1095)),
                size_gb=size_gb,
                object_count=object_count,
                storage_class=storage_class,
                versioning_enabled=random.choice([True, False]),
                lifecycle_policy=random.choice([True, False]),
                public_access=random.choice([True, False]),
                estimated_monthly_cost=monthly_cost,
                tags={
                    'data-type': random.choice(['backups', 'logs', 'media', 'analytics']),
                    'retention': random.choice(['30d', '90d', '1y', '7y']),
                    'compliance': random.choice(['pci', 'hipaa', 'gdpr', 'none'])
                },
                provider_metadata={
                    'location_type': random.choice(['region', 'dual-region', 'multi-region']),
                    'uniform_bucket_level_access': True,
                }
            )
            buckets.append(bucket)

        return buckets

    @staticmethod
    def _get_machine_specs(machine_type: str) -> tuple:
        """Get machine specs (vcpus, memory, monthly cost)"""
        specs = {
            'e2-micro': (2, 1, 7.11),
            'e2-small': (2, 2, 14.23),
            'e2-medium': (2, 4, 28.45),
            'e2-standard-2': (2, 8, 56.90),
            'e2-standard-4': (4, 16, 113.81),
            'n1-standard-1': (1, 3.75, 24.27),
            'n1-standard-2': (2, 7.5, 48.55),
            'n1-standard-4': (4, 15, 97.09),
            'n1-standard-8': (8, 30, 194.18),
            'n2-standard-2': (2, 8, 69.37),
            'n2-standard-4': (4, 16, 138.74),
            'c2-standard-4': (4, 16, 186.63),
            'c2-standard-8': (8, 32, 373.26),
        }
        return specs.get(machine_type, (2, 4, 50.0))

    @staticmethod
    def _get_sql_cost(tier: str, storage_gb: int, engine: str) -> float:
        """Calculate Cloud SQL instance cost"""
        base_costs = {
            'db-f1-micro': 7.67,
            'db-g1-small': 25.00,
            'db-n1-standard-1': 69.30,
            'db-n1-standard-2': 138.60,
            'db-n1-standard-4': 277.20,
            'db-n1-highmem-2': 171.60,
            'db-n1-highmem-4': 343.20,
        }
        base = base_costs.get(tier, 50.0)

        # Storage cost: $0.17/GB for SSD, $0.09/GB for HDD
        storage_cost = storage_gb * 0.17

        # SQL Server costs more
        if engine == 'SQLSERVER':
            base *= 4

        return base + storage_cost

    @staticmethod
    def _get_storage_cost(size_gb: float, storage_class: str) -> float:
        """Calculate Cloud Storage bucket cost"""
        costs_per_gb = {
            'STANDARD': 0.020,
            'NEARLINE': 0.010,
            'COLDLINE': 0.004,
            'ARCHIVE': 0.0012,
        }
        return size_gb * costs_per_gb.get(storage_class, 0.020)

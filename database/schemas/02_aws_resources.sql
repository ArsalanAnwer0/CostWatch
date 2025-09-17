-- CostWatch AWS Resources Schema
-- Version: 1.0
-- Description: Tables for tracking AWS resources, costs, and usage data

-- Create custom types for AWS resources
CREATE TYPE resource_state AS ENUM ('running', 'stopped', 'terminated', 'pending', 'stopping', 'starting', 'available', 'unavailable', 'creating', 'deleting');
CREATE TYPE aws_service_type AS ENUM ('ec2', 'rds', 's3', 'ebs', 'elb', 'lambda', 'cloudwatch', 'efs', 'nat_gateway', 'elastic_ip', 'route53', 'cloudfront', 'other');
CREATE TYPE cost_dimension AS ENUM ('service', 'region', 'instance_type', 'usage_type', 'resource_id', 'tag');

-- AWS Accounts table (links to organizations)
CREATE TABLE aws_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    account_id VARCHAR(20) UNIQUE NOT NULL,
    account_name VARCHAR(255),
    account_alias VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    default_region VARCHAR(20) DEFAULT 'us-west-2',
    credentials_encrypted JSONB, -- Encrypted AWS credentials
    last_scan_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for aws_accounts
CREATE INDEX idx_aws_accounts_organization_id ON aws_accounts(organization_id);
CREATE INDEX idx_aws_accounts_account_id ON aws_accounts(account_id);
CREATE INDEX idx_aws_accounts_is_active ON aws_accounts(is_active);

-- AWS Regions table
CREATE TABLE aws_regions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    region_code VARCHAR(20) UNIQUE NOT NULL,
    region_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AWS Resources table (main resource tracking)
CREATE TABLE aws_resources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    aws_account_id UUID NOT NULL REFERENCES aws_accounts(id) ON DELETE CASCADE,
    resource_id VARCHAR(255) NOT NULL, -- AWS resource identifier
    resource_arn VARCHAR(500),
    resource_name VARCHAR(255),
    service_type aws_service_type NOT NULL,
    resource_type VARCHAR(100) NOT NULL, -- e.g., 't3.micro', 'gp3', 'application'
    region VARCHAR(20) NOT NULL,
    availability_zone VARCHAR(30),
    state resource_state,
    tags JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}', -- Service-specific metadata
    launch_time TIMESTAMP WITH TIME ZONE,
    last_seen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint on AWS resource ID per account
    UNIQUE(aws_account_id, resource_id)
);

-- Create indexes for aws_resources
CREATE INDEX idx_aws_resources_organization_id ON aws_resources(organization_id);
CREATE INDEX idx_aws_resources_aws_account_id ON aws_resources(aws_account_id);
CREATE INDEX idx_aws_resources_resource_id ON aws_resources(resource_id);
CREATE INDEX idx_aws_resources_service_type ON aws_resources(service_type);
CREATE INDEX idx_aws_resources_region ON aws_resources(region);
CREATE INDEX idx_aws_resources_state ON aws_resources(state);
CREATE INDEX idx_aws_resources_is_active ON aws_resources(is_active);
CREATE INDEX idx_aws_resources_last_seen_at ON aws_resources(last_seen_at);
CREATE INDEX idx_aws_resources_tags ON aws_resources USING GIN(tags);

-- Cost data table (historical cost tracking)
CREATE TABLE cost_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    aws_account_id UUID NOT NULL REFERENCES aws_accounts(id) ON DELETE CASCADE,
    aws_resource_id UUID REFERENCES aws_resources(id) ON DELETE CASCADE,
    service_type aws_service_type NOT NULL,
    usage_type VARCHAR(100),
    operation VARCHAR(100),
    region VARCHAR(20),
    cost_date DATE NOT NULL,
    unblended_cost DECIMAL(15,4) DEFAULT 0,
    blended_cost DECIMAL(15,4) DEFAULT 0,
    usage_quantity DECIMAL(15,4) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    dimensions JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint to prevent duplicate cost entries
    UNIQUE(aws_account_id, service_type, usage_type, operation, region, cost_date, aws_resource_id)
);

-- Create indexes for cost_data
CREATE INDEX idx_cost_data_organization_id ON cost_data(organization_id);
CREATE INDEX idx_cost_data_aws_account_id ON cost_data(aws_account_id);
CREATE INDEX idx_cost_data_aws_resource_id ON cost_data(aws_resource_id);
CREATE INDEX idx_cost_data_service_type ON cost_data(service_type);
CREATE INDEX idx_cost_data_cost_date ON cost_data(cost_date);
CREATE INDEX idx_cost_data_region ON cost_data(region);
CREATE INDEX idx_cost_data_usage_type ON cost_data(usage_type);

-- Resource usage metrics table (for optimization recommendations)
CREATE TABLE resource_usage_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    aws_resource_id UUID NOT NULL REFERENCES aws_resources(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4) NOT NULL,
    unit VARCHAR(50),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    dimensions JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Index for time-series queries
    UNIQUE(aws_resource_id, metric_name, timestamp)
);

-- Create indexes for resource_usage_metrics
CREATE INDEX idx_resource_usage_metrics_resource_id ON resource_usage_metrics(aws_resource_id);
CREATE INDEX idx_resource_usage_metrics_metric_name ON resource_usage_metrics(metric_name);
CREATE INDEX idx_resource_usage_metrics_timestamp ON resource_usage_metrics(timestamp);

-- EC2 specific details table
CREATE TABLE ec2_instances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    aws_resource_id UUID NOT NULL REFERENCES aws_resources(id) ON DELETE CASCADE,
    instance_type VARCHAR(50) NOT NULL,
    platform VARCHAR(50),
    tenancy VARCHAR(20) DEFAULT 'default',
    vpc_id VARCHAR(50),
    subnet_id VARCHAR(50),
    security_groups JSONB DEFAULT '[]',
    key_name VARCHAR(100),
    public_ip_address INET,
    private_ip_address INET,
    monitoring_state VARCHAR(20) DEFAULT 'disabled',
    ebs_optimized BOOLEAN DEFAULT false,
    root_device_type VARCHAR(20),
    virtualization_type VARCHAR(20),
    cpu_credits VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for ec2_instances
CREATE INDEX idx_ec2_instances_aws_resource_id ON ec2_instances(aws_resource_id);
CREATE INDEX idx_ec2_instances_instance_type ON ec2_instances(instance_type);
CREATE INDEX idx_ec2_instances_vpc_id ON ec2_instances(vpc_id);

-- RDS specific details table
CREATE TABLE rds_instances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    aws_resource_id UUID NOT NULL REFERENCES aws_resources(id) ON DELETE CASCADE,
    db_instance_class VARCHAR(50) NOT NULL,
    engine VARCHAR(50),
    engine_version VARCHAR(50),
    storage_type VARCHAR(20),
    allocated_storage INTEGER,
    max_allocated_storage INTEGER,
    storage_encrypted BOOLEAN DEFAULT false,
    multi_az BOOLEAN DEFAULT false,
    publicly_accessible BOOLEAN DEFAULT false,
    backup_retention_period INTEGER DEFAULT 0,
    db_subnet_group_name VARCHAR(100),
    vpc_security_groups JSONB DEFAULT '[]',
    performance_insights_enabled BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for rds_instances
CREATE INDEX idx_rds_instances_aws_resource_id ON rds_instances(aws_resource_id);
CREATE INDEX idx_rds_instances_db_instance_class ON rds_instances(db_instance_class);
CREATE INDEX idx_rds_instances_engine ON rds_instances(engine);

-- S3 buckets table
CREATE TABLE s3_buckets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    aws_resource_id UUID NOT NULL REFERENCES aws_resources(id) ON DELETE CASCADE,
    bucket_name VARCHAR(255) NOT NULL,
    storage_class VARCHAR(50),
    versioning_status VARCHAR(20) DEFAULT 'Suspended',
    encryption_enabled BOOLEAN DEFAULT false,
    public_read_access BOOLEAN DEFAULT false,
    public_write_access BOOLEAN DEFAULT false,
    total_size_bytes BIGINT DEFAULT 0,
    object_count BIGINT DEFAULT 0,
    lifecycle_rules JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for s3_buckets
CREATE INDEX idx_s3_buckets_aws_resource_id ON s3_buckets(aws_resource_id);
CREATE INDEX idx_s3_buckets_bucket_name ON s3_buckets(bucket_name);
CREATE INDEX idx_s3_buckets_storage_class ON s3_buckets(storage_class);

-- Resource scan jobs table (tracking scan operations)
CREATE TABLE resource_scan_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    aws_account_id UUID NOT NULL REFERENCES aws_accounts(id) ON DELETE CASCADE,
    scan_type VARCHAR(50) NOT NULL, -- 'full', 'incremental', 'service-specific'
    service_types aws_service_type[] DEFAULT '{}',
    regions VARCHAR(20)[] DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    resources_found INTEGER DEFAULT 0,
    resources_updated INTEGER DEFAULT 0,
    errors JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for resource_scan_jobs
CREATE INDEX idx_resource_scan_jobs_organization_id ON resource_scan_jobs(organization_id);
CREATE INDEX idx_resource_scan_jobs_aws_account_id ON resource_scan_jobs(aws_account_id);
CREATE INDEX idx_resource_scan_jobs_status ON resource_scan_jobs(status);
CREATE INDEX idx_resource_scan_jobs_created_at ON resource_scan_jobs(created_at);

-- Apply updated_at triggers to relevant tables
CREATE TRIGGER update_aws_accounts_updated_at 
    BEFORE UPDATE ON aws_accounts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_aws_resources_updated_at 
    BEFORE UPDATE ON aws_resources 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ec2_instances_updated_at 
    BEFORE UPDATE ON ec2_instances 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rds_instances_updated_at 
    BEFORE UPDATE ON rds_instances 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_s3_buckets_updated_at 
    BEFORE UPDATE ON s3_buckets 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default AWS regions
INSERT INTO aws_regions (region_code, region_name) VALUES
('us-east-1', 'US East (N. Virginia)'),
('us-east-2', 'US East (Ohio)'),
('us-west-1', 'US West (N. California)'),
('us-west-2', 'US West (Oregon)'),
('eu-west-1', 'Europe (Ireland)'),
('eu-west-2', 'Europe (London)'),
('eu-west-3', 'Europe (Paris)'),
('eu-central-1', 'Europe (Frankfurt)'),
('ap-southeast-1', 'Asia Pacific (Singapore)'),
('ap-southeast-2', 'Asia Pacific (Sydney)'),
('ap-northeast-1', 'Asia Pacific (Tokyo)'),
('ap-south-1', 'Asia Pacific (Mumbai)');

-- Comments for documentation
COMMENT ON TABLE aws_accounts IS 'AWS accounts linked to organizations';
COMMENT ON TABLE aws_regions IS 'AWS regions for resource location tracking';
COMMENT ON TABLE aws_resources IS 'Main table for tracking all AWS resources';
COMMENT ON TABLE cost_data IS 'Historical cost and billing data from AWS Cost Explorer';
COMMENT ON TABLE resource_usage_metrics IS 'CloudWatch metrics for resource utilization';
COMMENT ON TABLE ec2_instances IS 'EC2 instance specific details';
COMMENT ON TABLE rds_instances IS 'RDS instance specific details';
COMMENT ON TABLE s3_buckets IS 'S3 bucket specific details';
COMMENT ON TABLE resource_scan_jobs IS 'Resource scanning job status and history';
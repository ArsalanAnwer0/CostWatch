-- CostWatch Database Migration Script
-- Version: 001 - Initial Setup
-- Description: Complete database initialization with all schemas and sample data

-- Begin transaction
BEGIN;

-- Create database if it doesn't exist (this should be run by a superuser)
-- SELECT 'CREATE DATABASE costwatch_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'costwatch_db');

-- Connect to costwatch_db and run the following:

-- Set client encoding and timezone
SET client_encoding = 'UTF8';
SET timezone = 'UTC';

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Drop existing types if they exist (for clean reinstall)
DROP TYPE IF EXISTS user_role CASCADE;
DROP TYPE IF EXISTS organization_tier CASCADE;
DROP TYPE IF EXISTS alert_severity CASCADE;
DROP TYPE IF EXISTS notification_channel CASCADE;
DROP TYPE IF EXISTS resource_state CASCADE;
DROP TYPE IF EXISTS aws_service_type CASCADE;
DROP TYPE IF EXISTS cost_dimension CASCADE;
DROP TYPE IF EXISTS alert_type CASCADE;
DROP TYPE IF EXISTS alert_status CASCADE;
DROP TYPE IF EXISTS recommendation_type CASCADE;
DROP TYPE IF EXISTS recommendation_status CASCADE;
DROP TYPE IF EXISTS analysis_period CASCADE;

-- Execute all schema files in order
\i database/schemas/01_core_schema.sql
\i database/schemas/02_aws_resources.sql
\i database/schemas/03_cost_analytics_alerts.sql

-- Insert sample data for development/testing

-- Sample organization
INSERT INTO organizations (id, name, slug, tier, aws_account_id, billing_email) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'Demo Organization', 'demo-org', 'pro', '123456789012', 'billing@demo-org.com')
ON CONFLICT (id) DO NOTHING;

-- Sample admin user
INSERT INTO users (id, organization_id, email, password_hash, first_name, last_name, role, is_active, email_verified) VALUES
('550e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440000', 'admin@demo-org.com', 
 crypt('admin123', gen_salt('bf')), 'Admin', 'User', 'admin', true, true)
ON CONFLICT (email) DO NOTHING;

-- Sample regular user
INSERT INTO users (id, organization_id, email, password_hash, first_name, last_name, role, is_active, email_verified) VALUES
('550e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440000', 'user@demo-org.com',
 crypt('user123', gen_salt('bf')), 'Regular', 'User', 'user', true, true)
ON CONFLICT (email) DO NOTHING;

-- Sample AWS account
INSERT INTO aws_accounts (id, organization_id, account_id, account_name, account_alias, default_region) VALUES
('550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440000', '123456789012', 'Demo Production Account', 'demo-prod', 'us-west-2')
ON CONFLICT (account_id) DO NOTHING;

-- Sample AWS resources
INSERT INTO aws_resources (id, organization_id, aws_account_id, resource_id, resource_name, service_type, resource_type, region, state, tags, launch_time) VALUES
('550e8400-e29b-41d4-a716-446655440020', '550e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440010', 
 'i-1234567890abcdef0', 'web-server-01', 'ec2', 't3.medium', 'us-west-2', 'running', 
 '{"Environment": "production", "Team": "web", "Project": "costwatch"}', NOW() - INTERVAL '30 days'),
 
('550e8400-e29b-41d4-a716-446655440021', '550e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440010', 
 'db-instance-prod', 'main-database', 'rds', 'db.t3.small', 'us-west-2', 'available', 
 '{"Environment": "production", "Team": "backend", "Project": "costwatch"}', NOW() - INTERVAL '60 days'),
 
('550e8400-e29b-41d4-a716-446655440022', '550e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440010', 
 'costwatch-backups', 'Application Backups', 's3', 'standard', 'us-west-2', 'available', 
 '{"Environment": "production", "Team": "ops", "Project": "costwatch"}', NOW() - INTERVAL '90 days')
ON CONFLICT (aws_account_id, resource_id) DO NOTHING;

-- Sample EC2 instance details
INSERT INTO ec2_instances (aws_resource_id, instance_type, platform, vpc_id, subnet_id, public_ip_address, private_ip_address) VALUES
('550e8400-e29b-41d4-a716-446655440020', 't3.medium', 'Linux/UNIX', 'vpc-12345678', 'subnet-12345678', '52.12.34.56', '10.0.1.100')
ON CONFLICT (aws_resource_id) DO NOTHING;

-- Sample RDS instance details
INSERT INTO rds_instances (aws_resource_id, db_instance_class, engine, engine_version, allocated_storage, multi_az, backup_retention_period) VALUES
('550e8400-e29b-41d4-a716-446655440021', 'db.t3.small', 'postgres', '13.7', 100, false, 7)
ON CONFLICT (aws_resource_id) DO NOTHING;

-- Sample S3 bucket details
INSERT INTO s3_buckets (aws_resource_id, bucket_name, storage_class, versioning_status, total_size_bytes, object_count) VALUES
('550e8400-e29b-41d4-a716-446655440022', 'costwatch-backups', 'STANDARD', 'Enabled', 1073741824, 1250)
ON CONFLICT (aws_resource_id) DO NOTHING;

-- Sample cost data (last 30 days)
INSERT INTO cost_data (organization_id, aws_account_id, aws_resource_id, service_type, usage_type, region, cost_date, unblended_cost, usage_quantity)
SELECT 
    '550e8400-e29b-41d4-a716-446655440000',
    '550e8400-e29b-41d4-a716-446655440010',
    '550e8400-e29b-41d4-a716-446655440020',
    'ec2',
    'BoxUsage:t3.medium',
    'us-west-2',
    generate_series(CURRENT_DATE - INTERVAL '30 days', CURRENT_DATE - INTERVAL '1 day', INTERVAL '1 day')::date,
    ROUND((RANDOM() * 5 + 10)::numeric, 4), -- Random cost between $10-15 per day
    24 -- 24 hours usage per day
ON CONFLICT (aws_account_id, service_type, usage_type, operation, region, cost_date, aws_resource_id) DO NOTHING;

-- Sample budget
INSERT INTO budgets (id, organization_id, name, amount, period, start_date, created_by) VALUES
('550e8400-e29b-41d4-a716-446655440030', '550e8400-e29b-41d4-a716-446655440000', 'Monthly AWS Budget', 1000.00, 'monthly', 
 DATE_TRUNC('month', CURRENT_DATE), '550e8400-e29b-41d4-a716-446655440001')
ON CONFLICT (id) DO NOTHING;

-- Sample alert rule
INSERT INTO alert_rules (id, organization_id, name, description, alert_type, conditions, severity, notification_channels, created_by) VALUES
('550e8400-e29b-41d4-a716-446655440040', '550e8400-e29b-41d4-a716-446655440000', 'High Daily Cost Alert', 
 'Alert when daily costs exceed $50', 'cost_threshold', '{"threshold": 50, "period": "daily"}', 'high', 
 ARRAY['email']::notification_channel[], '550e8400-e29b-41d4-a716-446655440001')
ON CONFLICT (id) DO NOTHING;

-- Sample optimization recommendation
INSERT INTO optimization_recommendations (id, organization_id, aws_resource_id, recommendation_type, title, description, potential_savings, confidence_score) VALUES
('550e8400-e29b-41d4-a716-446655440050', '550e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440020',
 'rightsizing', 'Downsize EC2 Instance', 'This t3.medium instance shows low CPU utilization. Consider downsizing to t3.small.', 
 120.00, 0.85)
ON CONFLICT (id) DO NOTHING;

-- Create database functions for common operations

-- Function to get monthly cost summary
CREATE OR REPLACE FUNCTION get_monthly_cost_summary(org_id UUID, month_date DATE DEFAULT CURRENT_DATE)
RETURNS TABLE(
    service_type aws_service_type,
    region VARCHAR(20),
    total_cost DECIMAL(15,4),
    resource_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cd.service_type,
        cd.region,
        SUM(cd.unblended_cost) as total_cost,
        COUNT(DISTINCT cd.aws_resource_id) as resource_count
    FROM cost_data cd
    WHERE cd.organization_id = org_id
      AND DATE_TRUNC('month', cd.cost_date) = DATE_TRUNC('month', month_date)
    GROUP BY cd.service_type, cd.region
    ORDER BY total_cost DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up old data
CREATE OR REPLACE FUNCTION cleanup_old_data(days_to_keep INTEGER DEFAULT 365)
RETURNS VOID AS $$
BEGIN
    -- Clean up old cost data
    DELETE FROM cost_data WHERE cost_date < CURRENT_DATE - INTERVAL '1 day' * days_to_keep;
    
    -- Clean up old resource usage metrics
    DELETE FROM resource_usage_metrics WHERE timestamp < NOW() - INTERVAL '1 day' * days_to_keep;
    
    -- Clean up resolved alerts older than 90 days
    DELETE FROM alerts WHERE status = 'resolved' AND resolved_at < NOW() - INTERVAL '90 days';
    
    -- Clean up old notification records
    DELETE FROM alert_notifications WHERE created_at < NOW() - INTERVAL '90 days';
    
    -- Clean up old analytics jobs
    DELETE FROM analytics_jobs WHERE status IN ('completed', 'failed') AND completed_at < NOW() - INTERVAL '30 days';
    
    -- Clean up expired recommendations
    DELETE FROM optimization_recommendations WHERE status = 'expired' AND valid_until < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- Create indexes for performance optimization
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cost_data_date_service ON cost_data(cost_date, service_type);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cost_data_org_date ON cost_data(organization_id, cost_date);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alerts_org_status ON alerts(organization_id, status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_resources_org_service ON aws_resources(organization_id, service_type);

-- Grant permissions (adjust based on your user setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO costwatch_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO costwatch_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO costwatch_user;

-- Set up row level security (optional, for multi-tenant security)
-- ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE aws_resources ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE cost_data ENABLE ROW LEVEL SECURITY;

-- Create policies (example for organization-level security)
-- CREATE POLICY org_policy ON aws_resources FOR ALL TO costwatch_user USING (organization_id = current_setting('app.current_org_id')::UUID);

-- Commit the transaction
COMMIT;

-- Analyze tables for optimal query planning
ANALYZE organizations;
ANALYZE users;
ANALYZE aws_accounts;
ANALYZE aws_resources;
ANALYZE cost_data;
ANALYZE alerts;
ANALYZE alert_rules;
ANALYZE budgets;

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'CostWatch database initialization completed successfully!';
    RAISE NOTICE 'Sample data inserted for development and testing.';
    RAISE NOTICE 'Database is ready for application deployment.';
END $$;
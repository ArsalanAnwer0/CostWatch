-- CostWatch Database Initialization Script

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create AWS accounts table
CREATE TABLE IF NOT EXISTS aws_accounts (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(12) UNIQUE NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    role_arn VARCHAR(255),
    external_id VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create resources table
CREATE TABLE IF NOT EXISTS resources (
    id SERIAL PRIMARY KEY,
    resource_id VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    account_id VARCHAR(12) NOT NULL,
    status VARCHAR(50),
    tags JSONB,
    metadata JSONB,
    estimated_monthly_cost DECIMAL(10,2),
    last_scanned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(resource_id, account_id)
);

-- Create cost_data table
CREATE TABLE IF NOT EXISTS cost_data (
    id SERIAL PRIMARY KEY,
    resource_id VARCHAR(255) NOT NULL,
    account_id VARCHAR(12) NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    cost_date DATE NOT NULL,
    cost_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    region VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(resource_id, account_id, cost_date)
);

-- Create optimization_opportunities table
CREATE TABLE IF NOT EXISTS optimization_opportunities (
    id SERIAL PRIMARY KEY,
    resource_id VARCHAR(255) NOT NULL,
    account_id VARCHAR(12) NOT NULL,
    opportunity_type VARCHAR(100) NOT NULL,
    recommendation TEXT NOT NULL,
    potential_savings DECIMAL(10,2),
    priority VARCHAR(20) DEFAULT 'medium',
    effort VARCHAR(20) DEFAULT 'medium',
    category VARCHAR(50) DEFAULT 'cost',
    status VARCHAR(20) DEFAULT 'open',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create scan_jobs table
CREATE TABLE IF NOT EXISTS scan_jobs (
    id SERIAL PRIMARY KEY,
    job_id UUID DEFAULT uuid_generate_v4(),
    job_type VARCHAR(50) NOT NULL,
    account_id VARCHAR(12),
    regions TEXT[],
    status VARCHAR(20) DEFAULT 'pending',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    results JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create cost_alerts table
CREATE TABLE IF NOT EXISTS cost_alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    alert_name VARCHAR(255) NOT NULL,
    threshold_amount DECIMAL(10,2) NOT NULL,
    threshold_period VARCHAR(20) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    last_triggered_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_resources_account_id ON resources(account_id);
CREATE INDEX IF NOT EXISTS idx_resources_resource_type ON resources(resource_type);
CREATE INDEX IF NOT EXISTS idx_resources_region ON resources(region);
CREATE INDEX IF NOT EXISTS idx_resources_last_scanned ON resources(last_scanned_at);
CREATE INDEX IF NOT EXISTS idx_cost_data_account_date ON cost_data(account_id, cost_date);
CREATE INDEX IF NOT EXISTS idx_cost_data_service ON cost_data(service_name);
CREATE INDEX IF NOT EXISTS idx_optimization_status ON optimization_opportunities(status);
CREATE INDEX IF NOT EXISTS idx_optimization_priority ON optimization_opportunities(priority);
CREATE INDEX IF NOT EXISTS idx_scan_jobs_status ON scan_jobs(status);
CREATE INDEX IF NOT EXISTS idx_scan_jobs_created ON scan_jobs(created_at);

-- Create GIN indexes for JSONB columns
CREATE INDEX IF NOT EXISTS idx_resources_tags_gin ON resources USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_resources_metadata_gin ON resources USING GIN(metadata);

-- Insert sample data
INSERT INTO users (email, full_name, company, hashed_password) VALUES 
('admin@costwatch.com', 'Admin User', 'CostWatch', 'hashed_admin_password'),
('demo@costwatch.com', 'Demo User', 'Demo Company', 'hashed_demo_password')
ON CONFLICT (email) DO NOTHING;

INSERT INTO aws_accounts (account_id, account_name) VALUES 
('123456789012', 'Production Account'),
('123456789013', 'Development Account'),
('123456789014', 'Staging Account')
ON CONFLICT (account_id) DO NOTHING;

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_aws_accounts_updated_at BEFORE UPDATE ON aws_accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_resources_updated_at BEFORE UPDATE ON resources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_optimization_opportunities_updated_at BEFORE UPDATE ON optimization_opportunities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cost_alerts_updated_at BEFORE UPDATE ON cost_alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
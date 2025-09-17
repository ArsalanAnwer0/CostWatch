-- CostWatch Cost Analytics and Alerts Schema
-- Version: 1.0
-- Description: Tables for cost analysis, predictions, optimization recommendations, and alerts

-- Create custom types for analytics and alerts
CREATE TYPE alert_type AS ENUM ('cost_threshold', 'budget_exceeded', 'anomaly_detected', 'usage_spike', 'optimization_opportunity', 'service_health');
CREATE TYPE alert_status AS ENUM ('active', 'acknowledged', 'resolved', 'suppressed');
CREATE TYPE recommendation_type AS ENUM ('rightsizing', 'reserved_instances', 'spot_instances', 'storage_optimization', 'unused_resources', 'scheduling');
CREATE TYPE recommendation_status AS ENUM ('pending', 'accepted', 'rejected', 'implemented', 'expired');
CREATE TYPE analysis_period AS ENUM ('hourly', 'daily', 'weekly', 'monthly', 'yearly');

-- Budgets table
CREATE TABLE budgets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    period analysis_period DEFAULT 'monthly',
    start_date DATE NOT NULL,
    end_date DATE,
    filters JSONB DEFAULT '{}', -- Service, region, tag filters
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for budgets
CREATE INDEX idx_budgets_organization_id ON budgets(organization_id);
CREATE INDEX idx_budgets_is_active ON budgets(is_active);
CREATE INDEX idx_budgets_period ON budgets(period);

-- Cost forecasts table
CREATE TABLE cost_forecasts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    aws_account_id UUID REFERENCES aws_accounts(id) ON DELETE CASCADE,
    service_type aws_service_type,
    region VARCHAR(20),
    forecast_date DATE NOT NULL,
    predicted_cost DECIMAL(15,4) NOT NULL,
    confidence_interval_lower DECIMAL(15,4),
    confidence_interval_upper DECIMAL(15,4),
    confidence_score DECIMAL(5,4) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    model_version VARCHAR(50),
    factors JSONB DEFAULT '{}', -- Factors influencing the forecast
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for cost_forecasts
CREATE INDEX idx_cost_forecasts_organization_id ON cost_forecasts(organization_id);
CREATE INDEX idx_cost_forecasts_forecast_date ON cost_forecasts(forecast_date);
CREATE INDEX idx_cost_forecasts_service_type ON cost_forecasts(service_type);

-- Cost anomalies table
CREATE TABLE cost_anomalies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    aws_account_id UUID REFERENCES aws_accounts(id) ON DELETE CASCADE,
    aws_resource_id UUID REFERENCES aws_resources(id) ON DELETE CASCADE,
    service_type aws_service_type,
    anomaly_date DATE NOT NULL,
    expected_cost DECIMAL(15,4) NOT NULL,
    actual_cost DECIMAL(15,4) NOT NULL,
    deviation_percentage DECIMAL(8,2) NOT NULL,
    anomaly_score DECIMAL(5,4) CHECK (anomaly_score >= 0 AND anomaly_score <= 1),
    severity alert_severity,
    description TEXT,
    root_cause JSONB DEFAULT '{}',
    is_resolved BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for cost_anomalies
CREATE INDEX idx_cost_anomalies_organization_id ON cost_anomalies(organization_id);
CREATE INDEX idx_cost_anomalies_anomaly_date ON cost_anomalies(anomaly_date);
CREATE INDEX idx_cost_anomalies_severity ON cost_anomalies(severity);
CREATE INDEX idx_cost_anomalies_is_resolved ON cost_anomalies(is_resolved);

-- Optimization recommendations table
CREATE TABLE optimization_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    aws_resource_id UUID REFERENCES aws_resources(id) ON DELETE CASCADE,
    recommendation_type recommendation_type NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    potential_savings DECIMAL(15,2),
    confidence_score DECIMAL(5,4) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    effort_level VARCHAR(20) DEFAULT 'medium', -- low, medium, high
    impact_level VARCHAR(20) DEFAULT 'medium', -- low, medium, high
    implementation_details JSONB DEFAULT '{}',
    status recommendation_status DEFAULT 'pending',
    valid_until TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for optimization_recommendations
CREATE INDEX idx_optimization_recommendations_organization_id ON optimization_recommendations(organization_id);
CREATE INDEX idx_optimization_recommendations_type ON optimization_recommendations(recommendation_type);
CREATE INDEX idx_optimization_recommendations_status ON optimization_recommendations(status);
CREATE INDEX idx_optimization_recommendations_potential_savings ON optimization_recommendations(potential_savings);

-- Alert rules table
CREATE TABLE alert_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    alert_type alert_type NOT NULL,
    conditions JSONB NOT NULL, -- Alert conditions and thresholds
    filters JSONB DEFAULT '{}', -- Resource filters
    severity alert_severity DEFAULT 'medium',
    notification_channels notification_channel[] DEFAULT '{}',
    notification_settings JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    cooldown_minutes INTEGER DEFAULT 60,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for alert_rules
CREATE INDEX idx_alert_rules_organization_id ON alert_rules(organization_id);
CREATE INDEX idx_alert_rules_alert_type ON alert_rules(alert_type);
CREATE INDEX idx_alert_rules_is_active ON alert_rules(is_active);

-- Alerts table (alert instances)
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    alert_rule_id UUID REFERENCES alert_rules(id) ON DELETE CASCADE,
    aws_resource_id UUID REFERENCES aws_resources(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    severity alert_severity NOT NULL,
    status alert_status DEFAULT 'active',
    triggered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    acknowledged_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID REFERENCES users(id),
    suppressed_until TIMESTAMP WITH TIME ZONE,
    trigger_data JSONB DEFAULT '{}', -- Data that triggered the alert
    resolution_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for alerts
CREATE INDEX idx_alerts_organization_id ON alerts(organization_id);
CREATE INDEX idx_alerts_alert_rule_id ON alerts(alert_rule_id);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_triggered_at ON alerts(triggered_at);

-- Alert notifications table (tracking sent notifications)
CREATE TABLE alert_notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_id UUID NOT NULL REFERENCES alerts(id) ON DELETE CASCADE,
    channel notification_channel NOT NULL,
    recipient VARCHAR(255) NOT NULL,
    subject VARCHAR(255),
    message TEXT,
    status VARCHAR(20) DEFAULT 'pending', -- pending, sent, failed, delivered
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for alert_notifications
CREATE INDEX idx_alert_notifications_alert_id ON alert_notifications(alert_id);
CREATE INDEX idx_alert_notifications_status ON alert_notifications(status);
CREATE INDEX idx_alert_notifications_channel ON alert_notifications(channel);

-- Cost trends table (aggregated cost data for analytics)
CREATE TABLE cost_trends (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    aws_account_id UUID REFERENCES aws_accounts(id) ON DELETE CASCADE,
    service_type aws_service_type,
    region VARCHAR(20),
    period analysis_period NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_cost DECIMAL(15,4) NOT NULL,
    average_daily_cost DECIMAL(15,4),
    cost_change_percentage DECIMAL(8,2),
    usage_quantity DECIMAL(15,4),
    dimensions JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint for each trend period
    UNIQUE(organization_id, aws_account_id, service_type, region, period, period_start)
);

-- Create indexes for cost_trends
CREATE INDEX idx_cost_trends_organization_id ON cost_trends(organization_id);
CREATE INDEX idx_cost_trends_period ON cost_trends(period);
CREATE INDEX idx_cost_trends_period_start ON cost_trends(period_start);
CREATE INDEX idx_cost_trends_service_type ON cost_trends(service_type);

-- Analytics jobs table (tracking analytics processing)
CREATE TABLE analytics_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    job_type VARCHAR(50) NOT NULL, -- 'cost_analysis', 'anomaly_detection', 'forecasting', 'optimization'
    parameters JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, failed
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    results JSONB DEFAULT '{}',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for analytics_jobs
CREATE INDEX idx_analytics_jobs_organization_id ON analytics_jobs(organization_id);
CREATE INDEX idx_analytics_jobs_job_type ON analytics_jobs(job_type);
CREATE INDEX idx_analytics_jobs_status ON analytics_jobs(status);
CREATE INDEX idx_analytics_jobs_created_at ON analytics_jobs(created_at);

-- ML models table (storing model metadata)
CREATE TABLE ml_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- 'forecasting', 'anomaly_detection', 'optimization'
    version VARCHAR(20) NOT NULL,
    accuracy_score DECIMAL(5,4),
    training_data_start DATE,
    training_data_end DATE,
    model_parameters JSONB DEFAULT '{}',
    feature_importance JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    trained_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(model_name, version)
);

-- Create indexes for ml_models
CREATE INDEX idx_ml_models_organization_id ON ml_models(organization_id);
CREATE INDEX idx_ml_models_model_type ON ml_models(model_type);
CREATE INDEX idx_ml_models_is_active ON ml_models(is_active);

-- Apply updated_at triggers
CREATE TRIGGER update_budgets_updated_at 
    BEFORE UPDATE ON budgets 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_optimization_recommendations_updated_at 
    BEFORE UPDATE ON optimization_recommendations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alert_rules_updated_at 
    BEFORE UPDATE ON alert_rules 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alerts_updated_at 
    BEFORE UPDATE ON alerts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default alert rules for new organizations (will be created via application)
-- This is handled in the application code, not as static data

-- Views for common analytics queries
CREATE VIEW monthly_cost_summary AS
SELECT 
    ct.organization_id,
    ct.aws_account_id,
    ct.service_type,
    ct.region,
    ct.period_start,
    ct.total_cost,
    ct.cost_change_percentage,
    LAG(ct.total_cost) OVER (
        PARTITION BY ct.organization_id, ct.aws_account_id, ct.service_type, ct.region 
        ORDER BY ct.period_start
    ) as previous_period_cost
FROM cost_trends ct
WHERE ct.period = 'monthly';

CREATE VIEW active_alerts_summary AS
SELECT 
    a.organization_id,
    a.severity,
    a.status,
    COUNT(*) as alert_count,
    MIN(a.triggered_at) as oldest_alert,
    MAX(a.triggered_at) as newest_alert
FROM alerts a
WHERE a.status IN ('active', 'acknowledged')
GROUP BY a.organization_id, a.severity, a.status;

-- Comments for documentation
COMMENT ON TABLE budgets IS 'Budget definitions and limits';
COMMENT ON TABLE cost_forecasts IS 'ML-generated cost predictions';
COMMENT ON TABLE cost_anomalies IS 'Detected cost anomalies and outliers';
COMMENT ON TABLE optimization_recommendations IS 'AI-generated cost optimization suggestions';
COMMENT ON TABLE alert_rules IS 'Alert rule definitions and configurations';
COMMENT ON TABLE alerts IS 'Alert instances and their lifecycle';
COMMENT ON TABLE alert_notifications IS 'Notification delivery tracking';
COMMENT ON TABLE cost_trends IS 'Aggregated cost trend data for analytics';
COMMENT ON TABLE analytics_jobs IS 'Background analytics job tracking';
COMMENT ON TABLE ml_models IS 'Machine learning model metadata and versions';
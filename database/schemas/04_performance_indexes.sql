-- Performance Indexes for CostWatch Database
-- These indexes optimize common query patterns for faster performance

-- ============================================================================
-- COST_DATA TABLE INDEXES
-- ============================================================================

-- Composite index for time-series cost queries by organization
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cost_data_org_date_service
ON cost_data (organization_id, cost_date DESC, service_type)
WHERE deleted_at IS NULL;

-- Index for cost aggregation queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cost_data_date_range
ON cost_data (cost_date DESC, organization_id)
INCLUDE (unblended_cost, blended_cost, service_type)
WHERE deleted_at IS NULL;

-- Index for service-specific cost queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cost_data_service_date
ON cost_data (service_type, organization_id, cost_date DESC)
WHERE deleted_at IS NULL;

-- Index for region-based cost analysis
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cost_data_region
ON cost_data (region, organization_id, cost_date DESC)
WHERE deleted_at IS NULL;

-- BRIN index for time-series data (efficient for large tables)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cost_data_date_brin
ON cost_data USING BRIN (cost_date)
WITH (pages_per_range = 128);

-- ============================================================================
-- AWS_RESOURCES TABLE INDEXES
-- ============================================================================

-- Composite index for resource lookups by organization and type
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_aws_resources_org_type_state
ON aws_resources (organization_id, resource_type, state)
WHERE deleted_at IS NULL;

-- Index for resource ARN lookups (unique)
CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_aws_resources_arn_unique
ON aws_resources (resource_arn)
WHERE deleted_at IS NULL;

-- Index for resource region queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_aws_resources_region
ON aws_resources (region, organization_id, resource_type)
WHERE deleted_at IS NULL;

-- Index for active resource queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_aws_resources_active
ON aws_resources (organization_id, resource_type)
INCLUDE (resource_id, region, state)
WHERE state = 'running' AND deleted_at IS NULL;

-- Index for resource discovery by launch time
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_aws_resources_launch_time
ON aws_resources (launch_time DESC, organization_id)
WHERE deleted_at IS NULL;

-- GIN index for tags JSONB queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_aws_resources_tags_gin
ON aws_resources USING GIN (tags);

-- ============================================================================
-- COST_FORECASTS TABLE INDEXES
-- ============================================================================

-- Index for forecast queries by organization and date
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cost_forecasts_org_date
ON cost_forecasts (organization_id, forecast_date DESC)
WHERE deleted_at IS NULL;

-- Index for confidence-based forecast queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cost_forecasts_confidence
ON cost_forecasts (confidence_score DESC, organization_id)
WHERE deleted_at IS NULL;

-- ============================================================================
-- ANOMALIES TABLE INDEXES
-- ============================================================================

-- Index for recent anomalies
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_anomalies_org_detected
ON anomalies (organization_id, detected_at DESC, severity)
WHERE deleted_at IS NULL;

-- Index for high-severity anomalies
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_anomalies_severity
ON anomalies (severity, organization_id, detected_at DESC)
WHERE severity IN ('high', 'critical') AND deleted_at IS NULL;

-- Index for unresolved anomalies
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_anomalies_unresolved
ON anomalies (organization_id, detected_at DESC)
WHERE resolved_at IS NULL AND deleted_at IS NULL;

-- ============================================================================
-- ALERT_RULES TABLE INDEXES
-- ============================================================================

-- Index for enabled rules by organization
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alert_rules_org_enabled
ON alert_rules (organization_id, enabled)
WHERE deleted_at IS NULL;

-- Index for rule lookups by name
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alert_rules_name
ON alert_rules (name, organization_id)
WHERE deleted_at IS NULL;

-- ============================================================================
-- ALERT_NOTIFICATIONS TABLE INDEXES
-- ============================================================================

-- Index for notification history by alert
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alert_notifications_alert
ON alert_notifications (alert_id, sent_at DESC)
WHERE deleted_at IS NULL;

-- Index for failed notifications requiring retry
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alert_notifications_failed
ON alert_notifications (sent_at ASC)
WHERE status = 'failed' AND deleted_at IS NULL;

-- ============================================================================
-- RESOURCE_USAGE_METRICS TABLE INDEXES
-- ============================================================================

-- Index for time-series metrics queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_resource_metrics_timestamp
ON resource_usage_metrics (resource_id, timestamp DESC, metric_name);

-- BRIN index for timestamp (efficient for time-series)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_resource_metrics_timestamp_brin
ON resource_usage_metrics USING BRIN (timestamp)
WITH (pages_per_range = 128);

-- Index for metric aggregation
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_resource_metrics_aggregation
ON resource_usage_metrics (resource_id, metric_name, timestamp DESC)
INCLUDE (metric_value, unit);

-- ============================================================================
-- API_KEYS TABLE INDEXES
-- ============================================================================

-- Index for active API key lookups
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_keys_key_hash
ON api_keys (key_hash)
WHERE is_active = true AND (expires_at IS NULL OR expires_at > NOW()) AND deleted_at IS NULL;

-- ============================================================================
-- SESSIONS TABLE INDEXES
-- ============================================================================

-- Index for active session lookups
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_token
ON sessions (session_token)
WHERE expires_at > NOW() AND deleted_at IS NULL;

-- Index for user sessions
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_user
ON sessions (user_id, created_at DESC)
WHERE deleted_at IS NULL;

-- ============================================================================
-- OPTIMIZATION NOTES
-- ============================================================================

-- CONCURRENTLY: Indexes are created without blocking writes
-- WHERE clauses: Partial indexes for frequently filtered data
-- INCLUDE: Covering indexes to avoid table lookups
-- BRIN: Block Range INdexes for time-series data (lower storage overhead)
-- GIN: Generalized Inverted Index for JSONB columns
-- DESC: Descending order for recent-first queries

-- To monitor index usage:
-- SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
-- FROM pg_stat_user_indexes
-- WHERE schemaname = 'public'
-- ORDER BY idx_scan ASC;

-- To find missing indexes:
-- SELECT schemaname, tablename, attname, n_distinct, correlation
-- FROM pg_stats
-- WHERE schemaname = 'public'
-- AND n_distinct > 100
-- ORDER BY abs(correlation) DESC;

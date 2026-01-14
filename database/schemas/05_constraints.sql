-- Database Constraints and Validation Rules
-- These constraints ensure data integrity and enforce business rules

-- ============================================================================
-- COST_DATA TABLE CONSTRAINTS
-- ============================================================================

-- Ensure costs are non-negative
ALTER TABLE cost_data
ADD CONSTRAINT chk_cost_data_unblended_cost_positive
CHECK (unblended_cost >= 0);

ALTER TABLE cost_data
ADD CONSTRAINT chk_cost_data_blended_cost_positive
CHECK (blended_cost >= 0);

-- Ensure cost_date is not in the future
ALTER TABLE cost_data
ADD CONSTRAINT chk_cost_data_date_not_future
CHECK (cost_date <= CURRENT_DATE);

-- Ensure service_type is not empty
ALTER TABLE cost_data
ADD CONSTRAINT chk_cost_data_service_type_not_empty
CHECK (service_type <> '' AND service_type IS NOT NULL);

-- Ensure region is not empty when specified
ALTER TABLE cost_data
ADD CONSTRAINT chk_cost_data_region_not_empty
CHECK (region IS NULL OR region <> '');

-- ============================================================================
-- AWS_RESOURCES TABLE CONSTRAINTS
-- ============================================================================

-- Ensure resource_id is not empty
ALTER TABLE aws_resources
ADD CONSTRAINT chk_aws_resources_resource_id_not_empty
CHECK (resource_id <> '' AND resource_id IS NOT NULL);

-- Ensure resource_arn is not empty
ALTER TABLE aws_resources
ADD CONSTRAINT chk_aws_resources_arn_not_empty
CHECK (resource_arn <> '' AND resource_arn IS NOT NULL);

-- Ensure resource_type is not empty
ALTER TABLE aws_resources
ADD CONSTRAINT chk_aws_resources_type_not_empty
CHECK (resource_type <> '' AND resource_type IS NOT NULL);

-- Ensure state is valid
ALTER TABLE aws_resources
ADD CONSTRAINT chk_aws_resources_state_valid
CHECK (state IN ('running', 'stopped', 'terminated', 'pending', 'stopping', 'available', 'deleting', 'deleted'));

-- Ensure region is not empty
ALTER TABLE aws_resources
ADD CONSTRAINT chk_aws_resources_region_not_empty
CHECK (region <> '' AND region IS NOT NULL);

-- Ensure launch_time is not in the future
ALTER TABLE aws_resources
ADD CONSTRAINT chk_aws_resources_launch_time_not_future
CHECK (launch_time <= NOW());

-- ============================================================================
-- COST_FORECASTS TABLE CONSTRAINTS
-- ============================================================================

-- Ensure predicted_cost is non-negative
ALTER TABLE cost_forecasts
ADD CONSTRAINT chk_cost_forecasts_predicted_cost_positive
CHECK (predicted_cost >= 0);

-- Ensure confidence_score is between 0 and 100
ALTER TABLE cost_forecasts
ADD CONSTRAINT chk_cost_forecasts_confidence_score_range
CHECK (confidence_score >= 0 AND confidence_score <= 100);

-- Ensure forecast_date is in the future
ALTER TABLE cost_forecasts
ADD CONSTRAINT chk_cost_forecasts_date_is_future
CHECK (forecast_date >= CURRENT_DATE);

-- Ensure upper_bound >= predicted_cost >= lower_bound
ALTER TABLE cost_forecasts
ADD CONSTRAINT chk_cost_forecasts_bounds_valid
CHECK (lower_bound <= predicted_cost AND predicted_cost <= upper_bound);

-- ============================================================================
-- ANOMALIES TABLE CONSTRAINTS
-- ============================================================================

-- Ensure severity is valid
ALTER TABLE anomalies
ADD CONSTRAINT chk_anomalies_severity_valid
CHECK (severity IN ('low', 'medium', 'high', 'critical'));

-- Ensure expected_cost is non-negative
ALTER TABLE anomalies
ADD CONSTRAINT chk_anomalies_expected_cost_positive
CHECK (expected_cost >= 0);

-- Ensure actual_cost is non-negative
ALTER TABLE anomalies
ADD CONSTRAINT chk_anomalies_actual_cost_positive
CHECK (actual_cost >= 0);

-- Ensure deviation_percentage is not null
ALTER TABLE anomalies
ADD CONSTRAINT chk_anomalies_deviation_not_null
CHECK (deviation_percentage IS NOT NULL);

-- Ensure detected_at is not in the future
ALTER TABLE anomalies
ADD CONSTRAINT chk_anomalies_detected_at_not_future
CHECK (detected_at <= NOW());

-- Ensure resolved_at is after detected_at (if resolved)
ALTER TABLE anomalies
ADD CONSTRAINT chk_anomalies_resolved_after_detected
CHECK (resolved_at IS NULL OR resolved_at >= detected_at);

-- ============================================================================
-- ALERT_RULES TABLE CONSTRAINTS
-- ============================================================================

-- Ensure name is not empty
ALTER TABLE alert_rules
ADD CONSTRAINT chk_alert_rules_name_not_empty
CHECK (name <> '' AND name IS NOT NULL);

-- Ensure threshold_value is non-negative
ALTER TABLE alert_rules
ADD CONSTRAINT chk_alert_rules_threshold_positive
CHECK (threshold_value >= 0);

-- Ensure comparison_operator is valid
ALTER TABLE alert_rules
ADD CONSTRAINT chk_alert_rules_comparison_valid
CHECK (comparison_operator IN ('>', '>=', '<', '<=', '=', '!='));

-- Ensure time_window_minutes is positive
ALTER TABLE alert_rules
ADD CONSTRAINT chk_alert_rules_time_window_positive
CHECK (time_window_minutes > 0);

-- ============================================================================
-- ALERT_NOTIFICATIONS TABLE CONSTRAINTS
-- ============================================================================

-- Ensure status is valid
ALTER TABLE alert_notifications
ADD CONSTRAINT chk_alert_notifications_status_valid
CHECK (status IN ('pending', 'sent', 'failed', 'retrying'));

-- Ensure channel is valid
ALTER TABLE alert_notifications
ADD CONSTRAINT chk_alert_notifications_channel_valid
CHECK (channel IN ('email', 'sms', 'slack', 'sns', 'webhook'));

-- Ensure sent_at is not in the future
ALTER TABLE alert_notifications
ADD CONSTRAINT chk_alert_notifications_sent_at_not_future
CHECK (sent_at IS NULL OR sent_at <= NOW());

-- ============================================================================
-- RESOURCE_USAGE_METRICS TABLE CONSTRAINTS
-- ============================================================================

-- Ensure metric_value is non-negative for CPU, memory, and storage metrics
ALTER TABLE resource_usage_metrics
ADD CONSTRAINT chk_resource_metrics_value_positive
CHECK (
  (metric_name NOT IN ('cpu_utilization', 'memory_utilization', 'disk_usage', 'network_in', 'network_out'))
  OR (metric_value >= 0)
);

-- Ensure utilization percentages are between 0 and 100
ALTER TABLE resource_usage_metrics
ADD CONSTRAINT chk_resource_metrics_utilization_range
CHECK (
  (metric_name NOT IN ('cpu_utilization', 'memory_utilization'))
  OR (metric_value >= 0 AND metric_value <= 100)
);

-- Ensure timestamp is not in the future
ALTER TABLE resource_usage_metrics
ADD CONSTRAINT chk_resource_metrics_timestamp_not_future
CHECK (timestamp <= NOW());

-- Ensure metric_name is not empty
ALTER TABLE resource_usage_metrics
ADD CONSTRAINT chk_resource_metrics_name_not_empty
CHECK (metric_name <> '' AND metric_name IS NOT NULL);

-- ============================================================================
-- USERS TABLE CONSTRAINTS
-- ============================================================================

-- Ensure email is valid format
ALTER TABLE users
ADD CONSTRAINT chk_users_email_valid
CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- Ensure username is not empty
ALTER TABLE users
ADD CONSTRAINT chk_users_username_not_empty
CHECK (username <> '' AND username IS NOT NULL);

-- Ensure password_hash is not empty
ALTER TABLE users
ADD CONSTRAINT chk_users_password_hash_not_empty
CHECK (password_hash <> '' AND password_hash IS NOT NULL);

-- Ensure role is valid
ALTER TABLE users
ADD CONSTRAINT chk_users_role_valid
CHECK (role IN ('admin', 'user', 'viewer'));

-- ============================================================================
-- ORGANIZATIONS TABLE CONSTRAINTS
-- ============================================================================

-- Ensure name is not empty
ALTER TABLE organizations
ADD CONSTRAINT chk_organizations_name_not_empty
CHECK (name <> '' AND name IS NOT NULL);

-- Ensure aws_account_id is valid (12 digits)
ALTER TABLE organizations
ADD CONSTRAINT chk_organizations_aws_account_valid
CHECK (aws_account_id ~* '^[0-9]{12}$');

-- ============================================================================
-- API_KEYS TABLE CONSTRAINTS
-- ============================================================================

-- Ensure name is not empty
ALTER TABLE api_keys
ADD CONSTRAINT chk_api_keys_name_not_empty
CHECK (name <> '' AND name IS NOT NULL);

-- Ensure key_hash is not empty
ALTER TABLE api_keys
ADD CONSTRAINT chk_api_keys_key_hash_not_empty
CHECK (key_hash <> '' AND key_hash IS NOT NULL);

-- Ensure expires_at is in the future (if set)
ALTER TABLE api_keys
ADD CONSTRAINT chk_api_keys_expires_at_future
CHECK (expires_at IS NULL OR expires_at > created_at);

-- ============================================================================
-- SESSIONS TABLE CONSTRAINTS
-- ============================================================================

-- Ensure session_token is not empty
ALTER TABLE sessions
ADD CONSTRAINT chk_sessions_token_not_empty
CHECK (session_token <> '' AND session_token IS NOT NULL);

-- Ensure expires_at is in the future
ALTER TABLE sessions
ADD CONSTRAINT chk_sessions_expires_at_future
CHECK (expires_at > created_at);

-- ============================================================================
-- NOTES ON CONSTRAINTS
-- ============================================================================

-- Performance Considerations:
-- - CHECK constraints are evaluated on INSERT and UPDATE operations
-- - They have minimal performance impact compared to triggers
-- - Constraints are enforced at the database level, providing data integrity
-- - Use partial indexes (WHERE clauses) for performance on large tables

-- To disable a constraint temporarily (for bulk operations):
-- ALTER TABLE table_name DISABLE TRIGGER ALL;
-- -- perform bulk operation
-- ALTER TABLE table_name ENABLE TRIGGER ALL;

-- To list all constraints:
-- SELECT conname, contype, conrelid::regclass AS table_name
-- FROM pg_constraint
-- WHERE connamespace = 'public'::regnamespace
-- ORDER BY conrelid::regclass::text, contype, conname;

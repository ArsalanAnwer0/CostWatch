-- Database Views for Common Queries
-- These views simplify complex queries and improve query performance

-- ============================================================================
-- COST ANALYSIS VIEWS
-- ============================================================================

-- Monthly cost aggregation by organization and service
CREATE OR REPLACE VIEW monthly_costs AS
SELECT
    organization_id,
    service_type,
    region,
    DATE_TRUNC('month', cost_date) AS month,
    SUM(unblended_cost) AS total_unblended_cost,
    SUM(blended_cost) AS total_blended_cost,
    AVG(unblended_cost) AS avg_daily_unblended_cost,
    AVG(blended_cost) AS avg_daily_blended_cost,
    COUNT(*) AS days_in_month,
    MIN(cost_date) AS first_date,
    MAX(cost_date) AS last_date
FROM cost_data
WHERE deleted_at IS NULL
GROUP BY organization_id, service_type, region, DATE_TRUNC('month', cost_date);

COMMENT ON VIEW monthly_costs IS 'Aggregated monthly costs by organization, service, and region';

-- Daily cost summary with running totals
CREATE OR REPLACE VIEW daily_cost_summary AS
SELECT
    organization_id,
    cost_date,
    SUM(unblended_cost) AS total_unblended_cost,
    SUM(blended_cost) AS total_blended_cost,
    COUNT(DISTINCT service_type) AS service_count,
    COUNT(DISTINCT region) AS region_count,
    SUM(SUM(unblended_cost)) OVER (
        PARTITION BY organization_id
        ORDER BY cost_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_unblended_cost
FROM cost_data
WHERE deleted_at IS NULL
GROUP BY organization_id, cost_date
ORDER BY organization_id, cost_date DESC;

COMMENT ON VIEW daily_cost_summary IS 'Daily cost summary with running totals per organization';

-- Top cost services by organization
CREATE OR REPLACE VIEW top_cost_services AS
WITH service_costs AS (
    SELECT
        organization_id,
        service_type,
        SUM(unblended_cost) AS total_cost,
        COUNT(*) AS record_count,
        MIN(cost_date) AS first_seen,
        MAX(cost_date) AS last_seen
    FROM cost_data
    WHERE deleted_at IS NULL
    GROUP BY organization_id, service_type
),
ranked_services AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY organization_id ORDER BY total_cost DESC) AS cost_rank
    FROM service_costs
)
SELECT
    organization_id,
    service_type,
    total_cost,
    record_count,
    first_seen,
    last_seen,
    cost_rank
FROM ranked_services
WHERE cost_rank <= 10;

COMMENT ON VIEW top_cost_services IS 'Top 10 most expensive services per organization';

-- Cost trends with month-over-month comparison
CREATE OR REPLACE VIEW cost_trends AS
WITH monthly_totals AS (
    SELECT
        organization_id,
        DATE_TRUNC('month', cost_date) AS month,
        SUM(unblended_cost) AS monthly_cost
    FROM cost_data
    WHERE deleted_at IS NULL
    GROUP BY organization_id, DATE_TRUNC('month', cost_date)
)
SELECT
    organization_id,
    month,
    monthly_cost,
    LAG(monthly_cost, 1) OVER (PARTITION BY organization_id ORDER BY month) AS previous_month_cost,
    monthly_cost - LAG(monthly_cost, 1) OVER (PARTITION BY organization_id ORDER BY month) AS cost_change,
    ROUND(
        ((monthly_cost - LAG(monthly_cost, 1) OVER (PARTITION BY organization_id ORDER BY month))
        / NULLIF(LAG(monthly_cost, 1) OVER (PARTITION BY organization_id ORDER BY month), 0) * 100)::numeric, 2
    ) AS cost_change_percentage
FROM monthly_totals
ORDER BY organization_id, month DESC;

COMMENT ON VIEW cost_trends IS 'Month-over-month cost trends with percentage changes';

-- ============================================================================
-- RESOURCE MANAGEMENT VIEWS
-- ============================================================================

-- Active resources summary
CREATE OR REPLACE VIEW active_resources AS
SELECT
    ar.id,
    ar.organization_id,
    ar.resource_id,
    ar.resource_arn,
    ar.resource_type,
    ar.region,
    ar.state,
    ar.tags,
    ar.launch_time,
    ar.last_scanned_at,
    ar.created_at,
    ar.updated_at,
    o.name AS organization_name,
    EXTRACT(EPOCH FROM (NOW() - ar.launch_time)) / 3600 AS hours_running,
    EXTRACT(EPOCH FROM (NOW() - ar.last_scanned_at)) / 3600 AS hours_since_last_scan
FROM aws_resources ar
LEFT JOIN organizations o ON ar.organization_id = o.id
WHERE ar.state = 'running'
  AND ar.deleted_at IS NULL;

COMMENT ON VIEW active_resources IS 'Currently running AWS resources with runtime metrics';

-- Resource utilization summary
CREATE OR REPLACE VIEW resource_utilization_summary AS
WITH latest_metrics AS (
    SELECT DISTINCT ON (resource_id, metric_name)
        resource_id,
        metric_name,
        metric_value,
        unit,
        timestamp
    FROM resource_usage_metrics
    ORDER BY resource_id, metric_name, timestamp DESC
)
SELECT
    ar.id,
    ar.organization_id,
    ar.resource_id,
    ar.resource_type,
    ar.region,
    ar.state,
    MAX(CASE WHEN lm.metric_name = 'cpu_utilization' THEN lm.metric_value END) AS cpu_utilization,
    MAX(CASE WHEN lm.metric_name = 'memory_utilization' THEN lm.metric_value END) AS memory_utilization,
    MAX(CASE WHEN lm.metric_name = 'disk_usage' THEN lm.metric_value END) AS disk_usage,
    MAX(CASE WHEN lm.metric_name = 'network_in' THEN lm.metric_value END) AS network_in,
    MAX(CASE WHEN lm.metric_name = 'network_out' THEN lm.metric_value END) AS network_out,
    MAX(lm.timestamp) AS last_metric_timestamp
FROM aws_resources ar
LEFT JOIN latest_metrics lm ON ar.id = lm.resource_id
WHERE ar.deleted_at IS NULL
GROUP BY ar.id, ar.organization_id, ar.resource_id, ar.resource_type, ar.region, ar.state;

COMMENT ON VIEW resource_utilization_summary IS 'Latest resource utilization metrics for all resources';

-- Underutilized resources (potential savings)
CREATE OR REPLACE VIEW underutilized_resources AS
WITH avg_utilization AS (
    SELECT
        resource_id,
        metric_name,
        AVG(metric_value) AS avg_value,
        MAX(metric_value) AS max_value,
        COUNT(*) AS sample_count
    FROM resource_usage_metrics
    WHERE timestamp >= NOW() - INTERVAL '7 days'
      AND metric_name IN ('cpu_utilization', 'memory_utilization')
    GROUP BY resource_id, metric_name
)
SELECT
    ar.id,
    ar.organization_id,
    ar.resource_id,
    ar.resource_type,
    ar.region,
    ar.state,
    ar.tags,
    MAX(CASE WHEN au.metric_name = 'cpu_utilization' THEN au.avg_value END) AS avg_cpu_utilization,
    MAX(CASE WHEN au.metric_name = 'memory_utilization' THEN au.avg_value END) AS avg_memory_utilization,
    MAX(CASE WHEN au.metric_name = 'cpu_utilization' THEN au.max_value END) AS max_cpu_utilization,
    MAX(CASE WHEN au.metric_name = 'memory_utilization' THEN au.max_value END) AS max_memory_utilization,
    ar.last_scanned_at
FROM aws_resources ar
INNER JOIN avg_utilization au ON ar.id = au.resource_id
WHERE ar.state = 'running'
  AND ar.deleted_at IS NULL
GROUP BY ar.id, ar.organization_id, ar.resource_id, ar.resource_type, ar.region, ar.state, ar.tags, ar.last_scanned_at
HAVING
    MAX(CASE WHEN au.metric_name = 'cpu_utilization' THEN au.avg_value END) < 20
    OR MAX(CASE WHEN au.metric_name = 'memory_utilization' THEN au.avg_value END) < 30;

COMMENT ON VIEW underutilized_resources IS 'Resources with low average CPU (<20%) or memory (<30%) utilization';

-- ============================================================================
-- ALERT AND ANOMALY VIEWS
-- ============================================================================

-- Active alerts summary
CREATE OR REPLACE VIEW active_alerts AS
SELECT
    a.id,
    a.organization_id,
    a.severity,
    a.service_type,
    a.resource_id,
    a.expected_cost,
    a.actual_cost,
    a.deviation_percentage,
    a.detected_at,
    a.description,
    o.name AS organization_name,
    ar.resource_arn,
    ar.resource_type,
    ar.region,
    EXTRACT(EPOCH FROM (NOW() - a.detected_at)) / 3600 AS hours_since_detected
FROM anomalies a
LEFT JOIN organizations o ON a.organization_id = o.id
LEFT JOIN aws_resources ar ON a.resource_id = ar.id
WHERE a.resolved_at IS NULL
  AND a.deleted_at IS NULL
ORDER BY a.severity DESC, a.detected_at DESC;

COMMENT ON VIEW active_alerts IS 'Currently unresolved anomalies with related resource information';

-- Alert notification history
CREATE OR REPLACE VIEW alert_notification_history AS
SELECT
    an.id,
    an.alert_id,
    a.organization_id,
    a.severity,
    an.channel,
    an.recipient,
    an.status,
    an.sent_at,
    an.error_message,
    an.created_at,
    o.name AS organization_name,
    a.service_type,
    a.description AS alert_description,
    EXTRACT(EPOCH FROM (an.sent_at - a.detected_at)) / 60 AS minutes_to_notification
FROM alert_notifications an
INNER JOIN anomalies a ON an.alert_id = a.id
LEFT JOIN organizations o ON a.organization_id = o.id
WHERE an.deleted_at IS NULL
ORDER BY an.created_at DESC;

COMMENT ON VIEW alert_notification_history IS 'Complete notification history with timing metrics';

-- Failed notifications requiring retry
CREATE OR REPLACE VIEW failed_notifications AS
SELECT
    an.id,
    an.alert_id,
    a.organization_id,
    a.severity,
    an.channel,
    an.recipient,
    an.error_message,
    an.sent_at,
    an.created_at,
    o.name AS organization_name,
    a.service_type,
    EXTRACT(EPOCH FROM (NOW() - an.created_at)) / 3600 AS hours_since_creation,
    COUNT(*) OVER (PARTITION BY an.alert_id, an.recipient) AS retry_count
FROM alert_notifications an
INNER JOIN anomalies a ON an.alert_id = a.id
LEFT JOIN organizations o ON a.organization_id = o.id
WHERE an.status = 'failed'
  AND an.deleted_at IS NULL
ORDER BY an.created_at ASC;

COMMENT ON VIEW failed_notifications IS 'Failed notifications that need to be retried';

-- ============================================================================
-- FORECASTING VIEWS
-- ============================================================================

-- Latest cost forecasts
CREATE OR REPLACE VIEW latest_cost_forecasts AS
SELECT DISTINCT ON (organization_id, forecast_date)
    cf.id,
    cf.organization_id,
    cf.forecast_date,
    cf.predicted_cost,
    cf.confidence_score,
    cf.lower_bound,
    cf.upper_bound,
    cf.model_version,
    cf.created_at,
    o.name AS organization_name
FROM cost_forecasts cf
LEFT JOIN organizations o ON cf.organization_id = o.id
WHERE cf.deleted_at IS NULL
  AND cf.forecast_date >= CURRENT_DATE
ORDER BY organization_id, forecast_date, created_at DESC;

COMMENT ON VIEW latest_cost_forecasts IS 'Most recent forecast predictions for each future date';

-- Forecast accuracy (compare predictions with actual costs)
CREATE OR REPLACE VIEW forecast_accuracy AS
SELECT
    cf.organization_id,
    cf.forecast_date,
    cf.predicted_cost,
    cd.total_actual_cost,
    cf.confidence_score,
    cf.lower_bound,
    cf.upper_bound,
    ABS(cf.predicted_cost - cd.total_actual_cost) AS absolute_error,
    ROUND(
        (ABS(cf.predicted_cost - cd.total_actual_cost) / NULLIF(cd.total_actual_cost, 0) * 100)::numeric, 2
    ) AS percentage_error,
    CASE
        WHEN cd.total_actual_cost BETWEEN cf.lower_bound AND cf.upper_bound THEN true
        ELSE false
    END AS within_confidence_interval
FROM cost_forecasts cf
LEFT JOIN (
    SELECT
        organization_id,
        cost_date,
        SUM(unblended_cost) AS total_actual_cost
    FROM cost_data
    WHERE deleted_at IS NULL
    GROUP BY organization_id, cost_date
) cd ON cf.organization_id = cd.organization_id AND cf.forecast_date = cd.cost_date
WHERE cf.forecast_date < CURRENT_DATE
  AND cf.deleted_at IS NULL
ORDER BY cf.forecast_date DESC;

COMMENT ON VIEW forecast_accuracy IS 'Historical forecast accuracy compared to actual costs';

-- ============================================================================
-- USER AND ORGANIZATION VIEWS
-- ============================================================================

-- Organization summary with user count
CREATE OR REPLACE VIEW organization_summary AS
SELECT
    o.id,
    o.name,
    o.aws_account_id,
    o.created_at,
    o.updated_at,
    COUNT(DISTINCT u.id) AS user_count,
    COUNT(DISTINCT ar.id) FILTER (WHERE ar.state = 'running' AND ar.deleted_at IS NULL) AS active_resource_count,
    COUNT(DISTINCT a.id) FILTER (WHERE a.resolved_at IS NULL AND a.deleted_at IS NULL) AS active_anomaly_count,
    SUM(cd.total_cost) AS total_cost_last_30_days
FROM organizations o
LEFT JOIN users u ON o.id = u.organization_id AND u.deleted_at IS NULL
LEFT JOIN aws_resources ar ON o.id = ar.organization_id
LEFT JOIN anomalies a ON o.id = a.organization_id
LEFT JOIN (
    SELECT
        organization_id,
        SUM(unblended_cost) AS total_cost
    FROM cost_data
    WHERE cost_date >= CURRENT_DATE - INTERVAL '30 days'
      AND deleted_at IS NULL
    GROUP BY organization_id
) cd ON o.id = cd.organization_id
WHERE o.deleted_at IS NULL
GROUP BY o.id, o.name, o.aws_account_id, o.created_at, o.updated_at, cd.total_cost;

COMMENT ON VIEW organization_summary IS 'Organization overview with key metrics';

-- Active user sessions
CREATE OR REPLACE VIEW active_user_sessions AS
SELECT
    s.id,
    s.user_id,
    u.username,
    u.email,
    u.organization_id,
    o.name AS organization_name,
    s.session_token,
    s.expires_at,
    s.created_at,
    s.updated_at,
    EXTRACT(EPOCH FROM (s.expires_at - NOW())) / 60 AS minutes_until_expiry
FROM sessions s
INNER JOIN users u ON s.user_id = u.id
LEFT JOIN organizations o ON u.organization_id = o.id
WHERE s.expires_at > NOW()
  AND s.deleted_at IS NULL
  AND u.deleted_at IS NULL
ORDER BY s.created_at DESC;

COMMENT ON VIEW active_user_sessions IS 'Currently active user sessions';

-- ============================================================================
-- VIEW USAGE NOTES
-- ============================================================================

-- To refresh a materialized view (if converted to materialized):
-- REFRESH MATERIALIZED VIEW CONCURRENTLY view_name;

-- To check view dependencies:
-- SELECT * FROM pg_views WHERE schemaname = 'public';

-- To see view definition:
-- \d+ view_name

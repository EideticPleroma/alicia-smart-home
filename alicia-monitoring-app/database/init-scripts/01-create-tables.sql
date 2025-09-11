-- Alicia Monitoring App Database Schema
-- Create tables for monitoring data storage

-- Health status table
CREATE TABLE IF NOT EXISTS health_status (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    service_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    response_time_ms INTEGER,
    error_message TEXT,
    metadata JSONB
);

-- Test results table
CREATE TABLE IF NOT EXISTS test_results (
    id SERIAL PRIMARY KEY,
    test_id VARCHAR(100) UNIQUE NOT NULL,
    test_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    input_text TEXT,
    output_text TEXT,
    error_message TEXT,
    duration_ms INTEGER,
    metrics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Configuration history table
CREATE TABLE IF NOT EXISTS config_history (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    environment VARCHAR(50) NOT NULL,
    config_data JSONB NOT NULL,
    updated_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Metrics aggregation table
CREATE TABLE IF NOT EXISTS metrics_aggregated (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    date_hour TIMESTAMP WITH TIME ZONE NOT NULL,
    avg_response_time_ms DECIMAL(10,2),
    min_response_time_ms INTEGER,
    max_response_time_ms INTEGER,
    total_checks INTEGER,
    successful_checks INTEGER,
    error_checks INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    service_name VARCHAR(100),
    message TEXT NOT NULL,
    metadata JSONB,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_health_status_timestamp ON health_status(timestamp);
CREATE INDEX IF NOT EXISTS idx_health_status_service ON health_status(service_name);
CREATE INDEX IF NOT EXISTS idx_test_results_created_at ON test_results(created_at);
CREATE INDEX IF NOT EXISTS idx_test_results_test_type ON test_results(test_type);
CREATE INDEX IF NOT EXISTS idx_config_history_service_env ON config_history(service_name, environment);
CREATE INDEX IF NOT EXISTS idx_metrics_aggregated_service_date ON metrics_aggregated(service_name, date_hour);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at);
CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON alerts(acknowledged);


-- Create staging database
CREATE DATABASE IF NOT EXISTS staging;

-- Create staging tables
CREATE TABLE IF NOT EXISTS staging.mines (
    mine_id UInt32,
    mine_code String,
    mine_name String,
    location String,
    operational_status String
) ENGINE = MergeTree()
ORDER BY mine_id;

CREATE TABLE IF NOT EXISTS staging.production_logs (
    log_id UInt32,
    date Date,
    mine_id UInt32,
    shift String,
    tons_extracted Decimal64(2),
    quality_grade Decimal32(1)
) ENGINE = MergeTree()
ORDER BY (date, mine_id);

CREATE TABLE IF NOT EXISTS staging.equipment_sensors (
    timestamp DateTime,
    equipment_id String,
    status String,
    fuel_consumption Float64,
    maintenance_alert Boolean
) ENGINE = MergeTree()
ORDER BY (timestamp, equipment_id);
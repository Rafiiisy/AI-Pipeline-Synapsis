-- DWH Star Schema
-- This schema defines the structure for the data warehouse,
-- including dimension and fact tables.

CREATE DATABASE IF NOT EXISTS dwh;

-- Dimension Tables
CREATE TABLE IF NOT EXISTS dwh.dim_date (
    date_id Date,
    year UInt16,
    month UInt8,
    day UInt8,
    day_of_week UInt8,
    quarter UInt8,
    is_weekend UInt8
) ENGINE = MergeTree()
ORDER BY date_id;

CREATE TABLE IF NOT EXISTS dwh.dim_mine (
    mine_id String,
    location String,
    type String,
    opened_date Date
) ENGINE = MergeTree()
PRIMARY KEY mine_id;

CREATE TABLE IF NOT EXISTS dwh.dim_equipment (
    equipment_id String,
    equipment_type String,
    last_maintenance_date DateTime
) ENGINE = MergeTree()
PRIMARY KEY equipment_id;

CREATE TABLE IF NOT EXISTS dwh.dim_location (
    location_id UInt64,
    location String,
    latitude Float64,
    longitude Float64,
    elevation Float64,
    timezone String,
    utc_offset_seconds Int32
) ENGINE = MergeTree()
PRIMARY KEY location_id;

-- Fact Tables
CREATE TABLE IF NOT EXISTS dwh.fact_daily_production (
    date_id Date,
    mine_id String,
    location_id UInt64,
    total_production_daily Float64,
    average_quality_grade Float32,
    equipment_utilization Float32,
    fuel_efficiency Float32,
    temperature_2m_mean Float32,
    rainfall_mm Float32
) ENGINE = MergeTree()
ORDER BY (date_id, mine_id);

CREATE TABLE IF NOT EXISTS dwh.fact_equipment_metrics (
    date_id Date,
    equipment_id String,
    mine_id String,
    location_id UInt64,
    total_operational_hours UInt8,
    total_maintenance_hours UInt8,
    total_fuel_consumption Float64,
    maintenance_alerts UInt8
) ENGINE = MergeTree()
ORDER BY (date_id, equipment_id);
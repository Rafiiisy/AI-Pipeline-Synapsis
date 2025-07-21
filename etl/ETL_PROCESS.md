# ETL Process Documentation

This document explains the ETL (Extract, Transform, Load) pipeline and all jobs/scripts in the `etl/` folder for the Synapsis Mining Data Project.

---

## Overview
The ETL pipeline automates the flow of data from raw sources (SQL, CSV, API) into a data warehouse (DWH) for analytics and dashboarding. It ensures data quality through validation and supports monitoring for reliability.

---

## ETL Pipeline Steps

### 1. **Extraction**
- **Production Logs:** Extracted from the `staging.production_logs` SQL table.
- **Equipment Sensors:** Read from `equipment_sensors.csv` (IoT sensor data).
- **Weather Data:** Fetched from the Open-Meteo API for Berau, Kalimantan, Indonesia, retrieving daily mean temperature and precipitation.

### 2. **Transformation**
- **Production Data:** Aggregated by day and mine to compute total production and average quality.
- **Equipment Data:** Aggregated by day to compute operational hours and fuel consumption.
- **Weather Data:** Merged by date with production and equipment data.
- **Metrics Calculated:**
  - `total_production_daily`: Total tons mined per day
  - `average_quality_grade`: Average coal quality per day
  - `equipment_utilization`: % of time equipment is active per day
  - `fuel_efficiency`: Tons mined per unit of fuel
  - `weather_impact`: Correlation between rainfall and production (for analysis)

### 3. **Validation**
- Checks for negative production values, out-of-range utilization, and missing weather data.
- Anomalies are logged for review.

### 4. **Loading**
- Transformed and validated data is loaded into the DWH table `dwh.fact_daily_production`.

---

## ETL Folder Job Descriptions

### - `etl.py`
Main ETL script. Orchestrates extraction, transformation, validation, and loading. Handles logging and error management.

### - `validation.py`
Contains the `DataValidator` class. Implements data quality checks, anomaly detection, and logging of validation results.

### - `monitor_etl.py`
Script to monitor ETL runs, check logs, and alert on failures or anomalies.

### - `test_scrape_weather.py`
Test script for weather data extraction. Used to validate API integration and data structure before running the main ETL.

### - `crontab`
Defines the schedule for automated ETL runs (e.g., daily at a set time).

### - `Dockerfile`
Defines the Docker image for the ETL environment, ensuring reproducibility and easy deployment.

### - `requirements.txt`
Lists Python dependencies for the ETL scripts.

### - `logs/`
Stores log files for each ETL run, including both process and validation logs.

---

## ETL Process Flow Diagram

```mermaid
graph TD
    A[Extract Production Logs (SQL)] --> D[Transform & Merge]
    B[Extract Equipment Sensors (CSV)] --> D
    C[Fetch Weather Data (API)] --> D
    D --> E[Validate Data]
    E --> F[Load to DWH]
    F --> G[Monitor & Log]
```

---

## Notes
- The ETL process is automated and can be scheduled via cron or other orchestrators.
- All logs are stored in `etl/logs/` for traceability.
- The pipeline is containerized for easy deployment and reproducibility. 
# Coal Mining Analytics Dashboard Documentation

This document provides a simple, focused guide for creating the dashboard in Metabase.
---

## Dashboard Setup Instructions

### **Step 1: Access Metabase**
- Open [http://localhost:3001](http://localhost:3001) in your browser
- Login with credentials: `admin` / `admin`

### **Step 2: Create New Dashboard**
1. Click **"New"** → **"Dashboard"**
2. Name it: **"Coal Mining Analytics Dashboard"**
3. Click **"Create"**

### **Step 3: Create the Charts**

#### **Chart 1: Daily Production Trends (Line Chart)**
1. Click **"New question"**
2. Select **"Native query"**
3. Choose **Clickhouse** database
4. Enter this SQL:
```sql
SELECT 
    date_id as "Date",
    total_production_daily as "Daily Production (Tons)"
FROM dwh.fact_daily_production
WHERE date_id >= today() - 30
ORDER BY date_id
```
5. Click **"Save"** → Name: **"Daily Production Trends"**
6. Set visualization to **"Line"**
7. Click **"Add to dashboard"** → Select your dashboard

#### **Chart 2: Average Quality Grade by Mine (Bar Chart)**
1. Click **"New question"**
2. Select **"Native query"**
3. Choose **Clickhouse** database
4. Enter this SQL:
```sql
SELECT 
    mine_id as "Mine",
    AVG(average_quality_grade) as "Average Quality Grade"
FROM dwh.fact_daily_production
GROUP BY mine_id
ORDER BY "Average Quality Grade" DESC
```
5. Click **"Save"** → Name: **"Average Quality Grade by Mine"**
6. Set visualization to **"Bar"**
7. Click **"Add to dashboard"** → Select your dashboard

#### **Chart 3: Rainfall vs Production (Scatter Plot)**
1. Click **"New question"**
2. Select **"Native query"**
3. Choose **Clickhouse** database
4. Enter this SQL:
```sql
SELECT 
    rainfall_mm as "Daily Rainfall (mm)",
    total_production_daily as "Daily Production (Tons)"
FROM dwh.fact_daily_production
WHERE rainfall_mm IS NOT NULL
ORDER BY rainfall_mm
```
5. Click **"Save"** → Name: **"Rainfall Impact on Production"**
6. Set visualization to **"Scatter"**
7. Click **"Add to dashboard"** → Select your dashboard

### **Step 4: Create KPI Cards**

#### **KPI 1: Total Production (Last 30 Days)**
1. Click **"New question"**
2. Select **"Native query"**
3. Choose **Clickhouse** database
4. Enter this SQL:
```sql
SELECT 
    SUM(total_production_daily) as "Total Production (Tons)"
FROM dwh.fact_daily_production
WHERE date_id >= today() - 30
```
5. Click **"Save"** → Name: **"Total Production (30 Days)"**
6. Set visualization to **"Number"**
7. Click **"Add to dashboard"** → Select your dashboard

#### **KPI 2: Average Daily Production**
1. Click **"New question"**
2. Select **"Native query"**
3. Choose **Clickhouse** database
4. Enter this SQL:
```sql
SELECT 
    AVG(total_production_daily) as "Average Daily Production (Tons)"
FROM dwh.fact_daily_production
WHERE date_id >= today() - 30
```
5. Click **"Save"** → Name: **"Average Daily Production"**
6. Set visualization to **"Number"**
7. Click **"Add to dashboard"** → Select your dashboard

#### **KPI 3: Average Equipment Utilization**
1. Click **"New question"**
2. Select **"Native query"**
3. Choose **Clickhouse** database
4. Enter this SQL:
```sql
SELECT 
    AVG(equipment_utilization) as "Average Equipment Utilization (%)"
FROM dwh.fact_daily_production
WHERE date_id >= today() - 30
```
5. Click **"Save"** → Name: **"Average Equipment Utilization"**
6. Set visualization to **"Number"**
7. Click **"Add to dashboard"** → Select your dashboard

#### **KPI 4: Average Quality Grade**
1. Click **"New question"**
2. Select **"Native query"**
3. Choose **Clickhouse** database
4. Enter this SQL:
```sql
SELECT 
    AVG(average_quality_grade) as "Average Quality Grade"
FROM dwh.fact_daily_production
WHERE date_id >= today() - 30
```
5. Click **"Save"** → Name: **"Average Quality Grade"**
6. Set visualization to **"Number"**
7. Click **"Add to dashboard"** → Select your dashboard

### **Step 5: Create Additional Insightful Charts**

#### **Chart 4: Equipment Utilization Trends (Line Chart)**
1. Click **"New question"**
2. Select **"Native query"**
3. Choose **Clickhouse** database
4. Enter this SQL:
```sql
SELECT 
    date_id as "Date",
    AVG(equipment_utilization) as "Equipment Utilization (%)"
FROM dwh.fact_daily_production
WHERE date_id >= today() - 30
GROUP BY date_id
ORDER BY date_id
```
5. Click **"Save"** → Name: **"Equipment Utilization Trends"**
6. Set visualization to **"Line"**
7. Click **"Add to dashboard"** → Select your dashboard

#### **Chart 5: Weather Impact Summary (Bar Chart)**
1. Click **"New question"**
2. Select **"Native query"**
3. Choose **Clickhouse** database
4. Enter this SQL:
```sql
SELECT 
    CASE 
        WHEN rainfall_mm > 1.0 THEN 'Rainy Days (>1mm)'
        ELSE 'Non-Rainy Days (≤1mm)'
    END as "Weather Condition",
    AVG(total_production_daily) as "Average Daily Production (Tons)"
FROM dwh.fact_daily_production
WHERE rainfall_mm IS NOT NULL
GROUP BY "Weather Condition"
ORDER BY "Average Daily Production (Tons)" DESC
```
5. Click **"Save"** → Name: **"Weather Impact Summary"**
6. Set visualization to **"Bar"**
7. Click **"Add to dashboard"** → Select your dashboard

#### **Chart 6: Maintenance Alerts Trend (Line Chart)**
1. Click **"New question"**
2. Select **"Native query"**
3. Choose **Clickhouse** database
4. Enter this SQL:
```sql
SELECT 
    date_id as "Date",
    SUM(maintenance_alerts) as "Total Maintenance Alerts"
FROM dwh.fact_equipment_metrics
WHERE date_id >= today() - 30
GROUP BY date_id
ORDER BY date_id
```
5. Click **"Save"** → Name: **"Maintenance Alerts Trend"**
6. Set visualization to **"Line"**
7. Click **"Add to dashboard"** → Select your dashboard
---

## Data Source Information

### **Primary Tables**

#### **`dwh.fact_daily_production`** - Main production metrics
| Column | Description | Data Type |
|--------|-------------|-----------|
| `date_id` | Date of production | Date |
| `mine_id` | Mine identifier | String |
| `location_id` | Location reference | UInt64 |
| `total_production_daily` | Daily coal production in tons | Float64 |
| `average_quality_grade` | Average coal quality grade | Float32 |
| `equipment_utilization` | Equipment utilization percentage | Float32 |
| `fuel_efficiency` | Fuel efficiency (tons per liter) | Float32 |
| `temperature_2m_mean` | Average daily temperature (°C) | Float32 |
| `rainfall_mm` | Daily rainfall in millimeters | Float32 |

#### **`dwh.fact_equipment_metrics`** - Equipment performance data
| Column | Description | Data Type |
|--------|-------------|-----------|
| `date_id` | Date of metrics | Date |
| `equipment_id` | Equipment identifier | String |
| `mine_id` | Mine identifier | String |
| `location_id` | Location reference | UInt64 |
| `total_operational_hours` | Total operational hours | UInt8 |
| `total_maintenance_hours` | Total maintenance hours | UInt8 |
| `total_fuel_consumption` | Total fuel consumption | Float64 |
| `maintenance_alerts` | Number of maintenance alerts | UInt8 |

### **Data Availability**
- Data is populated after running the ETL pipeline
- Updates daily when ETL runs
- Historical data covers multiple months
- Weather data sourced from Open-Meteo API for Berau, Kalimantan, Indonesia

---

## Business Value & Insights

### **Charts**

#### **Chart 1: Daily Production Trends**
- **Purpose**: Monitor daily production performance
- **Insights**: Identify trends, detect anomalies, track operational efficiency
- **Action**: Alert on production drops, plan resource allocation

#### **Chart 2: Average Quality Grade by Mine**
- **Purpose**: Compare coal quality across different mines
- **Insights**: Identify quality issues, ensure standards compliance
- **Action**: Focus improvement efforts on underperforming mines

#### **Chart 3: Rainfall vs Production**
- **Purpose**: Analyze weather impact on mining operations
- **Insights**: Understand seasonal patterns, plan for weather contingencies
- **Action**: Optimize operations during adverse weather conditions

### **KPI Metrics**

#### **KPI 1: Total Production (Last 30 Days)**
- **Purpose**: Monitor overall production performance
- **Insights**: Track total output, compare with targets
- **Action**: Assess production goals achievement

#### **KPI 2: Average Daily Production**
- **Purpose**: Monitor daily production consistency
- **Insights**: Identify production stability, detect trends
- **Action**: Plan resource allocation, set daily targets

#### **KPI 3: Average Equipment Utilization**
- **Purpose**: Monitor equipment efficiency
- **Insights**: Track operational efficiency, identify optimization opportunities
- **Action**: Improve equipment planning, reduce downtime

#### **KPI 4: Average Quality Grade**
- **Purpose**: Monitor product quality consistency
- **Insights**: Track quality standards, identify quality trends
- **Action**: Maintain quality standards, focus improvement efforts

### **Additional Insightful Charts**

#### **Chart 4: Equipment Utilization Trends**
- **Purpose**: Monitor equipment efficiency and operational planning
- **Insights**: Identify equipment downtime patterns, optimize maintenance schedules
- **Action**: Improve operational planning, reduce unplanned downtime

#### **Chart 5: Weather Impact Summary**
- **Purpose**: Quantify weather impact on production performance
- **Insights**: Understand weather-related production patterns, plan for weather contingencies
- **Action**: Optimize operations during adverse weather, justify weather-related decisions

#### **Chart 6: Maintenance Alerts Trend**
- **Purpose**: Track maintenance requirements and planning
- **Insights**: Identify maintenance patterns, optimize maintenance schedules
- **Action**: Reduce unplanned downtime, improve equipment reliability

---

## Technical Notes

### **Database Connection**
- **Host**: `clickhouse`
- **Port**: `8123`
- **Database**: `dwh`
- **Username**: `admin`
- **Password**: `admin`

### **Query Performance**
- All queries use indexed columns for optimal performance
- Data is pre-aggregated in the fact table
- Queries are optimized for Clickhouse columnar storage

### **Data Refresh**
- Dashboard data refreshes automatically when accessed
- ETL runs daily to update the underlying data
- No manual refresh required

---

## Troubleshooting

### **Common Issues**:
1. **No data displayed**: Ensure ETL has been run and data exists in `dwh.fact_daily_production`
2. **Connection errors**: Verify Clickhouse is running and accessible
3. **Empty charts**: Check that the date range contains data

### **Verification Steps**:
1. Run: `docker-compose exec clickhouse clickhouse-client --query "SELECT COUNT(*) FROM dwh.fact_daily_production"`
2. Should return a number > 0
3. If 0, run the ETL: `docker-compose run --rm etl python /app/etl/etl.py`

# Coal Mining Analytics Dashboard Documentation

This document provides a comprehensive overview of the Coal Mining Analytics Dashboard created in Metabase, including detailed explanations of each chart, their business value, and technical implementation.

---

## Dashboard Overview

**Dashboard Name**: Coal Mining Analytics Dashboard  
**Purpose**: Monitor and analyze coal mining operations performance, quality metrics, and weather impact  
**Target Users**: Mining operations managers, data analysts, and stakeholders  
**Update Frequency**: Daily (after ETL runs)

---

## Dashboard Sections

### **1. Production Overview Section**

#### **Chart 1: Daily Production Trends**
- **Chart Type**: Line Chart
- **Data Source**: `dwh.fact_daily_production`
- **X-Axis**: Date (`date_id`)
- **Y-Axis**: Daily Production (`total_production_daily`)
- **Time Range**: Last 30 days (configurable)
- **Display Name**: "Daily Coal Production (Tons)"

**Business Value**:
- Track daily production performance
- Identify production trends and patterns
- Monitor operational efficiency over time
- Detect anomalies or production drops

**Technical Details**:
```sql
SELECT 
    date_id as "Date",
    total_production_daily as "Daily Production (Tons)"
FROM dwh.fact_daily_production
WHERE date_id >= today() - 30
ORDER BY date_id
```

#### **Chart 2: Production by Mine**
- **Chart Type**: Bar Chart
- **Data Source**: `dwh.fact_daily_production`
- **X-Axis**: Mine (`mine_id`)
- **Y-Axis**: Total Production (sum of `total_production_daily`)
- **Display Name**: "Total Production by Mine"

**Business Value**:
- Compare performance across different mines
- Identify high-performing and underperforming mines
- Allocate resources based on production capacity
- Track mine-specific trends

---

### **2. Quality Metrics Section**

#### **Chart 3: Average Quality Grade by Mine**
- **Chart Type**: Bar Chart
- **Data Source**: `dwh.fact_daily_production`
- **X-Axis**: Mine (`mine_id`)
- **Y-Axis**: Average Quality Grade (`average_quality_grade`)
- **Display Name**: "Average Coal Quality Grade by Mine"

**Business Value**:
- Monitor coal quality across different mines
- Ensure quality standards are maintained
- Identify quality issues early
- Support pricing decisions based on quality

#### **Chart 4: Quality Trends Over Time**
- **Chart Type**: Line Chart
- **Data Source**: `dwh.fact_daily_production`
- **X-Axis**: Date (`date_id`)
- **Y-Axis**: Average Quality Grade (`average_quality_grade`)
- **Display Name**: "Coal Quality Trends"

**Business Value**:
- Track quality consistency over time
- Identify seasonal quality variations
- Monitor quality improvement initiatives
- Alert on quality degradation

---

### **3. Equipment Performance Section**

#### **Chart 5: Equipment Utilization Trends**
- **Chart Type**: Line Chart
- **Data Source**: `dwh.fact_daily_production`
- **X-Axis**: Date (`date_id`)
- **Y-Axis**: Equipment Utilization (`equipment_utilization`)
- **Display Name**: "Equipment Utilization (%)"

**Business Value**:
- Monitor equipment efficiency
- Identify equipment downtime patterns
- Optimize maintenance schedules
- Improve operational planning

#### **Chart 6: Fuel Efficiency Analysis**
- **Chart Type**: Line Chart
- **Data Source**: `dwh.fact_daily_production`
- **X-Axis**: Date (`date_id`)
- **Y-Axis**: Fuel Efficiency (`fuel_efficiency`)
- **Display Name**: "Fuel Efficiency (Tons/Liter)"

**Business Value**:
- Track fuel consumption efficiency
- Identify cost optimization opportunities
- Monitor equipment performance
- Support sustainability initiatives

---

### **4. Weather Impact Analysis Section**

#### **Chart 7: Rainfall vs Production Scatter Plot**
- **Chart Type**: Scatter Plot
- **Data Source**: `dwh.fact_daily_production`
- **X-Axis**: Daily Rainfall (`precipitation_sum` in mm)
- **Y-Axis**: Daily Production (`total_production_daily`)
- **Display Name**: "Rainfall Impact on Production"

**Business Value**:
- Analyze weather impact on operations
- Plan production based on weather forecasts
- Understand seasonal production patterns
- Optimize operations during adverse weather

**Technical Note**: 
- `precipitation_sum` represents daily rainfall in millimeters (mm)
- This matches the challenge requirement for `rainfall_mm`
- Data sourced from Open-Meteo API for Berau, Kalimantan, Indonesia

#### **Chart 8: Weather Impact Summary**
- **Chart Type**: Bar Chart
- **Data Source**: Custom query using `dwh.weather_impact_analysis` view
- **X-Axis**: Day Type (Rainy/Non-Rainy)
- **Y-Axis**: Average Daily Production
- **Display Name**: "Production: Rainy vs Non-Rainy Days"

**Business Value**:
- Quantify weather impact on production
- Support operational planning
- Justify weather-related operational decisions
- Plan for weather contingencies

---

### **5. Equipment Metrics Section**

#### **Chart 9: Equipment Performance by Equipment ID**
- **Chart Type**: Bar Chart
- **Data Source**: `dwh.fact_equipment_metrics`
- **X-Axis**: Equipment (`equipment_id`)
- **Y-Axis**: Operational Hours (`total_operational_hours`)
- **Display Name**: "Equipment Operational Hours"

**Business Value**:
- Monitor individual equipment performance
- Identify equipment requiring maintenance
- Optimize equipment allocation
- Track equipment utilization

#### **Chart 10: Maintenance Alerts Trend**
- **Chart Type**: Line Chart
- **Data Source**: `dwh.fact_equipment_metrics`
- **X-Axis**: Date (`date_id`)
- **Y-Axis**: Maintenance Alerts (`maintenance_alerts`)
- **Display Name**: "Maintenance Alerts Over Time"

**Business Value**:
- Track maintenance requirements
- Plan preventive maintenance
- Reduce unplanned downtime
- Optimize maintenance schedules

---

## Dashboard Filters

### **Global Filters**:
1. **Date Range**: Filter all charts by date period
2. **Mine Selection**: Filter by specific mines
3. **Equipment Selection**: Filter by specific equipment
4. **Weather Conditions**: Filter by rainy/non-rainy days

### **Filter Implementation**:
```sql
-- Example: Date Range Filter
WHERE date_id BETWEEN {{start_date}} AND {{end_date}}

-- Example: Mine Filter
WHERE mine_id IN ({{selected_mines}})

-- Example: Weather Filter
WHERE CASE 
    WHEN precipitation_sum > 1.0 THEN 'Rainy'
    ELSE 'Non-Rainy'
END = {{weather_condition}}
```

---

## Key Performance Indicators (KPIs)

### **Production KPIs**:
- **Daily Production Target**: Track against production goals
- **Production Efficiency**: Compare actual vs planned production
- **Quality Compliance**: Monitor quality standards adherence

### **Operational KPIs**:
- **Equipment Utilization Rate**: Target > 80%
- **Fuel Efficiency**: Monitor cost per ton
- **Maintenance Response Time**: Track maintenance efficiency

### **Weather KPIs**:
- **Weather Impact Score**: Quantify weather effect on production
- **Rainy Day Performance**: Compare production during adverse weather

---

## Dashboard Refresh Schedule

- **Data Refresh**: Daily after ETL completion
- **Chart Refresh**: Real-time when dashboard is accessed
- **Alert Thresholds**: Set for critical metrics

---

## Technical Implementation

### **Data Sources**:
- **Primary**: `dwh.fact_daily_production`
- **Secondary**: `dwh.fact_equipment_metrics`
- **Views**: `dwh.daily_summary_metrics`, `dwh.weather_impact_analysis`

### **Performance Optimization**:
- Use indexed columns for filtering
- Implement query caching
- Optimize chart rendering

### **Access Control**:
- Role-based access to different dashboard sections
- Data-level security based on user permissions

---

## Future Enhancements

### **Planned Additions**:
1. **Predictive Analytics**: Production forecasting
2. **Real-time Alerts**: Automated notifications for anomalies
3. **Mobile Dashboard**: Responsive design for field operations
4. **Drill-down Capabilities**: Detailed analysis views

### **Advanced Analytics**:
1. **Machine Learning Integration**: Predictive maintenance
2. **Cost Analysis**: Operational cost tracking
3. **Sustainability Metrics**: Environmental impact monitoring

---

## Troubleshooting

### **Common Issues**:
1. **No Data Displayed**: Check ETL completion and data freshness
2. **Slow Loading**: Verify database performance and query optimization
3. **Incorrect Values**: Validate data transformation logic

### **Support Contacts**:
- **Technical Issues**: Data Engineering Team
- **Business Questions**: Operations Management
- **Dashboard Access**: IT Support

---

**Last Updated**: [Current Date]  
**Dashboard Version**: 1.0  
**Documentation Version**: 1.0 
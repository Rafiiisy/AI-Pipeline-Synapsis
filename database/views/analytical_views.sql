-- This file creates analytical views on top of the DWH tables
-- to generate the specific metrics required for the project dashboard.

-- View 1: Daily Summary Metrics
-- This view aggregates key performance indicators on a daily basis,
-- covering total production, average quality, equipment utilization, and fuel efficiency.
CREATE OR REPLACE VIEW dwh.daily_summary_metrics AS
SELECT
    date_id,
    sum(total_production_daily) AS total_production_daily,
    avg(average_quality_grade) AS average_quality_grade_daily,
    avg(equipment_utilization) AS average_equipment_utilization,
    avg(fuel_efficiency) AS average_fuel_efficiency
FROM dwh.fact_daily_production
GROUP BY date_id
ORDER BY date_id;


-- View 2: Weather Impact Analysis
-- This view is designed to analyze the relationship between rainfall and production.
-- It categorizes days into 'Rainy' and 'Non-Rainy' to compare production levels
-- and also calculates the Pearson correlation coefficient between daily rainfall and production.
CREATE OR REPLACE VIEW dwh.weather_impact_analysis AS
WITH daily_aggregated_data AS (
    SELECT
        date_id,
        sum(total_production_daily) AS total_production_per_day,
        max(precipitation_sum) AS precipitation_sum_per_day
    FROM dwh.fact_daily_production
    GROUP BY date_id
)
SELECT
    CASE
        WHEN precipitation_sum_per_day > 1.0 THEN 'Rainy Day'
        ELSE 'Non-Rainy Day'
    END AS day_type,
    avg(total_production_per_day) AS average_daily_production,
    corr(precipitation_sum_per_day, total_production_per_day) AS rainfall_production_correlation
FROM daily_aggregated_data
GROUP BY day_type; 
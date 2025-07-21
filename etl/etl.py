import pandas as pd
import clickhouse_connect
import logging
from datetime import datetime
from pathlib import Path
import os
import requests
from validation import DataValidator

def setup_logging(run_id):
    """Set up logging for the ETL process."""
    log_dir = Path(f'etl/logs/run_{run_id}')
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Set up main logger
    logger = logging.getLogger('etl')
    file_handler = logging.FileHandler(log_dir / 'etl.log')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)
    
    return logger

def extract_data(client, logger):
    """Extract data from staging tables."""
    logger.info("Starting data extraction from staging tables...")
    
    try:
        production_data = client.query_df("""
            SELECT * FROM staging.production_logs
        """)
        equipment_data = client.query_df("""
            SELECT * FROM staging.equipment_sensors
        """)
        mines_data = client.query_df("""
            SELECT * FROM staging.mines
        """)
        logger.info("Data extraction completed successfully")
        return production_data, equipment_data, mines_data
    except Exception as e:
        logger.error(f"Error during data extraction: {str(e)}")
        raise

def fetch_weather_data(start_date, end_date, logger):
    """Fetch historical weather data from Open-Meteo API."""
    logger.info(f'Fetching historical weather data from {start_date} to {end_date}')
    base_url = "https://archive-api.open-meteo.com/v1/archive"
    
    params = {
        'latitude': 2.0167,
        'longitude': 117.3000,
        'daily': 'temperature_2m_mean,precipitation_sum',
        'timezone': 'Asia/Jakarta',
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d')
    }
    
    try:
        resp = requests.get(base_url, params=params)
        if resp.status_code == 200:
            logger.info("Successfully fetched weather data.")
            weather_data = resp.json()['daily']
            weather_df = pd.DataFrame(weather_data)
            weather_df = weather_df.rename(columns={'time': 'date_id'})
            weather_df['date_id'] = pd.to_datetime(weather_df['date_id']).dt.date
            return weather_df
        else:
            logger.error(f"Failed to fetch weather data: HTTP {resp.status_code} - {resp.text}")
            return pd.DataFrame()
    except Exception as e:
        logger.error(f"An exception occurred while fetching weather data: {e}")
        return pd.DataFrame()

def transform_data(production_data, equipment_data, weather_data, validator, logger):
    """Transform and validate the extracted data."""
    logger.info("Starting data transformation and validation...")
    
    try:
        # Rename 'date' column to 'date_id' for consistency
        production_data = production_data.rename(columns={'date': 'date_id'})
        production_data['date_id'] = pd.to_datetime(production_data['date_id']).dt.date

        # Aggregate production data by day and mine
        daily_production_data = production_data.groupby(['date_id', 'mine_id']).agg(
            total_production_daily=('tons_extracted', 'sum'),
            average_quality_grade=('quality_grade', 'mean')
        ).reset_index()

        # Cast decimal types to float for calculations
        daily_production_data['total_production_daily'] = daily_production_data['total_production_daily'].astype(float)
        daily_production_data['average_quality_grade'] = daily_production_data['average_quality_grade'].astype(float)

        # Aggregate sensor data by day (since it has no mine_id)
        equipment_data['date_id'] = pd.to_datetime(equipment_data['timestamp']).dt.date
        daily_equipment_data = equipment_data.groupby(['date_id']).agg(
            operational_hours=('status', lambda s: (s == 'active').sum()),
            fuel_consumption=('fuel_consumption', 'sum')
        ).reset_index()

        # Merge production, equipment, and weather data
        merged_data = pd.merge(
            daily_production_data,
            daily_equipment_data,
            on=['date_id'],
            how='left'
        )
        
        if not weather_data.empty:
            merged_data = pd.merge(
                merged_data,
                weather_data,
                on='date_id',
                how='left'
            )
        
        # Calculate metrics
        transformed_data = merged_data.copy()
        transformed_data['equipment_utilization'] = (
            transformed_data['operational_hours'].fillna(0) / 24 * 100
        )
        transformed_data['fuel_efficiency'] = (
            transformed_data['total_production_daily'] / 
            transformed_data['fuel_consumption'].replace(0, 1).fillna(1)
        )
        
        # Validate the transformed data
        transformed_data = validator.validate_production_data(transformed_data)
        transformed_data = validator.validate_equipment_utilization(transformed_data)
        validator.validate_weather_data(transformed_data, weather_data)
        
        # Log validation summary
        validator.log_validation_summary()
        
        logger.info("Data transformation and validation completed")
        return transformed_data
    except Exception as e:
        logger.error(f"Error during data transformation: {str(e)}")
        raise

def load_to_dwh(client, transformed_data, logger):
    """Load transformed data into the data warehouse."""
    logger.info("Starting data load to DWH...")
    
    try:
        # Define columns and their types for loading
        columns_to_load = [
            'date_id', 'mine_id', 'total_production_daily',
            'equipment_utilization', 'fuel_efficiency',
            'average_quality_grade', 'temperature_2m_mean', 
            'precipitation_sum'
        ]

        # Ensure all columns exist, fill missing with 0
        for col in columns_to_load:
            if col not in transformed_data:
                transformed_data[col] = 0.0

        # Cast columns to appropriate types before insertion
        load_data = transformed_data[columns_to_load].copy()
        load_data['date_id'] = pd.to_datetime(load_data['date_id']).dt.date
        load_data['mine_id'] = load_data['mine_id'].astype(str)
        numeric_columns = [
            'total_production_daily', 'equipment_utilization', 
            'fuel_efficiency', 'average_quality_grade',
            'temperature_2m_mean', 'precipitation_sum'
        ]
        for col in numeric_columns:
            load_data[col] = load_data[col].astype(float)

        # Insert into fact table
        client.insert_df(
            'dwh.fact_daily_production',
            load_data
        )
        
        logger.info("Data successfully loaded to DWH")
    except Exception as e:
        logger.error(f"Error during data load: {str(e)}")
        raise

def main():
    run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    logger = setup_logging(run_id)
    validator = DataValidator(run_id)
    
    logger.info(f"Starting ETL process (Run ID: {run_id})")
    
    try:
        # Connect to Clickhouse
        client = clickhouse_connect.get_client(
            host='clickhouse',
            port=8123,
            username=os.environ.get('CLICKHOUSE_USER', 'default'),
            password=os.environ.get('CLICKHOUSE_PASSWORD', '')
        )
        
        # Extract
        production_data, equipment_data, mines_data = extract_data(client, logger)
        
        # Fetch weather data for the date range in production data
        if not production_data.empty:
            start_date = pd.to_datetime(production_data['date']).min()
            end_date = pd.to_datetime(production_data['date']).max()
            weather_data = fetch_weather_data(start_date, end_date, logger)
        else:
            weather_data = pd.DataFrame()

        # Transform and Validate
        transformed_data = transform_data(
            production_data, 
            equipment_data, 
            weather_data,
            validator,
            logger
        )
        
        # Load
        load_to_dwh(client, transformed_data, logger)
        
        logger.info("ETL process completed successfully")
        
    except Exception as e:
        logger.error(f"ETL process failed: {str(e)}")
        raise
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    main() 
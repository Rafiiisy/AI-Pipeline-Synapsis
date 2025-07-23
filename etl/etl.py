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
            weather_response = resp.json()
            weather_data = weather_response['daily']
            weather_df = pd.DataFrame(weather_data)
            weather_df = weather_df.rename(columns={
                'time': 'date_id',
                'precipitation_sum': 'rainfall_mm'  # Rename for clarity
            })
            weather_df['date_id'] = pd.to_datetime(weather_df['date_id']).dt.date
            
            # Extract location data from API response
            location_data = {
                'latitude': weather_response.get('latitude', 2.0167),
                'longitude': weather_response.get('longitude', 117.3000),
                'elevation': weather_response.get('elevation', 44.0),
                'timezone': weather_response.get('timezone', 'Asia/Jakarta'),
                'utc_offset_seconds': weather_response.get('utc_offset_seconds', 25200)
            }
            
            return weather_df, location_data
        else:
            logger.error(f"Failed to fetch weather data: HTTP {resp.status_code} - {resp.text}")
            return pd.DataFrame(), {}
    except Exception as e:
        logger.error(f"An exception occurred while fetching weather data: {e}")
        return pd.DataFrame(), {}

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
        
        # Count total equipment pieces for proper utilization calculation
        total_equipment = equipment_data['equipment_id'].nunique()
        
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
                on=['date_id'],
                how='left'
            )
        
        # Calculate metrics
        transformed_data = merged_data.copy()
        # Calculate equipment utilization as percentage of total possible operational hours
        # Total possible hours = number of equipment × 24 hours per day
        total_possible_hours = total_equipment * 24
        transformed_data['equipment_utilization'] = (
            transformed_data['operational_hours'].fillna(0) / total_possible_hours * 100
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

def load_dimensions(client, production_data, equipment_data, mines_data, location_data, logger):
    """Load dimension tables with data."""
    logger.info("Loading dimension tables...")
    
    try:
        # Load dim_date
        if not production_data.empty:
            dates = pd.to_datetime(production_data['date']).dt.date.unique()
            date_dim_data = []
            for date in dates:
                date_obj = pd.to_datetime(date)
                date_dim_data.append({
                    'date_id': date,
                    'year': date_obj.year,
                    'month': date_obj.month,
                    'day': date_obj.day,
                    'day_of_week': date_obj.dayofweek + 1,  # 1-7 for Monday-Sunday
                    'quarter': date_obj.quarter,
                    'is_weekend': 1 if date_obj.dayofweek >= 5 else 0
                })
            
            if date_dim_data:
                date_df = pd.DataFrame(date_dim_data)
                client.insert_df('dwh.dim_date', date_df)
                logger.info(f"Loaded {len(date_dim_data)} records into dim_date")
        
        # Load dim_mine
        if not mines_data.empty:
            mine_dim_data = []
            for _, row in mines_data.iterrows():
                mine_dim_data.append({
                    'mine_id': str(row['mine_id']),
                    'location': row['location'],
                    'type': 'coal',  # Default type since not in staging
                    'opened_date': pd.to_datetime('2020-01-01').date()  # Default date
                })
            
            if mine_dim_data:
                mine_df = pd.DataFrame(mine_dim_data)
                client.insert_df('dwh.dim_mine', mine_df)
                logger.info(f"Loaded {len(mine_dim_data)} records into dim_mine")
        
        # Load dim_equipment
        if not equipment_data.empty:
            equipment_ids = equipment_data['equipment_id'].unique()
            equipment_dim_data = []
            for equipment_id in equipment_ids:
                equipment_dim_data.append({
                    'equipment_id': equipment_id,
                    'equipment_type': 'mining_equipment',  # Default type
                    'last_maintenance_date': pd.to_datetime('2024-01-01')  # Default date
                })
            
            if equipment_dim_data:
                equipment_df = pd.DataFrame(equipment_dim_data)
                client.insert_df('dwh.dim_equipment', equipment_df)
                logger.info(f"Loaded {len(equipment_dim_data)} records into dim_equipment")
        
        # Load dim_location using data from weather API
        if location_data:
            location_dim_data = [{
                'location_id': 1,  # Primary location from weather API
                'location': 'Berau, Kalimantan, Indonesia',  # Location name
                'latitude': location_data.get('latitude', 2.0167),
                'longitude': location_data.get('longitude', 117.3000),
                'elevation': location_data.get('elevation', 44.0),
                'timezone': location_data.get('timezone', 'Asia/Jakarta'),
                'utc_offset_seconds': location_data.get('utc_offset_seconds', 25200)
            }]
            
            location_df = pd.DataFrame(location_dim_data)
            client.insert_df('dwh.dim_location', location_df)
            logger.info(f"Loaded {len(location_dim_data)} records into dim_location from weather API")
        else:
            # Fallback: create default location if no weather API data
            location_dim_data = [{
                'location_id': 1,
                'location': 'Berau, Kalimantan, Indonesia',  # Location name
                'latitude': 2.0167,
                'longitude': 117.3000,
                'elevation': 44.0,
                'timezone': 'Asia/Jakarta',
                'utc_offset_seconds': 25200
            }]
            location_df = pd.DataFrame(location_dim_data)
            client.insert_df('dwh.dim_location', location_df)
            logger.info("Loaded 1 default record into dim_location")
        
        logger.info("Dimension tables loaded successfully")
        
    except Exception as e:
        logger.error(f"Error loading dimension tables: {str(e)}")
        raise

def load_equipment_metrics(client, equipment_data, production_data, logger):
    """Load equipment metrics into fact_equipment_metrics table."""
    logger.info("Loading equipment metrics...")
    
    try:
        if not equipment_data.empty:
            # Aggregate equipment data by date and equipment_id
            equipment_data['date_id'] = pd.to_datetime(equipment_data['timestamp']).dt.date
            equipment_metrics = equipment_data.groupby(['date_id', 'equipment_id']).agg(
                total_operational_hours=('status', lambda s: (s == 'active').sum()),
                total_maintenance_hours=('status', lambda s: (s == 'maintenance').sum()),
                total_fuel_consumption=('fuel_consumption', 'sum'),
                maintenance_alerts=('maintenance_alert', 'sum')
            ).reset_index()
            
            # Add mine_id and location_id (assuming all equipment belongs to the same mine for simplicity)
            # In a real scenario, you'd have equipment-mine mapping
            if not production_data.empty:
                mine_id = str(production_data['mine_id'].iloc[0])
                equipment_metrics['mine_id'] = mine_id
            else:
                equipment_metrics['mine_id'] = '1'  # Default mine_id
            
            # Add location_id (all equipment is in Berau location)
            equipment_metrics['location_id'] = 1
            
            # Ensure proper data types
            equipment_metrics['date_id'] = pd.to_datetime(equipment_metrics['date_id']).dt.date
            equipment_metrics['equipment_id'] = equipment_metrics['equipment_id'].astype(str)
            equipment_metrics['mine_id'] = equipment_metrics['mine_id'].astype(str)
            
            numeric_cols = ['total_operational_hours', 'total_maintenance_hours', 
                           'total_fuel_consumption', 'maintenance_alerts']
            for col in numeric_cols:
                equipment_metrics[col] = equipment_metrics[col].astype(float)
            
            # Insert into fact_equipment_metrics
            client.insert_df('dwh.fact_equipment_metrics', equipment_metrics)
            logger.info(f"Loaded {len(equipment_metrics)} records into fact_equipment_metrics")
        
        logger.info("Equipment metrics loaded successfully")
        
    except Exception as e:
        logger.error(f"Error loading equipment metrics: {str(e)}")
        raise

def load_to_dwh(client, transformed_data, production_data, equipment_data, mines_data, location_data, logger):
    """Load transformed data into the data warehouse."""
    logger.info("Starting data load to DWH...")
    
    try:
        # Load dimension tables first
        load_dimensions(client, production_data, equipment_data, mines_data, location_data, logger)
        
        # Load equipment metrics
        load_equipment_metrics(client, equipment_data, production_data, logger)
        
        # Load daily production metrics
        columns_to_load = [
            'date_id', 'mine_id', 'location_id', 'total_production_daily',
            'equipment_utilization', 'fuel_efficiency',
            'average_quality_grade', 'temperature_2m_mean', 
            'rainfall_mm'
        ]

        # Add location_id to the data (all records use location_id = 1 for Berau)
        transformed_data['location_id'] = 1
        
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
            'temperature_2m_mean', 'rainfall_mm'
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
            weather_data, location_data = fetch_weather_data(start_date, end_date, logger)
        else:
            weather_data = pd.DataFrame()
            location_data = {}

        # Transform and Validate
        transformed_data = transform_data(
            production_data, 
            equipment_data, 
            weather_data,
            validator,
            logger
        )
        
        # Load
        load_to_dwh(client, transformed_data, production_data, equipment_data, mines_data, location_data, logger)
        
        logger.info("ETL process completed successfully")
        
    except Exception as e:
        logger.error(f"ETL process failed: {str(e)}")
        raise
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    main() 
import pandas as pd
import logging
from datetime import datetime
from pathlib import Path

class DataValidator:
    def __init__(self, run_id=None):
        # Set up logging
        self.run_id = run_id or datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_dir = Path(f'etl/logs/run_{self.run_id}')
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up validation logger
        self.validation_logger = logging.getLogger('validation')
        validation_handler = logging.FileHandler(self.log_dir / 'validation.log')
        validation_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.validation_logger.addHandler(validation_handler)
        self.validation_logger.setLevel(logging.INFO)
        
        # Initialize validation results
        self.validation_results = {
            'total_errors': 0,
            'negative_production': 0,
            'invalid_utilization': 0,
            'missing_weather': 0,
            'details': []
        }

    def validate_production_data(self, df):
        """Validate production data for negative values."""
        negative_prod = df[df['total_production_daily'] < 0]
        if not negative_prod.empty:
            self.validation_results['negative_production'] = len(negative_prod)
            self.validation_results['total_errors'] += len(negative_prod)
            for _, row in negative_prod.iterrows():
                error_msg = f"Negative production found: {row['total_production_daily']} tons on date {row['date_id']} at mine {row['mine_id']}"
                self.validation_logger.error(error_msg)
                self.validation_results['details'].append({
                    'type': 'negative_production',
                    'message': error_msg,
                    'date': row['date_id'],
                    'mine_id': row['mine_id'],
                    'value': row['total_production_daily']
                })
            # Replace negative values with 0
            df.loc[df['total_production_daily'] < 0, 'total_production_daily'] = 0
            self.validation_logger.info("Replaced negative production values with 0")

        return df

    def validate_equipment_utilization(self, df):
        """Validate equipment utilization is between 0 and 100%."""
        invalid_util = df[(df['equipment_utilization'] < 0) | (df['equipment_utilization'] > 100)]
        if not invalid_util.empty:
            self.validation_results['invalid_utilization'] = len(invalid_util)
            self.validation_results['total_errors'] += len(invalid_util)
            for _, row in invalid_util.iterrows():
                error_msg = f"Invalid equipment utilization: {row['equipment_utilization']}% on date {row['date_id']} at mine {row['mine_id']}"
                self.validation_logger.error(error_msg)
                self.validation_results['details'].append({
                    'type': 'invalid_utilization',
                    'message': error_msg,
                    'date': row['date_id'],
                    'mine_id': row['mine_id'],
                    'value': row['equipment_utilization']
                })
            # Clip values to valid range
            df['equipment_utilization'] = df['equipment_utilization'].clip(0, 100)
            self.validation_logger.info("Clipped equipment utilization values to 0-100% range")

        return df

    def validate_weather_data(self, production_df, weather_df):
        """Validate weather data completeness for production dates."""
        prod_dates = set(production_df['date_id'].unique())
        weather_dates = set(weather_df['date_id'].unique())
        missing_dates = prod_dates - weather_dates
        
        if missing_dates:
            self.validation_results['missing_weather'] = len(missing_dates)
            self.validation_results['total_errors'] += len(missing_dates)
            for date in missing_dates:
                error_msg = f"Missing weather data for production date: {date}"
                self.validation_logger.error(error_msg)
                self.validation_results['details'].append({
                    'type': 'missing_weather',
                    'message': error_msg,
                    'date': date,
                    'value': None
                })

        return len(missing_dates) == 0

    def get_validation_summary(self):
        """Return a summary of validation results."""
        return {
            'validation_status': 'FAILED' if self.validation_results['total_errors'] > 0 else 'PASSED',
            'total_errors': self.validation_results['total_errors'],
            'error_counts': {
                'negative_production': self.validation_results['negative_production'],
                'invalid_utilization': self.validation_results['invalid_utilization'],
                'missing_weather': self.validation_results['missing_weather']
            }
        }

    def log_validation_summary(self):
        """Log the validation summary."""
        summary = self.get_validation_summary()
        self.validation_logger.info("=== Validation Summary ===")
        self.validation_logger.info(f"Status: {summary['validation_status']}")
        self.validation_logger.info(f"Total Errors: {summary['total_errors']}")
        self.validation_logger.info("Error Counts:")
        for error_type, count in summary['error_counts'].items():
            self.validation_logger.info(f"  - {error_type}: {count}") 
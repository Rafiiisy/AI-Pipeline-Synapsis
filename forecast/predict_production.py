#!/usr/bin/env python3
"""
Production Forecasting Script
Integrates with ETL pipeline to predict next day's coal production
"""

import os
import sys
import pandas as pd
import numpy as np
import joblib
import pickle
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clickhouse_connector import connector

class ProductionForecaster:
    def __init__(self, models_dir='models'):
        """Initialize the forecaster with trained models"""
        self.models_dir = models_dir
        self.xgb_model = None
        self.prophet_model = None
        self.feature_cols = None
        self.scaler = None
        self.best_model = None
        self.load_models()
    
    def load_models(self):
        """Load trained models from disk"""
        try:
            # Load XGBoost model
            xgb_path = os.path.join(self.models_dir, 'xgboost_production_model.pkl')
            if os.path.exists(xgb_path):
                self.xgb_model = joblib.load(xgb_path)
                print("✅ XGBoost model loaded")
            
            # Load Prophet model
            prophet_path = os.path.join(self.models_dir, 'prophet_production_model.pkl')
            if os.path.exists(prophet_path):
                with open(prophet_path, 'rb') as f:
                    self.prophet_model = pickle.load(f)
                print("✅ Prophet model loaded")
            
            # Load feature columns
            feature_path = os.path.join(self.models_dir, 'feature_columns.pkl')
            if os.path.exists(feature_path):
                with open(feature_path, 'rb') as f:
                    self.feature_cols = pickle.load(f)
                print("✅ Feature columns loaded")
            
            # Load scaler
            scaler_path = os.path.join(self.models_dir, 'scaler.pkl')
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
                print("✅ Scaler loaded")
            
            # Determine best model (you can modify this based on your evaluation)
            self.best_model = 'XGBoost'  # Default, can be changed based on performance
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            raise
    
    def prepare_features(self, df):
        """Prepare features for prediction"""
        df_features = df.copy()
        
        # Convert date to datetime if needed
        if 'date' in df_features.columns:
            df_features['date'] = pd.to_datetime(df_features['date'])
            df_features = df_features.set_index('date')
        
        # Time features
        df_features['day_of_week'] = df_features.index.dayofweek
        df_features['month'] = df_features.index.month
        df_features['quarter'] = df_features.index.quarter
        df_features['year'] = df_features.index.year
        
        # Lag features
        for lag in [1, 2, 3, 7, 14]:
            df_features[f'production_lag_{lag}'] = df_features['total_production_daily'].shift(lag)
        
        # Rolling averages
        for window in [3, 7, 14, 30]:
            df_features[f'production_ma_{window}'] = df_features['total_production_daily'].rolling(window=window).mean()
            df_features[f'production_std_{window}'] = df_features['total_production_daily'].rolling(window=window).std()
        
        # Weather interaction features
        if 'rainfall_mm' in df_features.columns and 'weather_impact' in df_features.columns:
            df_features['rainfall_impact'] = df_features['rainfall_mm'] * df_features['weather_impact']
        if 'temperature_c' in df_features.columns and 'weather_impact' in df_features.columns:
            df_features['temp_impact'] = df_features['temperature_c'] * df_features['weather_impact']
        
        # Equipment efficiency features
        if 'equipment_utilization' in df_features.columns and 'fuel_efficiency' in df_features.columns:
            df_features['equipment_efficiency'] = df_features['equipment_utilization'] * df_features['fuel_efficiency']
        
        return df_features
    
    def predict_next_day(self, days_back=30):
        """Predict next day's production"""
        try:
            # Get recent data
            print(f"📊 Loading last {days_back} days of data...")
            df = connector.get_daily_production_metrics(limit=days_back)
            
            if len(df) < 14:  # Need at least 14 days for lag features
                raise ValueError("Insufficient data for prediction (need at least 14 days)")
            
            # Prepare features
            df_features = self.prepare_features(df)
            
            # Get latest data point for prediction
            latest_data = df_features.iloc[-1:]
            
            if self.best_model == 'XGBoost' and self.xgb_model is not None:
                # Use XGBoost for prediction
                if self.feature_cols:
                    X_pred = latest_data[self.feature_cols].fillna(0)
                    prediction = self.xgb_model.predict(X_pred)[0]
                else:
                    raise ValueError("Feature columns not loaded")
                    
            elif self.best_model == 'Prophet' and self.prophet_model is not None:
                # Use Prophet for prediction
                last_date = df_features.index[-1]
                next_date = last_date + timedelta(days=1)
                future_df = pd.DataFrame({'ds': [next_date]})
                prediction = self.prophet_model.predict(future_df)['yhat'].iloc[0]
                
            else:
                raise ValueError("No valid model available for prediction")
            
            # Get current production for comparison
            current_production = df_features['total_production_daily'].iloc[-1]
            
            return {
                'prediction_date': (df_features.index[-1] + timedelta(days=1)).strftime('%Y-%m-%d'),
                'predicted_production': round(prediction, 2),
                'current_production': round(current_production, 2),
                'change_percent': round(((prediction - current_production) / current_production * 100), 2),
                'model_used': self.best_model,
                'confidence': self._calculate_confidence(df_features)
            }
            
        except Exception as e:
            print(f"❌ Prediction failed: {e}")
            return None
    
    def _calculate_confidence(self, df_features):
        """Calculate prediction confidence based on data quality"""
        # Simple confidence calculation based on data completeness
        missing_ratio = df_features.isnull().sum().sum() / (len(df_features) * len(df_features.columns))
        confidence = max(0.5, 1 - missing_ratio)  # Minimum 50% confidence
        return round(confidence * 100, 1)
    
    def save_prediction_to_db(self, prediction):
        """Save prediction to ClickHouse database"""
        try:
            if prediction is None:
                return False
            
            # Create predictions table if it doesn't exist
            create_table_query = """
            CREATE TABLE IF NOT EXISTS production_predictions (
                prediction_date Date,
                predicted_production Float64,
                current_production Float64,
                change_percent Float64,
                model_used String,
                confidence Float64,
                created_at DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY (prediction_date, created_at)
            """
            
            connector.execute_query(create_table_query)
            
            # Insert prediction
            insert_query = f"""
            INSERT INTO production_predictions 
            (prediction_date, predicted_production, current_production, change_percent, model_used, confidence)
            VALUES (
                '{prediction['prediction_date']}',
                {prediction['predicted_production']},
                {prediction['current_production']},
                {prediction['change_percent']},
                '{prediction['model_used']}',
                {prediction['confidence']}
            )
            """
            
            connector.execute_query(insert_query)
            print("✅ Prediction saved to database")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save prediction: {e}")
            return False

def main():
    """Main function for standalone execution"""
    print("🚀 Starting Production Forecasting...")
    
    # Initialize forecaster
    forecaster = ProductionForecaster()
    
    # Make prediction
    prediction = forecaster.predict_next_day()
    
    if prediction:
        print("\n📊 Prediction Results:")
        print(f"   Date: {prediction['prediction_date']}")
        print(f"   Predicted Production: {prediction['predicted_production']} tons")
        print(f"   Current Production: {prediction['current_production']} tons")
        print(f"   Change: {prediction['change_percent']}%")
        print(f"   Model: {prediction['model_used']}")
        print(f"   Confidence: {prediction['confidence']}%")
        
        # Save to database
        forecaster.save_prediction_to_db(prediction)
        
    else:
        print("❌ Failed to generate prediction")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 
# Jupyter Notebooks for Coal Production Forecasting

This directory contains Jupyter notebooks for time series forecasting of coal production data using ClickHouse.

## Setup

### 1. Start the Jupyter Service
```bash
# Start all services including Jupyter
docker-compose up -d

# Or start just Jupyter (if other services are running)
docker-compose up jupyter
```

### 2. Access Jupyter Lab
- Open your browser and go to: `http://localhost:8888`
- No password or token required (configured for development)

## Notebooks

### `01_production_forecasting.ipynb`
Comprehensive forecasting notebook that includes:

- **Data Loading**: Connect to ClickHouse and load production metrics
- **Exploratory Analysis**: Time series decomposition, ACF/PACF plots
- **Feature Engineering**: Time features, lag features, rolling averages
- **Model Training**: XGBoost, Prophet, SARIMA models
- **Model Evaluation**: MAE, RMSE, MAPE metrics
- **Next Day Prediction**: Ready for deployment
- **Model Persistence**: Save models for production use

## Features

### ClickHouse Integration
- Automatic connection to ClickHouse database
- Pre-built queries for common data access
- Easy data loading and manipulation

### ML Libraries Included
- **XGBoost**: Gradient boosting for tabular data
- **Prophet**: Facebook's forecasting library
- **SARIMA**: Traditional time series models
- **scikit-learn**: Machine learning utilities
- **statsmodels**: Statistical modeling
- **plotly**: Interactive visualizations

### Data Sources
- `daily_production_metrics`: Aggregated daily metrics
- `production_logs`: Raw production data
- `equipment_sensors`: Equipment sensor data

## Usage

### 1. Run the Forecasting Notebook
```python
# In Jupyter notebook
from clickhouse_connector import connector

# Load data
df = connector.get_daily_production_metrics()
print(f"Loaded {len(df)} records")
```

### 2. Train Models
The notebook automatically:
- Splits data chronologically (80% train, 20% test)
- Trains multiple models
- Compares performance
- Saves the best model

### 3. Make Predictions
```python
# Predict next day's production
next_day_pred = predict_next_day_production()
print(f"Next day prediction: {next_day_pred:.2f} tons")
```

## Model Performance

The notebook evaluates models using:
- **MAE**: Mean Absolute Error
- **RMSE**: Root Mean Square Error  
- **MAPE**: Mean Absolute Percentage Error

## Deployment

### Saved Models
Models are saved in `models/` directory:
- `xgboost_production_model.pkl`: XGBoost model
- `prophet_production_model.pkl`: Prophet model
- `feature_columns.pkl`: Feature column names
- `scaler.pkl`: Data scaler

### Integration with ETL
The trained models can be integrated into your ETL pipeline for daily predictions.

## Troubleshooting

### Connection Issues
- Ensure ClickHouse service is running: `docker-compose ps`
- Check environment variables in docker-compose.yml
- Verify network connectivity between containers

### Memory Issues
- Reduce data size by adding LIMIT to queries
- Use smaller model parameters
- Increase Docker memory allocation

### Model Training Issues
- Check for missing values in data
- Ensure sufficient historical data (at least 30 days)
- Adjust model parameters based on data characteristics

## Next Steps

1. **Run the notebook** and explore the data
2. **Experiment with different models** and parameters
3. **Integrate best model** into your ETL pipeline
4. **Set up automated predictions** for daily forecasting
5. **Monitor model performance** and retrain as needed 
# 🚀 Quick Start: Production Forecasting

## Setup Instructions

### 1. Start Jupyter Service
```bash
# Start all services including Jupyter
docker-compose up -d

# Check if Jupyter is running
docker-compose ps
```

### 2. Access Jupyter Lab
- Open browser: `http://localhost:8888`
- Navigate to `notebooks/01_production_forecasting.ipynb`

### 3. Run the Forecasting Notebook
1. **Load Data**: The notebook automatically connects to ClickHouse
2. **Explore Data**: View time series patterns and correlations
3. **Train Models**: XGBoost, Prophet, and SARIMA models are trained automatically
4. **Compare Performance**: See which model performs best
5. **Save Models**: Models are saved to `jupyter/models/` directory

## What You'll Get

### 📊 **Interactive Analysis**
- Time series decomposition
- ACF/PACF plots for seasonality
- Feature importance analysis
- Model performance comparison

### 🤖 **Trained Models**
- **XGBoost**: Best for complex feature interactions
- **Prophet**: Great for seasonal patterns
- **SARIMA**: Traditional time series approach

### 📈 **Predictions**
- Next day production forecast
- Confidence intervals
- Model comparison metrics (MAE, RMSE, MAPE)

## Integration with ETL

### Option 1: Standalone Script
```bash
# Run prediction script
cd jupyter
python predict_production.py
```

### Option 2: Add to ETL Pipeline
```python
# In your ETL script
from jupyter.predict_production import ProductionForecaster

forecaster = ProductionForecaster()
prediction = forecaster.predict_next_day()
print(f"Tomorrow's prediction: {prediction['predicted_production']} tons")
```

## Expected Results

After running the notebook, you should see:

1. **Data Analysis**: Production trends, seasonality patterns
2. **Model Performance**: Comparison table with metrics
3. **Best Model**: Identified based on lowest MAE
4. **Next Day Prediction**: Ready for deployment
5. **Saved Models**: In `jupyter/models/` directory

## Troubleshooting

### Connection Issues
```bash
# Check if ClickHouse is running
docker-compose ps clickhouse

# Restart services if needed
docker-compose restart
```

### Model Training Issues
- Ensure you have at least 30 days of data
- Check for missing values in the data
- Adjust model parameters if needed

### Memory Issues
- Reduce data size by adding LIMIT to queries
- Use smaller model parameters
- Increase Docker memory allocation

## Next Steps

1. **Run the notebook** and explore your data
2. **Experiment with parameters** to improve model performance
3. **Integrate the best model** into your ETL pipeline
4. **Set up automated daily predictions**
5. **Monitor model performance** and retrain as needed

## Files Created

- `jupyter/Dockerfile`: Jupyter environment with ML libraries
- `jupyter/clickhouse_connector.py`: Database connection utility
- `jupyter/notebooks/01_production_forecasting.ipynb`: Main forecasting notebook
- `jupyter/predict_production.py`: Standalone prediction script
- `jupyter/README.md`: Detailed documentation

Ready to start forecasting! 🎯 
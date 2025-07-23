import os
import pandas as pd
import clickhouse_connect
from sqlalchemy import create_engine
import warnings
warnings.filterwarnings('ignore')

class ClickHouseConnector:
    def __init__(self):
        # For local Jupyter connecting to Docker ClickHouse
        self.host = 'localhost'  # Docker ClickHouse exposed to localhost
        self.port = 8123         # HTTP port
        self.user = 'admin'
        self.password = 'admin'
        self.database = 'default'
        
        # Initialize connections
        self.client = None
        self.engine = None
        self._connect()
    
    def _connect(self):
        """Establish connections to ClickHouse"""
        try:
            # ClickHouse Connect client
            self.client = clickhouse_connect.get_client(
                host=self.host,
                port=self.port,
                username=self.user,
                password=self.password,
                database=self.database
            )
            
            # SQLAlchemy engine
            connection_string = f"clickhouse+http://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
            self.engine = create_engine(connection_string)
            
            print(f"✅ Connected to ClickHouse at {self.host}:{self.port}")
            
        except Exception as e:
            print(f"❌ Failed to connect to ClickHouse: {e}")
            print("💡 Make sure ClickHouse Docker container is running: docker-compose up clickhouse")
            raise
    
    def query_to_dataframe(self, query):
        """Execute query and return pandas DataFrame"""
        try:
            result = self.client.query(query)
            df = result.df
            return df
        except Exception as e:
            print(f"❌ Query failed: {e}")
            raise
    
    def execute_query(self, query):
        """Execute query without returning results"""
        try:
            self.client.command(query)
            print("✅ Query executed successfully")
        except Exception as e:
            print(f"❌ Query failed: {e}")
            raise
    
    def get_daily_production_metrics(self, limit=None):
        """Get daily production metrics for forecasting"""
        query = """
        SELECT 
            date,
            total_production_daily,
            average_quality_grade,
            equipment_utilization,
            fuel_efficiency,
            weather_impact,
            rainfall_mm,
            temperature_c
        FROM fact_daily_production
        ORDER BY date
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        return self.query_to_dataframe(query)
    
    def get_production_logs(self, limit=None):
        """Get raw production logs"""
        query = """
        SELECT 
            date,
            mine_id,
            shift,
            tons_extracted,
            quality_grade
        FROM production_logs
        ORDER BY date
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        return self.query_to_dataframe(query)
    
    def get_equipment_sensors(self, limit=None):
        """Get equipment sensor data"""
        query = """
        SELECT 
            timestamp,
            equipment_id,
            status,
            fuel_consumption,
            maintenance_alert
        FROM equipment_sensors
        ORDER BY timestamp
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        return self.query_to_dataframe(query)
    
    def close(self):
        """Close connections"""
        if self.client:
            self.client.close()
        if self.engine:
            self.engine.dispose()

# Global connector instance
connector = ClickHouseConnector() 
import pandas as pd
import requests
from datetime import datetime, timedelta
import logging

# Set up basic logging for the test
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_weather_data(start_date, end_date):
    """
    Fetches historical weather data from the Open-Meteo Archive API for a given date range.
    """
    logger = logging.getLogger('weather_scraper_test')
    logger.info(f'Fetching historical weather data from {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}')
    base_url = "https://archive-api.open-meteo.com/v1/archive"
    weather_rows = []

    for n in range((end_date - start_date).days + 1):
        date_str = (start_date + timedelta(days=n)).strftime('%Y-%m-%d')
        params = {
            'latitude': 2.0167,
            'longitude': 117.3000,
            'daily': 'temperature_2m_mean,precipitation_sum',
            'timezone': 'Asia/Jakarta',
            'start_date': date_str,
            'end_date': date_str
        }
        try:
            resp = requests.get(base_url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                if 'daily' in data and data['daily']['time']:
                    weather_rows.append({
                        'date': pd.to_datetime(data['daily']['time'][0]),
                        'temperature_2m_mean': data['daily']['temperature_2m_mean'][0],
                        'precipitation_sum': data['daily']['precipitation_sum'][0]
                    })
                    logger.info(f"Successfully fetched weather for {date_str}")
                else:
                    logger.warning(f"No weather data returned for {date_str}. Response: {data}")
            else:
                logger.error(f"Failed to fetch weather for {date_str}: HTTP {resp.status_code} - {resp.text}")
        except Exception as e:
            logger.error(f"An exception occurred while fetching weather for {date_str}: {e}")
            
    return pd.DataFrame(weather_rows)

if __name__ == "__main__":
    print("--- Running Weather API Test ---")
    
    # Define a small date range for the test
    test_start_date = datetime(2024, 7, 1)
    test_end_date = datetime(2024, 7, 3)
    
    # Fetch and print the full JSON response for one day
    print("\n--- Full JSON Response for a Single Day (2024-07-01): ---")
    import json
    single_day_params = {
        'latitude': 2.0167,
        'longitude': 117.3000,
        'daily': 'temperature_2m_mean,precipitation_sum',
        'timezone': 'Asia/Jakarta',
        'start_date': '2024-07-01',
        'end_date': '2024-07-01'
    }
    base_url = "https://archive-api.open-meteo.com/v1/archive"
    resp = requests.get(base_url, params=single_day_params)
    if resp.status_code == 200:
        print(json.dumps(resp.json(), indent=2))
    else:
        print(f"Failed to fetch data: HTTP {resp.status_code}")

    # Fetch and print the DataFrame for the date range
    weather_df = fetch_weather_data(test_start_date, test_end_date)
    
    # Print the results
    if not weather_df.empty:
        print("\n--- Processed DataFrame for the Date Range: ---")
        print(weather_df)
    else:
        print("\n--- Test failed. No data was fetched. Check logs for errors. ---")

    print("\n--- Test Finished ---") 
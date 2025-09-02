import requests
import pandas as pd
from datetime import datetime

def fetch_open_meteo_data(latitude, longitude, start_date, end_date):
    """
    Fetches hourly weather data from Open-Meteo and returns a clean DataFrame.
    """
    API_URL = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation",
        "timezone": "auto"
    }
    print("Fetching data from Open-Meteo...")
    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    data = response.json()
    print("Data fetched successfully!")
    hourly_data = data['hourly']
    df = pd.DataFrame(hourly_data)
    df = df.rename(columns={
        "time": "timestamp",
        "temperature_2m": "temp_c",
        "relative_humidity_2m": "rh",
        "precipitation": "rain_mm"
    })
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def fetch_visual_crossing_data(latitude, longitude, start_date, end_date, api_key):
    """
    Fetches hourly weather data from Visual Crossing as a backup.
    """
    API_URL = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{latitude},{longitude}/{start_date}/{end_date}"
    params = {
        "unitGroup": "metric",
        "include": "hours",
        "key": api_key,
        "contentType": "json"
    }
    print("Fetching data from Visual Crossing (backup)...")
    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    data = response.json()
    print("Data fetched successfully from backup!")
    all_hours = []
    for day in data['days']:
        all_hours.extend(day['hours'])
    df = pd.DataFrame(all_hours)
    df['timestamp'] = pd.to_datetime(data['days'][0]['datetime'] + ' ' + df['datetime'])
    df = df.rename(columns={
        "temp": "temp_c",
        "humidity": "rh",
        "precip": "rain_mm"
    })
    return df[['timestamp', 'temp_c', 'rh', 'rain_mm']]

def get_weather_data(latitude, longitude, start_date, end_date, vc_api_key):
    """
    Tries to fetch data from the primary source, failing over to the backup.
    """
    try:
        print("--- Attempting Primary API (Open-Meteo) ---")
        weather_df = fetch_open_meteo_data(latitude, longitude, start_date, end_date)
        if weather_df is not None:
            return weather_df
    except Exception as e:
        print(f"Primary API failed: {e}. Trying backup.")
    
    print("\n--- Attempting Backup API (Visual Crossing) ---")
    weather_df = fetch_visual_crossing_data(latitude, longitude, start_date, end_date, vc_api_key)
    return weather_df

# --- Main part of the script ---
if __name__ == "__main__":
    # Location: Summerside, PEI
    LATITUDE = 46.40
    LONGITUDE = -63.79
    
    # Date Range
    START_DATE = "2025-08-01"
    END_DATE = "2025-08-07"
    
    # !!! ADD YOUR VISUAL CROSSING API KEY HERE !!!
    VISUAL_CROSSING_API_KEY = "7V98YER9466SUUGPHQ4MWUSYV"

    weather_df = get_weather_data(LATITUDE, LONGITUDE, START_DATE, END_DATE, VISUAL_CROSSING_API_KEY)

    if weather_df is not None:
        print("\nFinal weather data processed and formatted:")
        print(weather_df.head())
        output_filename = "summerside_weather_failover.csv"
        weather_df.to_csv(output_filename, index=False)
        print(f"\nData saved to '{output_filename}'")
    else:
        print("\nCould not fetch weather data from any source.")
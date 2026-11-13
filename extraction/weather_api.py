import requests
import pandas as pd
import json
import time

from pathlib import Path
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ==========================================
# E-COMMERCE 360
# HISTORICAL WEATHER DATA EXTRACTION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
EXTERNAL_DIR = RAW_DIR / "external" / "weather"

EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)


# Historical period obtained from Olist

START_DATE = "2016-09-04"
END_DATE = "2018-10-17"


# Top five customer cities
# Approximate city-centre coordinates

CITIES = {
    "sao paulo": {
        "latitude": -23.5505,
        "longitude": -46.6333
    },

    "rio de janeiro": {
        "latitude": -22.9068,
        "longitude": -43.1729
    },

    "belo horizonte": {
        "latitude": -19.9167,
        "longitude": -43.9345
    },

    "brasilia": {
        "latitude": -15.7939,
        "longitude": -47.8828
    },

    "curitiba": {
        "latitude": -25.4284,
        "longitude": -49.2733
    }
}


API_URL = "https://archive-api.open-meteo.com/v1/archive"


# ==========================================
# REQUEST SESSION WITH RETRIES
# ==========================================

session = requests.Session()

retry_strategy = Retry(
    total=3,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)

adapter = HTTPAdapter(max_retries=retry_strategy)

session.mount("https://", adapter)


# ==========================================
# WEATHER EXTRACTION FUNCTION
# ==========================================

def extract_weather(city, coordinates):

    params = {
        "latitude": coordinates["latitude"],
        "longitude": coordinates["longitude"],

        "start_date": START_DATE,
        "end_date": END_DATE,

        "daily": [
            "temperature_2m_mean",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "rain_sum",
            "wind_speed_10m_max",
            "weather_code"
        ],

        "timezone": "America/Sao_Paulo",

        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm"
    }

    print(f"\nFetching weather: {city}")

    response = session.get(
        API_URL,
        params=params,
        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    daily = data["daily"]

    df = pd.DataFrame(daily)

    df.rename(
        columns={"time": "weather_date"},
        inplace=True
    )

    df["city"] = city

    df["latitude"] = coordinates["latitude"]

    df["longitude"] = coordinates["longitude"]

    df["source"] = "Open-Meteo Historical Weather API"

    df["extracted_at"] = datetime.now().isoformat()

    # Save original API response

    raw_file = EXTERNAL_DIR / f"{city.replace(' ', '_')}.json"

    with open(raw_file, "w") as file:

        json.dump(data, file, indent=4)

    print("Records:", len(df))

    return df


# ==========================================
# MAIN EXTRACTION PIPELINE
# ==========================================

def main():

    print("=" * 60)

    print("E-COMMERCE 360 - WEATHER DATA EXTRACTION")

    print("=" * 60)

    all_weather = []

    for city, coordinates in CITIES.items():

        try:

            df = extract_weather(city, coordinates)

            all_weather.append(df)

            time.sleep(1)

        except requests.RequestException as error:

            print(f"API ERROR for {city}: {error}")

        except (KeyError, ValueError) as error:

            print(f"DATA ERROR for {city}: {error}")

    if not all_weather:

        raise RuntimeError(
            "Weather extraction failed for every city."
        )

    final_df = pd.concat(
        all_weather,
        ignore_index=True
    )

    output_file = EXTERNAL_DIR / "weather_daily.csv"

    final_df.to_csv(
        output_file,
        index=False
    )

    metadata = {

        "project": "E-Commerce 360",

        "source": "Open-Meteo Historical Weather API",

        "cities_requested": len(CITIES),

        "cities_extracted": len(all_weather),

        "total_records": len(final_df),

        "start_date": START_DATE,

        "end_date": END_DATE,

        "extracted_at": datetime.now().isoformat()

    }

    metadata_file = EXTERNAL_DIR / "weather_metadata.json"

    with open(metadata_file, "w") as file:

        json.dump(metadata, file, indent=4)

    print("\n" + "=" * 60)

    print("WEATHER EXTRACTION SUMMARY")

    print("=" * 60)

    print(final_df.groupby("city").size())

    print("\nTotal weather records:", len(final_df))

    print("\nSaved:", output_file)

    print("\nWEATHER EXTRACTION COMPLETED!")


if __name__ == "__main__":

    main()
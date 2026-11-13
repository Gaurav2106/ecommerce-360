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
# BRAZIL NATIONAL HOLIDAY EXTRACTION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
EXTERNAL_DIR = RAW_DIR / "external" / "holidays"

EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)


YEARS = [2016, 2017, 2018]

API_URL = "https://brasilapi.com.br/api/feriados/v1"


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
# HOLIDAY EXTRACTION FUNCTION
# ==========================================

def extract_holidays(year):

    url = f"{API_URL}/{year}"

    print(f"\nFetching holidays for {year}...")

    response = session.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list):
        raise ValueError(
            f"Unexpected API response for {year}"
        )

    df = pd.DataFrame(data)

    required_columns = ["date", "name", "type"]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing API columns: {missing_columns}"
        )

    df["holiday_year"] = year

    df["source"] = "BrasilAPI"

    df["extracted_at"] = datetime.now().isoformat()

    # Save original API response

    raw_file = (
        EXTERNAL_DIR / f"holidays_{year}.json"
    )

    with open(raw_file, "w") as file:

        json.dump(data, file, indent=4, ensure_ascii=False)

    print("Holiday records:", len(df))

    return df


# ==========================================
# MAIN EXTRACTION PIPELINE
# ==========================================

def main():

    print("=" * 60)

    print("E-COMMERCE 360 - HOLIDAY DATA EXTRACTION")

    print("=" * 60)

    all_holidays = []

    failed_years = []

    for year in YEARS:

        try:

            df = extract_holidays(year)

            all_holidays.append(df)

            time.sleep(1)

        except requests.RequestException as error:

            print(f"API ERROR for {year}: {error}")

            failed_years.append(year)

        except (ValueError, KeyError) as error:

            print(f"DATA ERROR for {year}: {error}")

            failed_years.append(year)

    if not all_holidays:

        raise RuntimeError(
            "Holiday extraction failed for every year."
        )

    final_df = pd.concat(
        all_holidays,
        ignore_index=True
    )

    final_df["date"] = pd.to_datetime(
        final_df["date"],
        errors="coerce"
    )

    output_file = (
        EXTERNAL_DIR / "brazil_holidays.csv"
    )

    final_df.to_csv(
        output_file,
        index=False
    )

    metadata = {

        "project": "E-Commerce 360",

        "source": "BrasilAPI",

        "years_requested": YEARS,

        "years_extracted": sorted(
            final_df["holiday_year"].unique().tolist()
        ),

        "failed_years": failed_years,

        "total_records": len(final_df),

        "extracted_at": datetime.now().isoformat()

    }

    metadata_file = (
        EXTERNAL_DIR / "holiday_metadata.json"
    )

    with open(metadata_file, "w") as file:

        json.dump(metadata, file, indent=4)

    print("\n" + "=" * 60)

    print("HOLIDAY EXTRACTION SUMMARY")

    print("=" * 60)

    print(
        final_df.groupby("holiday_year").size()
    )

    print("\nTotal holiday records:", len(final_df))

    print("\nSaved:", output_file)

    print("\nFailed years:", failed_years)

    print("\nHOLIDAY EXTRACTION COMPLETED!")


if __name__ == "__main__":

    main()
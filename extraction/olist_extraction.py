import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# ==========================================
# E-COMMERCE 360
# OLIST DATA EXTRACTION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
LOG_DIR = BASE_DIR / "logs"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


DATASETS = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "category_translation": "product_category_name_translation.csv"
}


def extract_dataset(name, filename):

    file_path = RAW_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {filename}"
        )

    df = pd.read_csv(file_path)

    print(f"\nDataset: {name}")
    print(f"File: {filename}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("Column names:")
    print(df.columns.tolist())

    return df


def main():

    print("=" * 60)
    print("E-COMMERCE 360 - OLIST DATA EXTRACTION")
    print("=" * 60)

    extracted_data = {}
    dataset_profile = []

    for name, filename in DATASETS.items():

        df = extract_dataset(name, filename)

        extracted_data[name] = df

        dataset_profile.append({
            "dataset": name,
            "filename": filename,
            "row_count": len(df),
            "column_count": len(df.columns),
            "duplicate_rows": int(df.duplicated().sum()),
            "missing_values": int(df.isnull().sum().sum()),
            "extracted_at": datetime.now().isoformat()
        })

    # Save dataset profile

    profile_df = pd.DataFrame(dataset_profile)

    profile_path = (
        PROCESSED_DIR / "olist_data_profile.csv"
    )

    profile_df.to_csv(profile_path, index=False)

    # Save extraction metadata

    metadata = {
        "project": "E-Commerce 360",
        "source": "Olist Brazilian E-Commerce Dataset",
        "extraction_timestamp": datetime.now().isoformat(),
        "datasets_extracted": len(extracted_data),
        "total_records": int(
            profile_df["row_count"].sum()
        )
    }

    metadata_path = (
        PROCESSED_DIR / "extraction_metadata.json"
    )

    with open(metadata_path, "w") as file:
        json.dump(metadata, file, indent=4)

    print("\n" + "=" * 60)
    print("EXTRACTION SUMMARY")
    print("=" * 60)

    print(profile_df.to_string(index=False))

    print("\nTotal datasets:", len(extracted_data))

    print(
        "Total records:",
        f"{metadata['total_records']:,}"
    )

    print("\nProfile saved:", profile_path)
    print("Metadata saved:", metadata_path)

    print("\nOLIST EXTRACTION COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
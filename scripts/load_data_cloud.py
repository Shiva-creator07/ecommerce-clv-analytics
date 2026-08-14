"""
Loads Olist CSVs from data/raw/ into the cloud (Neon) Postgres instance.
Skips 'geolocation' — large table, unused by the dashboard, and Neon's
free tier has limited storage.
"""
import sys
import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

env_file = sys.argv[1] if len(sys.argv) > 1 else ".env.cloud"
load_dotenv(env_file, override=True)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATA_DIR = "data/raw"

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
)

TIMESTAMP_COLS = {
    "orders": [
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "order_items": ["shipping_limit_date"],
    "order_reviews": ["review_creation_date", "review_answer_timestamp"],
}

# geolocation skipped intentionally — see docstring
LOAD_ORDER = [
    ("olist_customers_dataset.csv", "customers"),
    ("olist_sellers_dataset.csv", "sellers"),
    ("product_category_name_translation.csv", "product_category_translation"),
    ("olist_products_dataset.csv", "products"),
    ("olist_orders_dataset.csv", "orders"),
    ("olist_order_items_dataset.csv", "order_items"),
    ("olist_order_payments_dataset.csv", "order_payments"),
    ("olist_order_reviews_dataset.csv", "order_reviews"),
]


def load_csv_to_table(csv_filename: str, table_name: str):
    path = os.path.join(DATA_DIR, csv_filename)
    print(f"Reading {csv_filename} ...")
    df = pd.read_csv(path)

    if table_name == "products":
        df = df.rename(columns={
            "product_name_lenght": "product_name_length",
            "product_description_lenght": "product_description_length",
        })

    for col in TIMESTAMP_COLS.get(table_name, []):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    df.to_sql(table_name, engine, if_exists="append", index=False,
               method="multi", chunksize=2000)
    print(f"  -> Loaded {len(df):,} rows into '{table_name}'")


def main():
    for csv_filename, table_name in LOAD_ORDER:
        load_csv_to_table(csv_filename, table_name)
    print("\nAll tables loaded successfully (geolocation skipped).")


if __name__ == "__main__":
    main()

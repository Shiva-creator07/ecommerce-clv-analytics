import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

CATEGORY_RANGES = {
    "electronics": (0.70, 0.80), "computers": (0.70, 0.80),
    "telephony": (0.70, 0.80), "tablets": (0.70, 0.80), "audio": (0.70, 0.80),
    "fashio": (0.35, 0.50), "beauty": (0.35, 0.50),
    "health": (0.35, 0.50), "perfum": (0.35, 0.50),
    "furniture": (0.45, 0.60), "decor": (0.45, 0.60),
    "housewares": (0.45, 0.60), "garden": (0.45, 0.60),
    "office_furniture": (0.45, 0.60),
    "book": (0.55, 0.65), "cd": (0.55, 0.65), "dvd": (0.55, 0.65),
    "music": (0.55, 0.65), "stationery": (0.55, 0.65),
    "toy": (0.40, 0.55), "game": (0.40, 0.55),
    "baby": (0.40, 0.55), "sport": (0.40, 0.55),
}
DEFAULT_RANGE = (0.50, 0.65)
RANDOM_SEED = 42


def get_range_for_category(category_name):
    if not isinstance(category_name, str):
        return DEFAULT_RANGE
    lowered = category_name.lower()
    for keyword, rng in CATEGORY_RANGES.items():
        if keyword in lowered:
            return rng
    return DEFAULT_RANGE


def main():
    rng = np.random.default_rng(RANDOM_SEED)
    query = """
        SELECT p.product_id, t.product_category_name_english
        FROM products p
        LEFT JOIN product_category_translation t
          ON p.product_category_name = t.product_category_name
    """
    products = pd.read_sql(query, engine)
    print(f"Fetched {len(products):,} products")

    cogs_ratios = []
    for category in products["product_category_name_english"]:
        low, high = get_range_for_category(category)
        cogs_ratios.append(round(rng.uniform(low, high), 3))

    products["cogs_ratio"] = cogs_ratios
    output = products[["product_id", "cogs_ratio"]]

    output.to_sql("product_costs", engine, if_exists="append",
                   index=False, method="multi", chunksize=5000)
    print(f"Loaded {len(output):,} rows into 'product_costs'")


if __name__ == "__main__":
    main()

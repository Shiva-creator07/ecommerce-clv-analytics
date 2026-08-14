"""
Runs a .sql file against a database, using credentials from a specified
.env file. Usage: python scripts/run_sql_file.py <sql_file> <env_file>
"""
import sys
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def main():
    if len(sys.argv) != 3:
        print("Usage: python scripts/run_sql_file.py <sql_file> <env_file>")
        sys.exit(1)

    sql_file, env_file = sys.argv[1], sys.argv[2]
    load_dotenv(env_file, override=True)

    engine = create_engine(
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        f"?sslmode=require"
    )

    with open(sql_file, "r") as f:
        sql_content = f.read()

    print(f"Running {sql_file} against {os.getenv('DB_HOST')} ...")
    with engine.begin() as conn:
        conn.execute(text(sql_content))
    print(f"  -> Done.")

if __name__ == "__main__":
    main()

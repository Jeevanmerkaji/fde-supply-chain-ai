from pathlib import Path
from urllib.parse import quote_plus
import os

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv


# __file__ is 'scripts/ingest_legacy_data.py'
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent

load_dotenv(project_root / ".env")


data_path = project_root / "data" / "raw" / "dynamic_supply_chain_logistics_dataset.csv"

db_host = os.getenv("SQL_SERVER_HOST", "localhost")
db_port = os.getenv("SQL_SERVER_PORT", "1433")
db_user = os.getenv("SQL_ADMIN_USER")
db_password = os.getenv("SQL_ADMIN_PASSWORD")


print(f"Loading the CSV from {data_path}")
df = pd.read_csv(data_path)

# Parse timestamps so SQL Server stores a real DATETIME, not text
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Mapping the clean columns to a messy 2000s legacy enterprise schema
legacy_mapping = {
    'timestamp': 'TS_UTC',
    'vehicle_gps_latitude': 'V_LAT',
    'vehicle_gps_longitude': 'V_LON',
    'iot_temperature': 'IOT_TEMP_VAL_C',
    'cargo_condition_status': 'CGO_COND_CD',
    'risk_classification': 'RISK_CLS_TXT',
    'delay_probability': 'DELAY_PROB_DEC',
    'port_congestion_level': 'PRT_CNG_LVL',
    'route_risk_level': 'RT_RSK_IDX'
}

# Keep only the columns we mapped for this demo and rename them
df_legacy = df[list(legacy_mapping.keys())].rename(columns=legacy_mapping)

# Adding a fake ingestion flag to make it look like an automated legacy system
df_legacy['SYS_INGEST_FLAG'] = 'Y'


# Connect to the docker SQL Server
print("Connecting to the legacy MSSQL Database.....")

# Using the pyodbc driver (requires ODBC Driver 18 for SQL Server on the OS).
# PWD is wrapped in {} so special characters like ; don't break the string.
connection_string = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={db_host},{db_port};"
    f"DATABASE=master;"
    f"UID={db_user};"
    f"PWD={{{db_password.replace('}', '}}')}}};"
    f"Encrypt=no;"
    f"TrustServerCertificate=yes;"
)

params = quote_plus(connection_string)

# fast_executemany sends rows in batches instead of one INSERT per row
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}", fast_executemany=True)

# Ingest the data into the messy table name
table_name = 'TBL_SC_FLEET_HIST_RAW'
print(f"Ingesting into {table_name}. This may take a minute....")
df_legacy.to_sql(table_name, engine, if_exists='replace', index=False, schema='dbo', chunksize=5000)

with engine.connect() as conn:
    row_count = conn.execute(text(f"SELECT COUNT(*) FROM dbo.{table_name}")).scalar()

print(f"Done. {row_count} rows in dbo.{table_name} (CSV had {len(df_legacy)} rows)")

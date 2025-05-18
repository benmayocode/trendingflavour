import psycopg2
from shapely.wkb import loads as wkb_loads
from dotenv import load_dotenv
import os
# Load environment variables from a .env file
load_dotenv()

def get_connection():
    return psycopg2.connect(
        dbname="postgres",
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port="5432"
    )



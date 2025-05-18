# cosmos.py
import os
from azure.cosmos import CosmosClient, PartitionKey
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / '.env')

COSMOS_URL = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
COSMOS_DB_NAME = "TrendingFlavours"

if not COSMOS_URL or not COSMOS_KEY:
    raise ValueError("COSMOS_ENDPOINT and COSMOS_KEY environment variables are required.")

client = CosmosClient(COSMOS_URL, COSMOS_KEY)
database = client.create_database_if_not_exists(COSMOS_DB_NAME)

def get_cosmos_container(container_name: str, partition_key_path: str = "/id"):
    return database.create_container_if_not_exists(
        id=container_name,
        partition_key=PartitionKey(path=partition_key_path)
    )

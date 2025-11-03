import os
from chromadb.config import Settings
import chromadb

CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

def get_client():
    settings = Settings(chroma_db_impl="duckdb+parquet", persist_directory=CHROMA_DIR)
    client = chromadb.Client(settings=settings)
    return client

def get_collection(name="documents"):
    client = get_client()
    try:
        return client.get_collection(name)
    except Exception:
        return client.create_collection(name=name)

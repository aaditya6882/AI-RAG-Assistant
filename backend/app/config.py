import os

from dotenv import load_dotenv

load_dotenv()

_raw_database_url = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/ragdb",
)

PSYCOPG_DATABASE_URL = (
    _raw_database_url
    .replace("postgresql+psycopg://", "postgresql://")
    .replace("postgresql+psycopg2://", "postgresql://")
)

SQLALCHEMY_DATABASE_URL = PSYCOPG_DATABASE_URL.replace(
    "postgresql://",
    "postgresql+psycopg://",
    1,
)

# Kept for existing imports
DATABASE_URL = SQLALCHEMY_DATABASE_URL

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
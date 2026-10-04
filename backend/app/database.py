from sqlalchemy import create_engine, text

from app.config import SQLALCHEMY_DATABASE_URL


engine = create_engine(SQLALCHEMY_DATABASE_URL)


def test_database_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return result.scalar() == 1
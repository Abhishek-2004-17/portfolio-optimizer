from sqlalchemy import create_engine, text

from app.core.config import settings


def init_db() -> None:
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("Database connection verified.")

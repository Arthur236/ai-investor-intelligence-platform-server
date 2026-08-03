from sqlalchemy import Engine, create_engine

from ..config import (
    POSTGRES_DATABASE,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)


def get_engine(database: str | None = None) -> Engine:
    db_name = database or POSTGRES_DATABASE
    url = (
        f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{db_name}?sslmode=require"
    )
    return create_engine(url)

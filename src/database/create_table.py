import psycopg2
from sqlalchemy import text

from ..config import (
    POSTGRES_DATABASE,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)
from .postgres_sql import get_engine

CREATE_FINANCIAL_METRICS_TABLE = """
CREATE TABLE IF NOT EXISTS financial_metrics (
    id SERIAL PRIMARY KEY,
    company TEXT NOT NULL,
    year TEXT NOT NULL,
    revenue TEXT,
    net_income TEXT,
    operating_income TEXT,
    cash_flow TEXT,
    total_assets TEXT,
    total_liabilities TEXT,
    risk_factors TEXT,
    growth_drivers TEXT,
    source_file TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


def create_database() -> None:
    """Create the target Postgres database if it doesn't already exist."""
    connection = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname="postgres",
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        sslmode="require",
    )
    connection.autocommit = True

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (POSTGRES_DATABASE,)
            )
            if cursor.fetchone() is None:
                cursor.execute(f'CREATE DATABASE "{POSTGRES_DATABASE}"')
    finally:
        connection.close()


def create_tables() -> None:
    engine = get_engine()
    with engine.begin() as connection:
        connection.execute(text(CREATE_FINANCIAL_METRICS_TABLE))


if __name__ == "__main__":
    create_database()
    create_tables()
    print("Database and tables ready.")

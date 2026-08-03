from sqlalchemy import text

from .postgres_sql import get_engine

LATEST_METRICS_QUERY = """
SELECT company, year, revenue, net_income, operating_income, cash_flow,
       total_assets, total_liabilities, risk_factors, growth_drivers,
       source_file, created_at
FROM (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY company, year ORDER BY created_at DESC
           ) AS row_number
    FROM financial_metrics
) ranked
WHERE row_number = 1
ORDER BY company, year;
"""


def get_metrics() -> list[dict]:
    engine = get_engine()
    with engine.connect() as connection:
        result = connection.execute(text(LATEST_METRICS_QUERY))
        return [dict(row._mapping) for row in result]

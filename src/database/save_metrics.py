from sqlalchemy import text

from .postgres_sql import get_engine

INSERT_METRICS = """
INSERT INTO financial_metrics (
    company, year, revenue, net_income, operating_income, cash_flow,
    total_assets, total_liabilities, risk_factors, growth_drivers, source_file
) VALUES (
    :company, :year, :revenue, :net_income, :operating_income, :cash_flow,
    :total_assets, :total_liabilities, :risk_factors, :growth_drivers, :source_file
);
"""


def _field(metrics: dict, snake_case: str, title_case: str):
    return metrics.get(snake_case, metrics.get(title_case))


def save_metrics(
    company: str, year: str, metrics: dict, source_file: str | None = None
) -> None:
    engine = get_engine()
    params = {
        "company": company,
        "year": year,
        "revenue": _field(metrics, "revenue", "Revenue"),
        "net_income": _field(metrics, "net_income", "Net Income"),
        "operating_income": _field(metrics, "operating_income", "Operating Income"),
        "cash_flow": _field(
            metrics, "cash_flow", "Cash Flow from Operating Activities"
        ),
        "total_assets": _field(metrics, "total_assets", "Total Assets"),
        "total_liabilities": _field(metrics, "total_liabilities", "Total Liabilities"),
        "risk_factors": _field(metrics, "risk_factors", "Top Risk Factors"),
        "growth_drivers": _field(metrics, "growth_drivers", "Top Growth Drivers"),
        "source_file": source_file,
    }

    with engine.begin() as connection:
        connection.execute(text(INSERT_METRICS), params)

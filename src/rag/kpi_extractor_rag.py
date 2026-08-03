from pydantic import BaseModel, Field

from ..llm.anthropic_client import get_structured_completion
from ..vectorstore.astra_vectorstore import Retriever


class FinancialMetrics(BaseModel):
    revenue: str | None = Field(default=None, description="Revenue")
    net_income: str | None = Field(default=None, description="Net Income")
    operating_income: str | None = Field(default=None, description="Operating Income")
    cash_flow: str | None = Field(
        default=None, description="Cash Flow from Operating Activities"
    )
    total_assets: str | None = Field(default=None, description="Total Assets")
    total_liabilities: str | None = Field(
        default=None, description="Total Liabilities"
    )
    risk_factors: str | None = Field(default=None, description="Top Risk Factors")
    growth_drivers: str | None = Field(default=None, description="Top Growth Drivers")


def retrieve_context(retriever: Retriever, company: str, year: str) -> str:
    query = f"{company} {year} revenue net income cash flow assets liabilities risk factors growth drivers"
    chunks = retriever.invoke(query, company=company, year=year, top_k=20)
    return "\n\n".join(chunk.page_content for chunk in chunks)


def build_extraction_prompt(company: str, year: str, context: str) -> str:
    return f"""You are a financial analyst extracting key metrics from a 10-K filing.

Company: {company}
Fiscal Year: {year}

Using ONLY the context below, extract the following metrics. If a value is not
present in the context, leave it null. Keep risk factors and growth drivers to
2-3 concise bullet points each.

Context:
{context}
"""


def extract_financial_metrics(retriever: Retriever, company: str, year: str) -> dict:
    context = retrieve_context(retriever, company, year)
    prompt = build_extraction_prompt(company, year, context)
    metrics = get_structured_completion(prompt, FinancialMetrics)
    return metrics.model_dump()

from pydantic import BaseModel, Field

from ..llm.anthropic_client import get_structured_completion
from ..vectorstore.astra_vectorstore import Retriever


class FinancialMetrics(BaseModel):
    """Structured financial metrics extracted from a 10-K filing."""

    revenue: str | None = Field(default=None, description="Revenue")
    net_income: str | None = Field(default=None, description="Net Income")
    operating_income: str | None = Field(default=None, description="Operating Income")
    cash_flow: str | None = Field(
        default=None, description="Cash Flow from Operating Activities"
    )
    total_assets: str | None = Field(default=None, description="Total Assets")
    total_liabilities: str | None = Field(default=None, description="Total Liabilities")
    risk_factors: str | None = Field(default=None, description="Top Risk Factors")
    growth_drivers: str | None = Field(default=None, description="Top Growth Drivers")


def retrieve_context(retriever: Retriever, company: str, year: str) -> str:
    """Retrieve relevant filing context for the given company and fiscal year."""
    query = f"{company} {year} revenue net income cash flow assets liabilities risk factors growth drivers"
    chunks = retriever.invoke(query, company=company, year=year, top_k=20)
    return "\n\n".join(chunk.page_content for chunk in chunks)


def build_extraction_prompt(company: str, year: str, context: str) -> str:
    """Build a prompt for extracting financial metrics from filing context."""
    return f"""You are a financial analyst extracting key metrics from a 10-K filing.

Company: {company}
Fiscal Year: {year}

Using ONLY the context below, extract the following metrics. If a value is not
present in the context, leave it null, don't make it up or say its not in the document.
Revenue, net income, operating income, cash flow, total assets, and total liabilities should be a single
number and not a comparison of previous year.
Keep risk factors and growth drivers to 2-3 concise bullet points each.

Use the following sample as a guide for formatting your response in JSON:
{
        "Revenue": "$716,924",
        "Net Income": "$77,670",
        "Operating Income": "$79,975",
        "Cash Flow": "$139,514",
        "Total Assets": "$818,042",
        "Total Liabilities": "$818,042M",
        "Risk Factors": "- Risk factor 1 \n- Risk factor 2 \n- Risk factor 3",
        "Growth Drivers": "- Growth driver 1 \n- Growth driver 2 \n- Growth driver 3"
}

Context:
{context}
"""


def extract_financial_metrics(retriever: Retriever, company: str, year: str) -> dict:
    """Extract financial metrics for a company and fiscal year using the retriever."""
    context = retrieve_context(retriever, company, year)
    prompt = build_extraction_prompt(company, year, context)
    metrics = get_structured_completion(prompt, FinancialMetrics)
    return metrics.model_dump()

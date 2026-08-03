from fastapi import APIRouter

from ..database.metrics import get_metrics

router = APIRouter()


@router.get("/metrics")
def list_metrics(company: str | None = None, year: str | None = None) -> list[dict]:
    metrics = get_metrics()

    if company:
        metrics = [m for m in metrics if m["company"].lower() == company.lower()]
    if year:
        metrics = [m for m in metrics if m["year"] == year]

    return metrics


@router.get("/companies")
def list_companies() -> list[str]:
    metrics = get_metrics()
    return sorted({m["company"] for m in metrics})

from fastapi import APIRouter

from ..database.metrics import get_metrics

router = APIRouter()


@router.get("/metrics")
def list_metrics(
    company: str | None = None, year: str | None = None
) -> dict[str, list[dict]]:
    """Retrieve metrics, optionally filtering by company and year."""
    metrics = get_metrics()

    if company:
        metrics = [m for m in metrics if m["company"].lower() == company.lower()]
    if year:
        metrics = [m for m in metrics if m["year"] == year]

    return {"metrics": metrics}


@router.get("/companies")
def list_companies() -> dict[str, list[str]]:
    """Retrieve a sorted list of all unique companies from metrics."""
    metrics = get_metrics()
    return {"companies": sorted({m["company"] for m in metrics})}

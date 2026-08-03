def main() -> None:
    from .ingestion.ingest_documents import (
        ingest_directory,
    )

    ingested = ingest_directory()
    print(f"Ingested {len(ingested)} document(s):")
    for item in ingested:
        print(f"  - {item['company']} {item['year']}")

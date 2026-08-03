import re
from pathlib import Path

from ..config import MARKDOWN_DIR, PDFS_DIR
from ..database.save_metrics import save_metrics
from ..embeddings.voyage_embeddings import (
    get_embeddings,
)
from ..rag.kpi_extractor_rag import (
    extract_financial_metrics,
)
from ..vectorstore.astra_vectorstore import (
    Retriever,
    upload_chunks,
)
from .pdf_to_markdown import (
    PDFToMarkdownConverter,
)
from .semantic_chunker import chunk_markdown

COMPANY_YEAR_PATTERN = re.compile(r"^([A-Za-z]+)_10K_(\d{4})$")


def parse_company_year(pdf_file: Path) -> tuple[str, str]:
    """Parse a company name and year from a 10-K PDF filename.

    Args:
        pdf_file: Path object for the PDF file.

    Returns:
        A tuple containing the company name and year.

    Raises:
        ValueError: If the filename does not match the expected pattern.
    """
    match = COMPANY_YEAR_PATTERN.match(pdf_file.stem)
    if not match:
        raise ValueError(
            f"Cannot parse company/year from filename: {pdf_file.name} "
            "(expected format: Company_10K_Year.pdf)"
        )
    return match.group(1), match.group(2)


def ingest_document(pdf_path: str, embeddings) -> dict:
    """Ingest a single PDF document and extract financial metrics.

    Args:
        pdf_path: Path to the PDF file to ingest.
        embeddings: Embeddings instance for processing.

    Returns:
        A dictionary containing company name, year, and extracted metrics.
    """
    pdf_file = Path(pdf_path)
    company, year = parse_company_year(pdf_file)

    converter = PDFToMarkdownConverter()
    markdown_file = converter.convert_pdf(str(pdf_file), str(MARKDOWN_DIR))

    chunks = chunk_markdown(markdown_file, embeddings)
    upload_chunks(chunks, embeddings, company, year, pdf_file.name)

    retriever = Retriever(embeddings)
    metrics = extract_financial_metrics(retriever, company, year)
    save_metrics(company, year, metrics, source_file=pdf_file.name)

    return {"company": company, "year": year, **metrics}


def ingest_directory(input_dir: str = str(PDFS_DIR)) -> list[dict]:
    """Ingest all PDF documents from a directory and extract financial metrics.

    Args:
        input_dir: Path to the directory containing PDF files. Defaults to PDFS_DIR.

    Returns:
        A list of dictionaries containing ingested documents with their metrics.
    """
    embeddings = get_embeddings()
    results = []

    for pdf_file in sorted(Path(input_dir).glob("*.pdf")):
        result = ingest_document(str(pdf_file), embeddings)
        results.append(result)

    return results


if __name__ == "__main__":
    ingested = ingest_directory()
    print(f"Ingested {len(ingested)} document(s):")
    for item in ingested:
        print(f"  - {item['company']} {item['year']}")

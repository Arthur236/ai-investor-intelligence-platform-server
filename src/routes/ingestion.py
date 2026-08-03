from fastapi import APIRouter, UploadFile

from ..config import PDFS_DIR
from ..embeddings.voyage_embeddings import get_embeddings
from ..ingestion.ingest_documents import ingest_document

router = APIRouter()


@router.post("/upload")
async def upload(file: UploadFile) -> dict:
    PDFS_DIR.mkdir(parents=True, exist_ok=True)
    destination = PDFS_DIR / file.filename

    contents = await file.read()
    destination.write_bytes(contents)

    return ingest_document(str(destination), get_embeddings())

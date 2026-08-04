import uuid
from types import SimpleNamespace

from langchain_core.documents import Document

from .create_index import get_collection

UPLOAD_BATCH_SIZE = 20


def upload_chunks(
    chunks: list[Document],
    embeddings,
    company: str,
    year: str,
    source_file: str,
) -> None:
    """Embed each chunk and upload it to Astra DB with company/year metadata."""
    collection = get_collection()

    documents = [
        {
            "_id": str(uuid.uuid4()),
            "company": company,
            "year": year,
            "source_file": source_file,
            "content": chunk.page_content,
            "$vector": embeddings.embed_query(chunk.page_content),
        }
        for chunk in chunks
    ]

    for start in range(0, len(documents), UPLOAD_BATCH_SIZE):
        batch = documents[start : start + UPLOAD_BATCH_SIZE]
        collection.insert_many(batch)


class Retriever:
    """Real vector-similarity retriever with optional company/year metadata filtering."""

    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.collection = get_collection()

    def invoke(
        self,
        query: str,
        company: str | None = None,
        year: str | None = None,
        top_k: int = 20,
    ) -> list[SimpleNamespace]:
        """Run a vector similarity search with optional metadata filtering."""
        query_vector = self.embeddings.embed_query(query)

        metadata_filter: dict = {}
        if company:
            metadata_filter["company"] = company
        if year:
            metadata_filter["year"] = year

        results = self.collection.find(
            metadata_filter,
            vector=query_vector,
            limit=top_k,
            include_similarity=True,
        )

        return [
            SimpleNamespace(
                page_content=doc["content"],
                metadata={
                    "company": doc.get("company"),
                    "year": doc.get("year"),
                    "source_file": doc.get("source_file"),
                },
                score=doc.get("$similarity"),
            )
            for doc in results
        ]

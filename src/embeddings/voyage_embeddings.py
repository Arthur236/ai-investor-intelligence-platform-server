from langchain_voyageai import VoyageAIEmbeddings

from ..config import VOYAGE_API_KEY, VOYAGE_MODEL

EMBEDDING_DIMENSIONS = 1024


def get_embeddings() -> VoyageAIEmbeddings:
    return VoyageAIEmbeddings(voyage_api_key=VOYAGE_API_KEY, model=VOYAGE_MODEL)


if __name__ == "__main__":
    embeddings = get_embeddings()
    vector = embeddings.embed_query("Revenue grew 12% year over year.")
    print(f"Embedded a sample string into {len(vector)} dimensions.")
    assert len(vector) == EMBEDDING_DIMENSIONS, (
        f"Expected {EMBEDDING_DIMENSIONS} dims, got {len(vector)}"
    )

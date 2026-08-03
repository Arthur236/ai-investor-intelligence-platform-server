from astrapy import Collection, DataAPIClient, Database
from astrapy.constants import VectorMetric

from ..config import (
    ASTRA_DB_API_ENDPOINT,
    ASTRA_DB_APPLICATION_TOKEN,
    ASTRA_DB_COLLECTION,
    ASTRA_DB_KEYSPACE,
)
from ..embeddings.voyage_embeddings import (
    EMBEDDING_DIMENSIONS,
)


def get_database() -> Database:
    """Return a configured Astra DB database client."""
    client = DataAPIClient(ASTRA_DB_APPLICATION_TOKEN)
    return client.get_database(ASTRA_DB_API_ENDPOINT, keyspace=ASTRA_DB_KEYSPACE)


def get_collection() -> Collection:
    """Get the vector collection from the Astra database."""
    return get_database().get_collection(ASTRA_DB_COLLECTION)


def ensure_collection() -> None:
    """Idempotent: create the vector-enabled collection if it doesn't exist."""
    database = get_database()
    database.create_collection(
        ASTRA_DB_COLLECTION,
        dimension=EMBEDDING_DIMENSIONS,
        metric=VectorMetric.COSINE,
        indexing={"deny": ["content"]},
        check_exists=False,
    )


if __name__ == "__main__":
    ensure_collection()
    ensure_collection()
    print(f"Collection '{ASTRA_DB_COLLECTION}' ready (idempotent create verified).")

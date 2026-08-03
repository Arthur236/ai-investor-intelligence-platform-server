from pathlib import Path

from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker

from ..config import MARKDOWN_DIR
from ..embeddings.voyage_embeddings import (
    get_embeddings,
)


def read_markdown(markdown_file: str) -> str:
    """Read markdown file and return its content as a string."""
    return Path(markdown_file).read_text(encoding="utf-8")


def chunk_markdown(markdown_file: str, embeddings) -> list[Document]:
    """Chunk markdown file into semantic documents using embeddings."""
    text = read_markdown(markdown_file)
    splitter = SemanticChunker(
        embeddings=embeddings, breakpoint_threshold_type="percentile"
    )
    return splitter.create_documents([text])


if __name__ == "__main__":
    sample_file = next(MARKDOWN_DIR.glob("*.md"))
    chunks = chunk_markdown(str(sample_file), get_embeddings())
    print(f"Chunked {sample_file.name} into {len(chunks)} chunks.")

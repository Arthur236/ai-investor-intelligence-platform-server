import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..embeddings.voyage_embeddings import get_embeddings
from ..llm.anthropic_client import get_chat_completion, stream_chat_completion
from ..vectorstore.astra_vectorstore import Retriever

router = APIRouter()

SYSTEM_PROMPT = (
    "You are an expert financial analyst. Answer the user's question using only "
    "the provided context from company 10-K filings. If the context doesn't "
    "contain the answer, say so."
)


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str
    company: str | None = None
    year: str | None = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    answer: str


def _build_system_prompt(request: ChatRequest) -> str:
    retriever = Retriever(get_embeddings())
    chunks = retriever.invoke(
        request.message, company=request.company, year=request.year, top_k=20
    )
    context = "\n\n".join(chunk.page_content for chunk in chunks)
    return f"{SYSTEM_PROMPT}\n\nContext:\n{context}"


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Handle chat requests and return a completed response."""
    system = _build_system_prompt(request)
    answer = get_chat_completion(system=system, message=request.message)

    return ChatResponse(answer=answer)


@router.post("/chat/stream")
def chat_stream(request: ChatRequest) -> StreamingResponse:
    """Handle chat requests and return a streaming response of tokens.

    Streams tokens from the LLM as Server-Sent Events (SSE) using the
    stream_chat_completion generator.
    """
    system = _build_system_prompt(request)

    def event_stream():
        for token in stream_chat_completion(system=system, message=request.message):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

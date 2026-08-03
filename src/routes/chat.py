from fastapi import APIRouter
from pydantic import BaseModel

from ..embeddings.voyage_embeddings import get_embeddings
from ..llm.anthropic_client import get_chat_completion
from ..vectorstore.astra_vectorstore import Retriever

router = APIRouter()

SYSTEM_PROMPT = (
    "You are an expert financial analyst. Answer the user's question using only "
    "the provided context from company 10-K filings. If the context doesn't "
    "contain the answer, say so."
)


class ChatRequest(BaseModel):
    message: str
    company: str | None = None
    year: str | None = None


class ChatResponse(BaseModel):
    answer: str


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    retriever = Retriever(get_embeddings())
    chunks = retriever.invoke(
        request.message, company=request.company, year=request.year, top_k=20
    )
    context = "\n\n".join(chunk.page_content for chunk in chunks)

    system = f"{SYSTEM_PROMPT}\n\nContext:\n{context}"
    answer = get_chat_completion(system=system, message=request.message)

    return ChatResponse(answer=answer)

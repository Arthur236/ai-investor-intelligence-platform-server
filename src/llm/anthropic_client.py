from collections.abc import Iterator
from typing import TypeVar

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from ..config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL

T = TypeVar("T", bound=BaseModel)


def get_client(model: str | None = None) -> ChatAnthropic:
    """Return an Anthropic chat client for the requested model."""
    return ChatAnthropic(
        model_name=model or ANTHROPIC_MODEL,
        api_key=ANTHROPIC_API_KEY,
        timeout=None,
        stop=None,
    )


def get_structured_completion[T](
    prompt: str, response_model: type[T], model: str | None = None
) -> T:
    """Return a structured completion parsed into the provided Pydantic model."""
    client = get_client(model).with_structured_output(response_model)
    return client.invoke(prompt)


def get_chat_completion(system: str, message: str, model: str | None = None) -> str:
    """Return a chat completion from the Anthropic client."""
    client = get_client(model)
    response = client.invoke(
        [SystemMessage(content=system), HumanMessage(content=message)]
    )
    return _extract_text(response.content)


def stream_chat_completion(
    system: str, message: str, model: str | None = None
) -> Iterator[str]:
    """Stream a chat completion from the Anthropic client."""
    client = get_client(model)
    for chunk in client.stream(
        [SystemMessage(content=system), HumanMessage(content=message)]
    ):
        text = _extract_text(chunk.content)
        if text:
            yield text


def _extract_text(content: str | list) -> str:
    if isinstance(content, str):
        return content
    return "".join(
        block.get("text", "")
        for block in content
        if isinstance(block, dict) and block.get("type") == "text"
    )

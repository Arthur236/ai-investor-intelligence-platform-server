from typing import TypeVar

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from ..config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL

T = TypeVar("T", bound=BaseModel)


def get_client(model: str | None = None) -> ChatAnthropic:
    return ChatAnthropic(model=model or ANTHROPIC_MODEL, api_key=ANTHROPIC_API_KEY)


def get_structured_completion(
    prompt: str, response_model: type[T], model: str | None = None
) -> T:
    client = get_client(model).with_structured_output(response_model)
    return client.invoke(prompt)


def get_chat_completion(system: str, message: str, model: str | None = None) -> str:
    client = get_client(model)
    response = client.invoke(
        [SystemMessage(content=system), HumanMessage(content=message)]
    )
    return response.content

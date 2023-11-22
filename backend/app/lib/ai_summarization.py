"""Module for ai generation."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from openai import OpenAI


class AIClient(ABC):
    """Abstract client for ai interactions."""

    @abstractmethod
    def summarize(self, *args) -> str:
        """Summarize the text."""
        raise NotImplementedError


def create_ai_client(client: Any) -> AIClient:
    """Create the ai client."""
    match client:
        case OpenAI():
            return OpenAIClient(client)
        case _:
            raise NotImplementedError


@dataclass
class OpenAIClient(AIClient):
    """OpenAI implementation."""

    ai_client: OpenAI

    def summarize(self, *args) -> str:
        """Summarize the text."""
        return 'Summary'

from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict], options: dict = None) -> str:
        pass

    @abstractmethod
    async def chat_stream(self, messages: list[dict], options: dict = None):
        pass

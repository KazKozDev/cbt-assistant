import httpx
import json
import re


from .base import BaseLLMClient


class ContentCleaner:
    @staticmethod
    def strip_think_tags(text: str) -> str:
        # Strip <think> tags if text is present
        if not text:
            return text
        return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


class OllamaClient(BaseLLMClient):
    """Client for generating completions using Ollama API."""

    def __init__(self, base_url: str, model: str):
        self.base_url = base_url
        self.model = model

    async def chat(self, messages: list[dict], options: dict = None, tools: list = None) -> dict:
        opts = options or {"temperature": 0.7, "top_p": 0.9, "num_predict": 1024}
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": opts,
        }
        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.base_url}/api/chat",
                json=payload,
            )
            resp.raise_for_status()
            message = resp.json().get("message", {})
            content = message.get("content", "")
            if content:
                message["content"] = ContentCleaner.strip_think_tags(content)
            return message

    async def chat_stream(self, messages: list[dict], options: dict = None, tools: list = None):
        opts = options or {"temperature": 0.7, "top_p": 0.9, "num_predict": 1024}
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": opts,
        }
        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json=payload,
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            yield data
                        except json.JSONDecodeError:
                            pass

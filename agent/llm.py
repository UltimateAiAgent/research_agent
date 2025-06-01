import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)  # Try .env in current/parent dirs

OPENAI_API_KEYYY = ""

class OpenAILLM:
    def __init__(self, model: str = "gpt-4o", api_key: str | None = None):
        self.api_key = OPENAI_API_KEYYY
        if not self.api_key:
            raise ValueError("Missing OPENAI_API_KEY in environment.")
        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def complete(self, prompt: str) -> str:
        """Single-turn prompt with user message"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def chat(self, messages: list[dict[str, str]]) -> str:
        """Multi-turn chat with multiple roles/messages"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        return response.choices[0].message.content
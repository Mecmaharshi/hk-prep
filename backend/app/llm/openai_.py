"""OpenAI, or any OpenAI-compatible service, through the official SDK. LLM_PROVIDER=openai in .env.

OPENAI_BASE_URL switches to a compatible service (Groq, OpenRouter, Ollama, Gemini's compatible
endpoint). For Azure OpenAI, ask: it needs a different client (openai.AzureOpenAI), ten lines.
"""

from __future__ import annotations

import os

from openai import OpenAI

DEFAULT_MODEL = "gpt-4.1"  # change to whatever the contest gives you, in .env (LLM_MODEL)
KEY_NAME = "OPENAI_API_KEY"
KEY_SET = bool(os.getenv(KEY_NAME))

_client = OpenAI(base_url=os.getenv("OPENAI_BASE_URL") or None)  # reads OPENAI_API_KEY itself


def ask(
    prompt: str, system: str | None = None, model: str = DEFAULT_MODEL, max_tokens: int = 4096
) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = _client.chat.completions.create(
        model=model, messages=messages, max_completion_tokens=max_tokens
    )
    return (response.choices[0].message.content or "").strip()

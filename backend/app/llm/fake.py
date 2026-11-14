"""Fake LLM: instant, free, and the same answer for the same question. Used when no key is set."""

from __future__ import annotations

import hashlib

DEFAULT_MODEL = "fake"
KEY_NAME = ""
KEY_SET = True

ANSWERS = [
    "This is a fake answer: set LLM_PROVIDER and a key in .env for a real one.",
    "Fake answer. The real LLM is not connected yet (see .env.example).",
    "No LLM key yet, so here is a stand-in answer that always works.",
]


def ask(
    prompt: str, system: str | None = None, model: str = DEFAULT_MODEL, max_tokens: int = 0
) -> str:
    number = int(hashlib.md5(prompt.encode()).hexdigest(), 16)
    return ANSWERS[number % len(ANSWERS)]

"""Claude, through Anthropic's official SDK. Chosen with LLM_PROVIDER=claude in .env."""

from __future__ import annotations

import os

import anthropic

DEFAULT_MODEL = "claude-opus-5-5"
KEY_NAME = "ANTHROPIC_API_KEY"
KEY_SET = bool(os.getenv(KEY_NAME))

_client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY itself


def ask(
    prompt: str, system: str | None = None, model: str = DEFAULT_MODEL, max_tokens: int = 4096
) -> str:
    response = _client.beta.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system or anthropic.NOT_GIVEN,
        messages=[{"role": "user", "content": prompt}],
        # If Claude's safety layer declines, Anthropic re-runs the request on another Claude
        # model inside the same call instead of failing. Remove these two lines to turn it off.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if response.stop_reason == "refusal":
        return "Claude declined to answer this request."
    return "".join(block.text for block in response.content if block.type == "text").strip()

"""The one place the team calls an LLM from.

    from backend.app.llm import ask
    answer = ask("Summarise this complaint in one line: ...")

The provider is chosen in .env (copy .env.example): LLM_PROVIDER=fake | claude | openai.
No key, or a provider that can't load, means fake answers plus a note, so the API and the
demo always work. Check which one is live: http://localhost:8000/board (LLM tab).
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from backend.app.llm import fake

log = logging.getLogger("uvicorn.error")
ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")

PROVIDERS = ("fake", "claude", "openai")
MAX_TOKENS = 4096


class LLMError(Exception):
    """The provider answered with an error. The message is safe to show the user."""


def _choose() -> tuple[object, str, str]:
    """Return (module, provider name, note). Falls back to fake with the reason in the note."""
    wanted = os.getenv("LLM_PROVIDER", "fake").strip().lower() or "fake"
    if wanted not in PROVIDERS:
        return fake, "fake", f"LLM_PROVIDER={wanted!r} isn't one of {', '.join(PROVIDERS)}"
    if wanted == "fake":
        return fake, "fake", "LLM_PROVIDER=fake in .env (or no .env yet)"
    try:
        if wanted == "claude":
            from backend.app.llm import claude as module
        else:
            from backend.app.llm import openai_ as module
    except Exception as error:  # noqa: BLE001 - a broken SDK must never take the API down
        log.warning("LLM provider %s didn't load, using fake answers: %s", wanted, error)
        return fake, "fake", f"{wanted} didn't load: {error}"
    if not module.KEY_SET:
        return fake, "fake", f"{wanted} chosen but {module.KEY_NAME} is empty in .env"
    return module, wanted, ""


_module, PROVIDER, NOTE = _choose()
MODEL = os.getenv("LLM_MODEL", "").strip() or getattr(_module, "DEFAULT_MODEL", "fake")
log.info("LLM answers come from %s (%s)", PROVIDER, MODEL)


def ask(prompt: str, system: str | None = None, max_tokens: int = MAX_TOKENS) -> str:
    """One question, one text answer. Raises LLMError if the provider fails."""
    try:
        return _module.ask(prompt, system=system, model=MODEL, max_tokens=max_tokens)
    except LLMError:
        raise
    except Exception as error:  # noqa: BLE001 - turn SDK errors into one readable message
        raise LLMError(f"{PROVIDER} ({MODEL}): {type(error).__name__}: {error}") from error


def status() -> dict:
    """For /board: which provider is live and why. Never includes a key."""
    return {
        "provider": PROVIDER,
        "model": MODEL,
        "wanted": os.getenv("LLM_PROVIDER", "fake") or "fake",
        "key_set": bool(getattr(_module, "KEY_SET", False)),
        "base_url": os.getenv("OPENAI_BASE_URL", "") if PROVIDER == "openai" else "",
        "note": NOTE,
        "env_file": (ROOT / ".env").exists(),
    }

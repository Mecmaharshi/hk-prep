"""The LLM module must work with no key and no network: the fake provider."""

from backend.app import llm
from backend.app.llm import fake


def test_fake_is_stable_and_free():
    assert fake.ask("hello") == fake.ask("hello")
    assert "fake" in fake.ask("hello").lower() or "LLM" in fake.ask("hello")


def test_status_never_leaks_a_key():
    status = llm.status()
    assert status["provider"] in llm.PROVIDERS
    assert set(status) >= {"provider", "model", "key_set", "note"}
    for value in status.values():
        assert not (isinstance(value, str) and value.startswith("sk-"))

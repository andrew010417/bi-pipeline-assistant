"""Provider selection and OpenAI call path, with the network mocked out."""

from types import SimpleNamespace

import pytest

from bi_assistant import config, llm, schemas

GUIDE = schemas.ParamGuide(summary="g", params=[])


@pytest.fixture
def clean_env(monkeypatch):
    for key in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "OPENAI_API_KEY", "BI_ASSISTANT_PROVIDER"):
        monkeypatch.delenv(key, raising=False)
    return monkeypatch


def test_no_keys_means_offline(clean_env):
    assert config._default_provider() is None


def test_openai_only(clean_env):
    clean_env.setenv("OPENAI_API_KEY", "sk-test")
    assert config._default_provider() == "openai"


def test_both_keys_respect_preference(clean_env):
    clean_env.setenv("OPENAI_API_KEY", "sk-test")
    clean_env.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    assert config._default_provider() == "anthropic"
    clean_env.setenv("BI_ASSISTANT_PROVIDER", "openai")
    assert config._default_provider() == "openai"


def test_empty_key_counts_as_missing(clean_env):
    clean_env.setenv("ANTHROPIC_API_KEY", "")
    clean_env.setenv("OPENAI_API_KEY", "sk-test")
    assert config._default_provider() == "openai"


def test_openai_call_returns_parsed_output(monkeypatch):
    calls = []

    class FakeResponses:
        def parse(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(status="completed", incomplete_details=None, output_parsed=GUIDE)

    monkeypatch.setattr(config, "PROVIDER", "openai")
    monkeypatch.setitem(llm._clients, "openai", SimpleNamespace(responses=FakeResponses()))
    assert llm.structured_call("sys", "user", schemas.ParamGuide) is GUIDE
    assert calls[0]["text_format"] is schemas.ParamGuide
    assert calls[0]["instructions"] == "sys"


def test_openai_truncation_raises(monkeypatch):
    class FakeResponses:
        def parse(self, **kwargs):
            return SimpleNamespace(
                status="incomplete",
                incomplete_details=SimpleNamespace(reason="max_output_tokens"),
                output_parsed=None,
            )

    monkeypatch.setattr(config, "PROVIDER", "openai")
    monkeypatch.setitem(llm._clients, "openai", SimpleNamespace(responses=FakeResponses()))
    with pytest.raises(llm.LLMError, match="잘렸습니다"):
        llm.structured_call("sys", "user", schemas.ParamGuide)


def test_no_provider_raises(monkeypatch):
    monkeypatch.setattr(config, "PROVIDER", None)
    with pytest.raises(llm.LLMError):
        llm.structured_call("sys", "user", schemas.ParamGuide)

"""Smoke test: the Streamlit app renders and the offline parameter guide works."""

from streamlit.testing.v1 import AppTest

from bi_assistant import config


def test_app_offline(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(config, "PROVIDER", None)
    at = AppTest.from_file("../app.py", default_timeout=30).run()
    assert not at.exception
    assert len(at.tabs) == 3
    # Parameter guide tab: click the (offline-capable) button
    guide_button = [b for b in at.button if "parameter" in b.label][0]
    guide_button.click().run()
    assert not at.exception
    assert any("오프라인 모드" in i.value for i in at.info)

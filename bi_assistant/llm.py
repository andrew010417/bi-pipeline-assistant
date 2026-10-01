"""Single entry point for LLM calls.

Every feature goes through `structured_call`, so supporting another provider
(e.g. an on-prem model for company code) only touches this file.
Supported: Anthropic Claude and OpenAI GPT, chosen by `config.PROVIDER`.
"""

from typing import TypeVar

from pydantic import BaseModel

from . import config

T = TypeVar("T", bound=BaseModel)

_clients: dict = {}


class LLMError(RuntimeError):
    pass


def _client(provider: str):
    if provider not in _clients:
        if provider == "anthropic":
            import anthropic

            _clients[provider] = anthropic.Anthropic()
        else:
            import openai

            _clients[provider] = openai.OpenAI()
    return _clients[provider]


def structured_call(system: str, user: str, schema: type[T], effort: str | None = None) -> T:
    """Ask the active provider for a response that validates against `schema`."""
    if config.PROVIDER == "anthropic":
        return _anthropic_call(system, user, schema, effort or config.EFFORT)
    if config.PROVIDER == "openai":
        return _openai_call(system, user, schema)
    raise LLMError("API 키가 설정되지 않았습니다. .env에 ANTHROPIC_API_KEY 또는 OPENAI_API_KEY를 넣어주세요.")


# ---------- Anthropic ----------

def _anthropic_call(system: str, user: str, schema: type[T], effort: str) -> T:
    import anthropic

    client = _client("anthropic")
    try:
        response = client.beta.messages.parse(
            model=config.model_for("anthropic"),
            max_tokens=config.MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": user}],
            output_format=schema,
            output_config={"effort": effort},
            cache_control={"type": "ephemeral"},
            # Re-run a policy-declined request on Anthropic's recommended fallback model.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
    except anthropic.AuthenticationError as e:
        raise LLMError("Claude API 키가 없거나 잘못되었습니다. .env의 ANTHROPIC_API_KEY를 확인하세요.") from e
    except anthropic.RateLimitError as e:
        raise LLMError("요청 한도를 초과했습니다. 잠시 후 다시 시도하세요.") from e
    except anthropic.APIStatusError as e:
        raise LLMError(f"Claude API 오류 ({e.status_code}): {e.message}") from e
    except anthropic.APIConnectionError as e:
        raise LLMError("Claude API에 연결할 수 없습니다. 네트워크/프록시 설정을 확인하세요.") from e

    if response.stop_reason == "refusal":
        raise LLMError("모델이 요청을 거절했습니다.")
    if response.stop_reason == "max_tokens":
        raise LLMError("응답이 max_tokens에서 잘렸습니다. BI_ASSISTANT_MAX_TOKENS를 늘리거나 입력을 나눠주세요.")
    if response.parsed_output is None:
        raise LLMError("구조화된 응답을 파싱하지 못했습니다.")
    return response.parsed_output


# ---------- OpenAI ----------

def _openai_call(system: str, user: str, schema: type[T]) -> T:
    import openai

    client = _client("openai")
    try:
        response = client.responses.parse(
            model=config.model_for("openai"),
            instructions=system,
            input=user,
            text_format=schema,
            max_output_tokens=config.MAX_TOKENS,
        )
    except openai.AuthenticationError as e:
        raise LLMError("OpenAI API 키가 없거나 잘못되었습니다. .env의 OPENAI_API_KEY를 확인하세요.") from e
    except openai.RateLimitError as e:
        raise LLMError("요청 한도를 초과했거나 크레딧이 부족합니다. platform.openai.com의 Billing을 확인하세요.") from e
    except openai.NotFoundError as e:
        raise LLMError(f"모델을 찾을 수 없습니다: {config.model_for('openai')}. .env의 OPENAI_MODEL을 확인하세요.") from e
    except openai.APIStatusError as e:
        raise LLMError(f"OpenAI API 오류 ({e.status_code}): {e.message}") from e
    except openai.APIConnectionError as e:
        raise LLMError("OpenAI API에 연결할 수 없습니다. 네트워크/프록시 설정을 확인하세요.") from e

    if response.status == "incomplete":
        reason = getattr(response.incomplete_details, "reason", "")
        if reason == "max_output_tokens":
            raise LLMError("응답이 잘렸습니다. BI_ASSISTANT_MAX_TOKENS를 늘리거나 입력을 나눠주세요.")
        raise LLMError(f"응답이 완료되지 않았습니다 ({reason}).")
    if response.output_parsed is None:
        raise LLMError("모델이 요청을 거절했거나 구조화된 응답을 파싱하지 못했습니다.")
    return response.output_parsed

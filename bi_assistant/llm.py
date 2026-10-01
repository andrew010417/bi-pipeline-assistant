"""Single entry point for LLM calls.

Every feature goes through `structured_call`, so swapping the provider
(e.g. an on-prem model for company code) only touches this file.
"""

from typing import TypeVar

import anthropic
from pydantic import BaseModel

from . import config

T = TypeVar("T", bound=BaseModel)

_client: anthropic.Anthropic | None = None


class LLMError(RuntimeError):
    pass


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


def structured_call(system: str, user: str, schema: type[T], effort: str | None = None) -> T:
    """Ask Claude for a response that validates against `schema`."""
    try:
        response = get_client().beta.messages.parse(
            model=config.MODEL,
            max_tokens=config.MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": user}],
            output_format=schema,
            output_config={"effort": effort or config.EFFORT},
            cache_control={"type": "ephemeral"},
            # Re-run a policy-declined request on Anthropic's recommended fallback model.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
    except anthropic.AuthenticationError as e:
        raise LLMError("API 키가 없거나 잘못되었습니다. .env의 ANTHROPIC_API_KEY를 확인하세요.") from e
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

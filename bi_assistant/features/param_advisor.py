"""Feature 3: point non-experts at the parameters worth changing, with candidate values."""

import re

from .. import knowledge, llm
from ..config import OUTPUT_LANGUAGE
from ..loader import PipelineSource
from ..schemas import ParamAdvice, ParamCandidate, ParamGuide, PipelineIR
from ..static_scan import scan_parameters

SYSTEM = f"""You help researchers who are NOT bioinformatics experts tune an analysis pipeline.
For the given pipeline, list the parameters a user is most likely to need to change.

Rules:
- Only list parameters that actually appear in the code (including hard-coded thresholds
  inside expressions such as `subset = percent.mt < 5`). Use the exact line number.
- Rank by impact on the biological result: `high` = changes which cells/genes are kept or how
  they are grouped; `low` = cosmetic or speed-only.
- Give 2-4 candidate values each, with when to use them (tissue type, dataset size,
  sequencing depth, etc.). Prefer the curated hints below when they apply.
- Explain in plain language with no jargon left unexplained.
- Write all explanation fields in {OUTPUT_LANGUAGE}. Keep code identifiers and values as-is.

Curated hints:
{knowledge.as_text("param_hints")}"""


def advise(source: PipelineSource, ir: PipelineIR) -> ParamGuide:
    user = (
        f"<structure>\n{ir.model_dump_json(indent=1)}\n</structure>\n\n"
        f"<code>\n{source.numbered()}\n</code>"
    )
    return llm.structured_call(SYSTEM, user, ParamGuide)


def offline_guide(source: PipelineSource) -> ParamGuide:
    """No-LLM fallback: static scan + curated hints. Only covers parameters in param_hints.yaml."""
    hints = knowledge.load("param_hints")
    advice = []
    for p in scan_parameters(source.code, source.language):
        hint = hints.get(p.name)
        if hint is None:
            continue
        advice.append(ParamAdvice(
            name=p.name,
            function=p.function,
            line=p.line,
            current_value=p.value,
            step="",
            importance=hint["importance"],
            what_it_does=hint["what"],
            effect_of_increase="",
            effect_of_decrease="",
            candidates=[ParamCandidate(value=c, when_to_use="") for c in hint["candidates"]],
        ))
    # Also catch thresholds written inside expressions, e.g. subset = percent.mt < 5
    seen = {(a.name, a.line) for a in advice}
    for lineno, line in enumerate(source.code.splitlines(), 1):
        code_part = line.split("#", 1)[0]
        for name, hint in hints.items():
            pattern = rf"(?<!\w){re.escape(name)}\s*[<>]=?\s*[-\w.]+"
            comparisons = re.findall(pattern, code_part)
            if comparisons and (name, lineno) not in seen:
                advice.append(ParamAdvice(
                    name=name, function="(expression)", line=lineno, current_value=" & ".join(comparisons),
                    step="", importance=hint["importance"], what_it_does=hint["what"],
                    effect_of_increase="", effect_of_decrease="",
                    candidates=[ParamCandidate(value=c, when_to_use="") for c in hint["candidates"]],
                ))
                seen.add((name, lineno))
    order = {"high": 0, "medium": 1, "low": 2}
    advice.sort(key=lambda a: (order[a.importance], a.line))
    return ParamGuide(summary="오프라인 모드: 정적 분석 + 내장 힌트 기반 결과입니다 (API 키를 설정하면 더 자세한 설명이 나옵니다).", params=advice)

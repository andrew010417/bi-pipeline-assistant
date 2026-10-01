"""Common core: source code -> PipelineIR."""

from . import knowledge, llm
from .config import OUTPUT_LANGUAGE
from .loader import PipelineSource
from .schemas import PipelineIR
from .static_scan import scan_parameters

SYSTEM = f"""You are a senior bioinformatician who reads analysis pipelines written in R or Python.
Split the given pipeline into ordered analysis steps and describe each one.

Rules:
- Line numbers in the input are given as `  12| code`. Cite them exactly.
- `category` must be one of the canonical step ids below (pick the analysis type that fits),
  or `other` if nothing fits.
- List every tunable argument (thresholds, counts, resolutions, method names) under the step that uses it.
  A pre-computed list of keyword arguments is provided; use it, and add positional or
  hard-coded values it missed (e.g. `subset = nFeature_RNA > 200`).
- Write `summary` and `description` fields in {OUTPUT_LANGUAGE}. Keep code identifiers as-is.

Canonical steps:
{knowledge.as_text("canonical_steps")}"""


def parse_pipeline(source: PipelineSource) -> PipelineIR:
    scanned = scan_parameters(source.code, source.language)
    hints = "\n".join(f"line {p.line}: {p.function}({p.name}={p.value})" for p in scanned) or "(none)"
    user = (
        f"File: {source.name} (detected language: {source.language})\n\n"
        f"<code>\n{source.numbered()}\n</code>\n\n"
        f"<keyword_arguments_found_by_static_scan>\n{hints}\n</keyword_arguments_found_by_static_scan>"
    )
    return llm.structured_call(SYSTEM, user, PipelineIR)

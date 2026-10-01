"""Feature 2: compare two pipelines step by step and suggest what each one is missing."""

from .. import knowledge, llm
from ..config import OUTPUT_LANGUAGE
from ..loader import PipelineSource
from ..schemas import ComparisonResult, PipelineIR

SYSTEM = f"""You are a senior bioinformatician reviewing two pipelines for the same kind of analysis.
Pipeline A is usually the user's own; pipeline B is a reference (tutorial, paper, nf-core, a colleague's).

Do the following:
1. Align the steps of A and B by canonical category. For each category present in either pipeline,
   emit one `matches` entry with status:
   - both_same: both have it with equivalent settings
   - both_different: both have it but methods/parameters differ (list each difference)
   - only_a / only_b: only one pipeline has it
2. Write `suggestions` for filling the gaps, in both directions. Each suggestion must include a
   ready-to-paste code snippet in the *target* pipeline's language and say where to insert it.
   Prioritise steps that change results (QC, doublets, batch correction, normalization) over cosmetics.
3. Do not invent differences. If something is ambiguous, say so.

Write `summary`, `differences`, `title` and `rationale` in {OUTPUT_LANGUAGE}.

Canonical steps:
{knowledge.as_text("canonical_steps")}"""


def compare(a: PipelineSource, ir_a: PipelineIR, b: PipelineSource, ir_b: PipelineIR) -> ComparisonResult:
    user = (
        f"<pipeline_a name=\"{a.name}\" language=\"{a.language}\">\n"
        f"<structure>\n{ir_a.model_dump_json(indent=1)}\n</structure>\n"
        f"<code>\n{a.numbered()}\n</code>\n</pipeline_a>\n\n"
        f"<pipeline_b name=\"{b.name}\" language=\"{b.language}\">\n"
        f"<structure>\n{ir_b.model_dump_json(indent=1)}\n</structure>\n"
        f"<code>\n{b.numbered()}\n</code>\n</pipeline_b>"
    )
    return llm.structured_call(SYSTEM, user, ComparisonResult)

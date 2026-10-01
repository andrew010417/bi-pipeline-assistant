"""Feature 1: convert a pipeline between R and Python.

`convert` does one translation pass. `verify_and_fix` adds the agent loop:
run the converted code, and on failure send the error back for a fix.
"""

import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from .. import knowledge, llm
from ..config import OUTPUT_LANGUAGE
from ..loader import PipelineSource
from ..schemas import ConversionResult, PipelineIR

SYSTEM = f"""You are an expert at porting bioinformatics pipelines between R and Python.
Produce a complete, runnable script in the target language that reproduces the original analysis.

Rules:
- Keep the same step order, parameters, thresholds, file paths and outputs.
- Prefer the package equivalents in the mapping table below. When there is no faithful
  equivalent, say so in `caveats` and choose the closest option.
- Watch for orientation differences (genes x cells vs cells x genes) and default-value
  differences between packages; set parameters explicitly so results match.
- Add a short comment above each step naming the original step.
- Write `caveats` and mapping `note` fields in {OUTPUT_LANGUAGE}.

Package mapping table:
{knowledge.as_text("package_map")}"""

FIX_SYSTEM = SYSTEM + """

You are now fixing a previously converted script that failed when executed.
Return the full corrected script, not a diff."""

INTERPRETERS = {"Python": ["python3"], "R": ["Rscript"]}
EXTENSIONS = {"Python": ".py", "R": ".R"}


def target_for(language: str) -> str:
    return "Python" if language == "R" else "R"


def convert(source: PipelineSource, ir: PipelineIR, target: str | None = None) -> ConversionResult:
    target = target or target_for(source.language)
    user = (
        f"Convert this {source.language} pipeline to {target}.\n\n"
        f"<structure>\n{ir.model_dump_json(indent=1)}\n</structure>\n\n"
        f"<code>\n{source.code}\n</code>"
    )
    return llm.structured_call(SYSTEM, user, ConversionResult)


@dataclass
class RunResult:
    ok: bool
    stdout: str
    stderr: str


@dataclass
class VerifyLog:
    rounds: list[RunResult] = field(default_factory=list)
    final: ConversionResult | None = None


def run_code(code: str, language: str, workdir: str | Path | None = None, timeout: int = 600) -> RunResult:
    """Execute a script. Only run code you trust: this has full access to the machine."""
    cmd = INTERPRETERS[language]
    if shutil.which(cmd[0]) is None:
        return RunResult(False, "", f"{cmd[0]} not found on PATH")
    workdir = Path(workdir) if workdir else Path(tempfile.mkdtemp(prefix="bi_assistant_"))
    script = workdir / f"converted{EXTENSIONS[language]}"
    script.write_text(code, encoding="utf-8")
    try:
        proc = subprocess.run(
            [*cmd, script.name], cwd=workdir, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return RunResult(False, "", f"timed out after {timeout}s")
    return RunResult(proc.returncode == 0, proc.stdout[-4000:], proc.stderr[-4000:])


def verify_and_fix(
    source: PipelineSource,
    result: ConversionResult,
    workdir: str | Path | None = None,
    max_rounds: int = 3,
) -> VerifyLog:
    """Run the converted script; on error, ask Claude to fix it and retry."""
    log = VerifyLog(final=result)
    for _ in range(max_rounds):
        run = run_code(log.final.code, log.final.target_language, workdir)
        log.rounds.append(run)
        if run.ok or "not found on PATH" in run.stderr:
            break
        user = (
            f"Original {source.language} pipeline:\n<code>\n{source.code}\n</code>\n\n"
            f"Converted {log.final.target_language} script:\n<converted>\n{log.final.code}\n</converted>\n\n"
            f"It failed with:\n<stderr>\n{run.stderr}\n</stderr>"
        )
        log.final = llm.structured_call(FIX_SYSTEM, user, ConversionResult)
    return log

"""Feature wiring tests with the LLM call mocked out."""

from pathlib import Path

from bi_assistant import llm, parser, schemas
from bi_assistant.features import comparator, converter, param_advisor
from bi_assistant.loader import load_file

EXAMPLES = Path(__file__).parent.parent / "examples"

IR = schemas.PipelineIR(language="R", analysis_type="scRNA-seq", summary="s", steps=[])


def fake_call(responses, calls):
    def _call(system, user, schema, effort=None):
        calls.append((system, user, schema))
        return responses[schema]
    return _call


def test_parser_sends_numbered_code_and_scan_hints(monkeypatch):
    calls = []
    monkeypatch.setattr(llm, "structured_call", fake_call({schemas.PipelineIR: IR}, calls))
    src = load_file(EXAMPLES / "scrna_seurat.R")
    assert parser.parse_pipeline(src) is IR
    _, user, _ = calls[0]
    assert "  23| seu <- FindClusters" in user
    assert "line 23: FindClusters(resolution=0.5)" in user


def test_converter_targets_other_language(monkeypatch):
    result = schemas.ConversionResult(
        target_language="Python", code="print(1)", package_mapping=[], caveats=[], install_hint="pip install scanpy"
    )
    calls = []
    monkeypatch.setattr(llm, "structured_call", fake_call({schemas.ConversionResult: result}, calls))
    src = load_file(EXAMPLES / "scrna_seurat.R")
    assert converter.convert(src, IR) is result
    assert "Convert this R pipeline to Python" in calls[0][1]


def test_verify_and_fix_retries_on_failure(monkeypatch, tmp_path):
    bad = schemas.ConversionResult(
        target_language="Python", code="raise SystemExit('boom')", package_mapping=[], caveats=[], install_hint=""
    )
    good = bad.model_copy(update={"code": "print('ok')"})
    calls = []
    monkeypatch.setattr(llm, "structured_call", fake_call({schemas.ConversionResult: good}, calls))
    src = load_file(EXAMPLES / "scrna_seurat.R")
    log = converter.verify_and_fix(src, bad, workdir=tmp_path)
    assert [r.ok for r in log.rounds] == [False, True]
    assert "boom" in calls[0][1]
    assert log.final is good


def test_comparator_and_advisor_wiring(monkeypatch):
    cmp = schemas.ComparisonResult(summary="x", matches=[], suggestions=[])
    guide = schemas.ParamGuide(summary="g", params=[])
    calls = []
    monkeypatch.setattr(llm, "structured_call", fake_call(
        {schemas.ComparisonResult: cmp, schemas.ParamGuide: guide}, calls))
    a = load_file(EXAMPLES / "scrna_seurat.R")
    b = load_file(EXAMPLES / "scrna_scanpy.py")
    assert comparator.compare(a, IR, b, IR) is cmp
    assert "<pipeline_b name=\"scrna_scanpy.py\"" in calls[0][1]
    assert param_advisor.advise(a, IR) is guide

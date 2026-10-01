"""Tests that run without an API key."""

import json
from pathlib import Path

import pytest
from anthropic.lib._parse._transform import transform_schema

from bi_assistant import schemas
from bi_assistant.features import param_advisor
from bi_assistant.loader import detect_language, load_file, load_text
from bi_assistant.static_scan import scan_parameters

EXAMPLES = Path(__file__).parent.parent / "examples"


def test_detect_language():
    assert detect_language("a.R") == "R"
    assert detect_language("a.ipynb") == "Python"
    assert detect_language("noext", "x <- library(Seurat)") == "R"


def test_rmd_keeps_only_code_chunks():
    raw = "# Title\ntext\n```{r}\nx <- 1\n```\nmore text\n```{r setup}\ny <- 2\n```\n"
    assert load_text("a.Rmd", raw).code == "x <- 1\ny <- 2"


def test_notebook_keeps_only_code_cells():
    nb = {"cells": [
        {"cell_type": "markdown", "source": ["# hi"]},
        {"cell_type": "code", "source": ["import scanpy as sc\n", "sc.settings.verbosity = 3"]},
    ]}
    src = load_text("a.ipynb", json.dumps(nb))
    assert src.language == "Python"
    assert "import scanpy" in src.code and "# hi" not in src.code


def test_scan_r_example():
    src = load_file(EXAMPLES / "scrna_seurat.R")
    found = {(p.name, p.value) for p in scan_parameters(src.code, src.language)}
    assert ("resolution", "0.5") in found
    assert ("nfeatures", "2000") in found
    assert ("dims", "1:10") in found
    by_name = {p.name: p for p in scan_parameters(src.code, src.language)}
    assert by_name["resolution"].function == "FindClusters"


def test_scan_python_example():
    src = load_file(EXAMPLES / "scrna_scanpy.py")
    params = scan_parameters(src.code, src.language)
    by_name = {p.name: p for p in params}
    assert by_name["resolution"].value == "0.8"
    assert by_name["resolution"].function == "sc.tl.leiden"
    assert by_name["n_pcs"].value == "40"


def test_offline_guide_finds_key_qc_params():
    src = load_file(EXAMPLES / "scrna_seurat.R")
    guide = param_advisor.offline_guide(src)
    names = {p.name for p in guide.params}
    assert {"resolution", "dims", "nFeature_RNA", "percent.mt"} <= names
    assert guide.params[0].importance == "high"


@pytest.mark.parametrize("model", [
    schemas.PipelineIR, schemas.ConversionResult, schemas.ComparisonResult, schemas.ParamGuide,
])
def test_schemas_are_valid_for_structured_outputs(model):
    # The SDK applies this transform before sending output_format to the API.
    transform_schema(model.model_json_schema())

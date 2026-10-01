"""Pydantic models shared by all features.

`PipelineIR` is the common intermediate representation: every feature
first turns source code into this structure, then works on it.
"""

from typing import Literal

from pydantic import BaseModel, Field

Language = Literal["R", "Python", "Other"]


# ---------- Common core: Pipeline IR ----------

class Parameter(BaseModel):
    name: str
    value: str = Field(description="Current value as written in the code")
    function: str = Field(description="Function/method the parameter is passed to")
    line: int = Field(description="1-based line number in the source")


class Step(BaseModel):
    id: str = Field(description="Short unique id, e.g. 's1'")
    name: str
    category: str = Field(description="Canonical category id from the canonical step list")
    description: str
    start_line: int
    end_line: int
    tools: list[str] = Field(description="Packages/functions used, e.g. 'Seurat::NormalizeData'")
    inputs: list[str]
    outputs: list[str]
    parameters: list[Parameter]


class PipelineIR(BaseModel):
    language: Language
    analysis_type: str = Field(description="e.g. 'scRNA-seq', 'bulk RNA-seq DE', 'variant calling'")
    summary: str
    steps: list[Step]


# ---------- Feature 1: conversion ----------

class PackageMapping(BaseModel):
    source: str
    target: str
    note: str


class ConversionResult(BaseModel):
    target_language: Language
    code: str
    package_mapping: list[PackageMapping]
    caveats: list[str] = Field(description="Behavioral differences the user must know about")
    install_hint: str = Field(description="Command to install required packages")


# ---------- Feature 2: comparison ----------

class StepMatch(BaseModel):
    category: str
    status: Literal["both_same", "both_different", "only_a", "only_b"]
    a_step: str = Field(description="Step name in pipeline A, or empty string")
    b_step: str = Field(description="Step name in pipeline B, or empty string")
    differences: list[str]


class Suggestion(BaseModel):
    target: Literal["A", "B"] = Field(description="Which pipeline should receive this change")
    title: str
    rationale: str
    insert_after_step: str = Field(description="Step name after which to insert, or empty string")
    code_snippet: str


class ComparisonResult(BaseModel):
    summary: str
    matches: list[StepMatch]
    suggestions: list[Suggestion]


# ---------- Feature 3: parameter guide ----------

class ParamCandidate(BaseModel):
    value: str
    when_to_use: str


class ParamAdvice(BaseModel):
    name: str
    function: str
    line: int
    current_value: str
    step: str
    importance: Literal["high", "medium", "low"]
    what_it_does: str = Field(description="Plain-language explanation for non-experts")
    effect_of_increase: str
    effect_of_decrease: str
    candidates: list[ParamCandidate]


class ParamGuide(BaseModel):
    summary: str
    params: list[ParamAdvice]

"""Read pipeline files of various formats into plain source text."""

import json
from dataclasses import dataclass
from pathlib import Path

EXTENSION_LANGUAGE = {
    ".py": "Python",
    ".ipynb": "Python",
    ".r": "R",
    ".rmd": "R",
    ".qmd": "R",
    ".smk": "Python",  # Snakemake rules embed Python
    ".nf": "Other",
    ".sh": "Other",
}


@dataclass
class PipelineSource:
    name: str
    language: str
    code: str

    def numbered(self) -> str:
        """Source with line numbers, so the LLM can cite exact locations."""
        return "\n".join(f"{i:>4}| {line}" for i, line in enumerate(self.code.splitlines(), 1))


def detect_language(filename: str, code: str = "") -> str:
    lang = EXTENSION_LANGUAGE.get(Path(filename).suffix.lower())
    if lang:
        return lang
    if "<-" in code or "library(" in code:
        return "R"
    if "import " in code or "def " in code:
        return "Python"
    return "Other"


def notebook_to_code(raw: str) -> str:
    nb = json.loads(raw)
    cells = [
        "".join(cell.get("source", []))
        for cell in nb.get("cells", [])
        if cell.get("cell_type") == "code"
    ]
    return "\n\n".join(cells)


def rmd_to_code(raw: str) -> str:
    """Keep only code chunks from R Markdown / Quarto."""
    out, inside = [], False
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith("```{r") or stripped.startswith("```{python"):
            inside = True
            continue
        if inside and stripped.startswith("```"):
            inside = False
            continue
        if inside:
            out.append(line)
    return "\n".join(out)


def load_text(name: str, raw: str) -> PipelineSource:
    suffix = Path(name).suffix.lower()
    if suffix == ".ipynb":
        code = notebook_to_code(raw)
    elif suffix in (".rmd", ".qmd"):
        code = rmd_to_code(raw)
    else:
        code = raw
    return PipelineSource(name=name, language=detect_language(name, code), code=code)


def load_file(path: str | Path) -> PipelineSource:
    path = Path(path)
    return load_text(path.name, path.read_text(encoding="utf-8"))

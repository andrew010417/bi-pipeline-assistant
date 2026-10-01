"""Offline parameter scanner (no LLM).

Finds `func(arg = value)` style keyword arguments so the parameter guide
still shows something useful without an API key, and gives the LLM a
precise list of locations to work from.
"""

import ast
import re

from .schemas import Parameter

# name=value inside a call, R or Python style. Values stop at ',' or ')'.
_R_KWARG = re.compile(r"([A-Za-z_.][\w.]*)\s*=\s*([^,()=]+(?:\([^()]*\))?)")
_R_CALL = re.compile(r"([A-Za-z_.][\w.:]*)\s*\(")


def _scan_python(code: str) -> list[Parameter]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return _scan_regex(code)
    params = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = ast.unparse(node.func)
            for kw in node.keywords:
                if kw.arg is None:
                    continue
                params.append(Parameter(
                    name=kw.arg,
                    value=ast.unparse(kw.value),
                    function=func,
                    line=kw.value.lineno,
                ))
    return sorted(params, key=lambda p: p.line)


def _scan_regex(code: str) -> list[Parameter]:
    """Line-based scan for R (and unparsable Python).

    Tracks the most recent open call so arguments on continuation lines
    of a multi-line call are attributed to it.
    """
    params = []
    current_func, depth = "?", 0
    for lineno, line in enumerate(code.splitlines(), 1):
        stripped = line.split("#", 1)[0]
        calls = _R_CALL.findall(stripped)
        if calls and depth == 0:
            current_func = calls[0]
        if depth > 0 or calls:
            for name, value in _R_KWARG.findall(stripped):
                params.append(Parameter(name=name, value=value.strip(), function=current_func, line=lineno))
        depth = max(depth + stripped.count("(") - stripped.count(")"), 0)
    return params


def scan_parameters(code: str, language: str) -> list[Parameter]:
    if language == "Python":
        return _scan_python(code)
    return _scan_regex(code)

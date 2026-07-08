"""Answer quality checks — groundedness verification.

Groundedness = do the numeric claims in the natural-language answer actually
appear in the SQL result set? This is a cheap, deterministic guard against
LLM hallucination on top of the grounded-summarization prompt.
"""

from __future__ import annotations

import re

_NUMBER_RE = re.compile(r"-?\d[\d,]*\.?\d*")
# List/ranking markers like "1.", "2)", "3:" followed by a word — formatting, not data.
_ORDINAL_RE = re.compile(r"(?<!\d)\d+\s*[.):]\s+(?=[A-Za-z$])")
# Number with a magnitude suffix, e.g. "4.1K", "$3.2M".
_SUFFIX_RE = re.compile(r"(-?\d[\d,]*\.?\d*)\s*([kKmMbB])\b")
_SUFFIX_MULT = {"k": 1e3, "m": 1e6, "b": 1e9}


def _extract_numbers(text: str) -> list[float]:
    numbers: list[float] = []

    # Expand magnitude suffixes first (4.1K -> 4100) so they compare to raw data.
    for value, suffix in _SUFFIX_RE.findall(text):
        try:
            numbers.append(float(value.replace(",", "")) * _SUFFIX_MULT[suffix.lower()])
        except ValueError:
            continue

    stripped = _ORDINAL_RE.sub(" ", text)
    stripped = _SUFFIX_RE.sub(" ", stripped)
    for match in _NUMBER_RE.findall(stripped):
        cleaned = match.replace(",", "")
        try:
            numbers.append(float(cleaned))
        except ValueError:
            continue
    return numbers


def _result_numbers(rows: list[tuple]) -> list[float]:
    numbers: list[float] = []
    for row in rows:
        for cell in row:
            if isinstance(cell, bool):
                continue
            if isinstance(cell, (int, float)):
                numbers.append(float(cell))
            elif isinstance(cell, str):
                for match in _NUMBER_RE.findall(cell):
                    try:
                        numbers.append(float(match.replace(",", "")))
                    except ValueError:
                        continue
    return numbers


def _matches(claim: float, available: list[float], tol: float = 0.02) -> bool:
    for value in available:
        if claim == value:
            return True
        # relative tolerance for rounding (e.g. 4134.93 vs 4135)
        denom = max(abs(value), abs(claim), 1.0)
        if abs(claim - value) / denom <= tol:
            return True
        # integer rounding match
        if round(claim) == round(value):
            return True
    return False


def groundedness_score(answer: str, rows: list[tuple]) -> float:
    """Fraction of numeric claims in the answer that are supported by the data.

    Returns 1.0 when the answer makes no numeric claims (nothing to hallucinate)
    or when every claim is supported. Years (1900-2100) are ignored as they are
    usually part of the question context, not a data claim.
    """
    claims = [n for n in _extract_numbers(answer) if not (1900 <= n <= 2100 and n == int(n))]
    if not claims:
        return 1.0

    available = _result_numbers(rows)
    if not available:
        # No numeric data to verify against (e.g. purely textual results) —
        # can't disprove the claims, so don't penalize.
        return 1.0

    supported = sum(1 for c in claims if _matches(c, available))
    return supported / len(claims)


def groundedness_label(score: float) -> str:
    if score >= 0.999:
        return "High"
    if score >= 0.6:
        return "Medium"
    return "Low"

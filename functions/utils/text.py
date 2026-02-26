from __future__ import annotations

import json
from typing import Any, Iterable, List, Optional


def safe_str(x: Any) -> str:
    if x is None:
        return ""
    return str(x)


def truncate(text: str, n: int) -> str:
    text = safe_str(text)
    if n <= 0:
        return ""
    if len(text) <= n:
        return text
    return text[: max(0, n - 1)] + "…"


def evidence_to_display(evidence: Any, sep: str = " | ") -> str:
    """
    evidence can be list[str] or already string; return a display-friendly string.
    """
    if evidence is None:
        return ""
    if isinstance(evidence, list):
        return sep.join([safe_str(e).strip() for e in evidence if safe_str(e).strip()])
    return safe_str(evidence).strip()


def evidence_to_export(evidence: Any, mode: str = "pipe") -> str:
    """
    mode:
      - "pipe" -> join list items with |
      - "json" -> json string for list
    """
    if evidence is None:
        return ""
    if isinstance(evidence, list):
        cleaned = [safe_str(e).strip() for e in evidence if safe_str(e).strip()]
        if mode == "json":
            return json.dumps(cleaned, ensure_ascii=False)
        return "|".join(cleaned)
    return safe_str(evidence).strip()
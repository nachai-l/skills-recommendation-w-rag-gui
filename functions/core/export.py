from __future__ import annotations

from io import BytesIO
from typing import Any, Dict, List, Optional

import pandas as pd

from functions.utils.text import evidence_to_export, safe_str


EXPORT_COLUMNS = [
    "skill_id",
    "skill_name",
    "source",
    "relevance_score",
    "reasoning",
    "evidence",
    "skill_text",
    "Foundational_Criteria",
    "Intermediate_Criteria",
    "Advanced_Criteria",
    "query",
    "generation_cache_id",
]


def build_export_rows(
    selected_skills: List[Dict[str, Any]],
    query: str,
    generation_cache_id: str,
    evidence_mode: str = "pipe",
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for s in selected_skills:
        row = {
            "skill_id": safe_str(s.get("skill_id")),
            "skill_name": safe_str(s.get("skill_name")),
            "source": safe_str(s.get("source")),
            "relevance_score": s.get("relevance_score", None),
            "reasoning": safe_str(s.get("reasoning")),
            "evidence": evidence_to_export(s.get("evidence"), mode=evidence_mode),
            "skill_text": safe_str(s.get("skill_text")),
            "Foundational_Criteria": safe_str(s.get("Foundational_Criteria")),
            "Intermediate_Criteria": safe_str(s.get("Intermediate_Criteria")),
            "Advanced_Criteria": safe_str(s.get("Advanced_Criteria")),
            "query": safe_str(query),
            "generation_cache_id": safe_str(generation_cache_id),
        }
        rows.append(row)
    return rows


def _to_df(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    # enforce column order (missing columns get created)
    for c in EXPORT_COLUMNS:
        if c not in df.columns:
            df[c] = None
    df = df[EXPORT_COLUMNS]
    return df


def export_csv_bytes(rows: List[Dict[str, Any]]) -> bytes:
    df = _to_df(rows)
    return df.to_csv(index=False).encode("utf-8")


def export_xlsx_bytes(rows: List[Dict[str, Any]]) -> bytes:
    df = _to_df(rows)
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="selected_skills")
    return bio.getvalue()
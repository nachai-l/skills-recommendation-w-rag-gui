from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class AppState:
    last_query: str = ""
    generation_cache_id: str = ""
    last_results: List[Dict[str, Any]] = None  # list of skill objects
    selected: Dict[str, Dict[str, Any]] = None  # skill_id -> skill object

    def __post_init__(self) -> None:
        if self.last_results is None:
            self.last_results = []
        if self.selected is None:
            self.selected = {}


def add_selected(state: AppState, skill: Dict[str, Any]) -> None:
    skill_id = str(skill.get("skill_id", "")).strip()
    if not skill_id:
        return
    state.selected[skill_id] = skill  # overwrite = dedupe


def remove_selected(state: AppState, skill_id: str) -> None:
    skill_id = str(skill_id).strip()
    if not skill_id:
        return
    state.selected.pop(skill_id, None)


def selected_list(state: AppState) -> List[Dict[str, Any]]:
    # stable order: by relevance_score desc then skill_name
    def _score(x: Dict[str, Any]) -> float:
        try:
            return float(x.get("relevance_score", 0.0))
        except Exception:
            return 0.0

    items = list(state.selected.values())
    items.sort(key=lambda x: (-_score(x), str(x.get("skill_name", "")).lower(), str(x.get("skill_id", ""))))
    return items
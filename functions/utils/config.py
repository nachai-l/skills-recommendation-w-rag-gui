# functions/utils/config.py
"""
Typed configuration loader for the Skills Recommendation Streamlit app.

This module defines dataclass-based config models and a YAML loader that reads
`configs/parameters.yaml` (by default) into a strongly-typed `AppConfig`.

Structure:
- `ApiConfig`: API base URL, endpoints, timeout
- `DefaultsConfig`: default request parameters for UI controls
- `UiConfig`: Streamlit page settings and display limits
- `AppConfig`: top-level container (api/defaults/ui)

Loading rules:
- `_read_yaml()` validates the YAML file exists and the root is a mapping.
- `load_config()` applies sane defaults for missing keys, strips trailing slash
  from `api.base_url`, and requires `api.base_url` to be present.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


@dataclass(frozen=True)
class ApiConfig:
    base_url: str
    endpoint_recommend: str
    endpoint_health: str
    timeout_seconds: int = 120


@dataclass(frozen=True)
class DefaultsConfig:
    top_k: int = 20
    top_k_vector: int = 20
    top_k_bm25: int = 20
    debug: bool = False
    require_judge_pass: bool = True
    require_all_meta: bool = False


@dataclass(frozen=True)
class UiConfig:
    page_title: str = "Skills Recommendation GUI"
    page_icon: str = "🧠"
    preview_chars: int = 120
    max_display_rows: int = 200


@dataclass(frozen=True)
class AppConfig:
    api: ApiConfig
    defaults: DefaultsConfig
    ui: UiConfig


def _read_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing config file: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Invalid YAML root (expected mapping): {path}")
    return data


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """
    Loads configs/parameters.yaml by default.
    """
    if config_path is None:
        config_path = str(Path(__file__).resolve().parents[2] / "configs" / "parameters.yaml")

    data = _read_yaml(Path(config_path))

    api_d = data.get("api", {}) or {}
    defaults_d = data.get("defaults", {}) or {}
    ui_d = data.get("ui", {}) or {}

    api = ApiConfig(
        base_url=str(api_d.get("base_url", "")).rstrip("/"),
        endpoint_recommend=str(api_d.get("endpoint_recommend", "/v1/recommend-skills")),
        endpoint_health=str(api_d.get("endpoint_health", "/healthz")),
        timeout_seconds=int(api_d.get("timeout_seconds", 120)),
    )

    if not api.base_url:
        raise ValueError("api.base_url is required in parameters.yaml")

    defaults = DefaultsConfig(
        top_k=int(defaults_d.get("top_k", 20)),
        top_k_vector=int(defaults_d.get("top_k_vector", 20)),
        top_k_bm25=int(defaults_d.get("top_k_bm25", 20)),
        debug=bool(defaults_d.get("debug", False)),
        require_judge_pass=bool(defaults_d.get("require_judge_pass", True)),
        require_all_meta=bool(defaults_d.get("require_all_meta", False)),
    )

    ui = UiConfig(
        page_title=str(ui_d.get("page_title", "Skills Recommendation GUI")),
        page_icon=str(ui_d.get("page_icon", "🧠")),
        preview_chars=int(ui_d.get("preview_chars", 120)),
        max_display_rows=int(ui_d.get("max_display_rows", 200)),
    )

    return AppConfig(api=api, defaults=defaults, ui=ui)
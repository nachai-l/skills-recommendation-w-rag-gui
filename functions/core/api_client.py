# functions/core/api_client.py
"""
API client helpers for Skills Recommendation service.

This module provides:
- `RecommendRequest`: typed request payload builder for `/v1/recommend-skills`
- `health_check()`: basic connectivity check to `/healthz`
- `recommend_skills()`: POST wrapper with consistent error handling

Error handling:
- Raises `ApiError` for timeouts, network errors, non-200 responses, and non-JSON bodies.
- `ApiError.detail` contains best-effort server error payload (JSON if possible, else raw text).

Config:
- Uses `ApiConfig` (base_url, endpoints, timeout_seconds). URL joining is normalized by `_url()`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import requests

from functions.utils.config import ApiConfig


class ApiError(RuntimeError):
    def __init__(self, message: str, status_code: Optional[int] = None, detail: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail


@dataclass(frozen=True)
class RecommendRequest:
    query: str
    top_k: int
    debug: bool
    require_judge_pass: bool
    top_k_vector: int
    top_k_bm25: int
    require_all_meta: bool

    def to_json(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "top_k": self.top_k,
            "debug": self.debug,
            "require_judge_pass": self.require_judge_pass,
            "top_k_vector": self.top_k_vector,
            "top_k_bm25": self.top_k_bm25,
            "require_all_meta": self.require_all_meta,
        }


def _url(base: str, path: str) -> str:
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


def health_check(api: ApiConfig) -> Tuple[bool, str]:
    url = _url(api.base_url, api.endpoint_health)
    try:
        r = requests.get(url, timeout=api.timeout_seconds)
        if r.status_code == 200:
            return True, "ok"
        return False, f"HTTP {r.status_code}: {r.text}"
    except requests.RequestException as e:
        return False, str(e)


def recommend_skills(api: ApiConfig, req: RecommendRequest) -> Dict[str, Any]:
    url = _url(api.base_url, api.endpoint_recommend)
    try:
        r = requests.post(url, json=req.to_json(), timeout=api.timeout_seconds)
    except requests.Timeout as e:
        raise ApiError(f"Request timed out after {api.timeout_seconds}s", detail=str(e)) from e
    except requests.RequestException as e:
        raise ApiError("Network error calling API", detail=str(e)) from e

    if r.status_code != 200:
        # best-effort parse FastAPI error shape
        detail: Any
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        raise ApiError(f"API error: HTTP {r.status_code}", status_code=r.status_code, detail=detail)

    try:
        return r.json()
    except Exception as e:
        raise ApiError("API returned non-JSON response", status_code=r.status_code, detail=r.text) from e
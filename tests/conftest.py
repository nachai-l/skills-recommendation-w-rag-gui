# tests/conftest.py
"""
Pytest configuration for the project test suite.

This conftest ensures the project root is on `sys.path` so tests can import
the local package modules (e.g., `import functions...`) without requiring an
editable install.

Note:
- This is a lightweight path tweak intended for local/CI test execution.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to PYTHONPATH so `import functions...` works
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
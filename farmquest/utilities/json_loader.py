"""Helpers for loading JSON resources."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    """Load JSON from a project file."""
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)

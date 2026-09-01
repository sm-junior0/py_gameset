"""Localization with safe English fallback."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from farmquest.config import DATA_ROOT
from farmquest.utilities.json_loader import load_json


@dataclass
class LocalizationManager:
    """Loads text resources and falls back to English."""

    language: str = "en"
    _fallback: dict[str, str] = field(default_factory=dict)
    _active: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._fallback = load_json(DATA_ROOT / "localization_en.json")["strings"]
        self._active = dict(self._fallback)
        custom_path = DATA_ROOT / f"localization_{self.language}.json"
        if self.language != "en" and Path(custom_path).exists():
            self._active.update(load_json(custom_path)["strings"])

    def translate(self, key: str) -> str:
        """Return the localized value or the key fallback."""
        return self._active.get(key, self._fallback.get(key, key))

"""Optional audio loading with graceful failure."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from farmquest.config import AUDIO_PATHS
from farmquest.managers.settings_manager import SettingsManager

LOGGER = logging.getLogger(__name__)

try:
    from kivy.core.audio import SoundLoader
except Exception:  # pragma: no cover - allows tests without Kivy audio
    SoundLoader = None


@dataclass
class AudioManager:
    """Loads and plays optional sounds without crashing on missing assets."""

    settings: SettingsManager
    sounds: dict[str, Any] = field(default_factory=dict)

    def load(self) -> None:
        """Attempt to load configured audio files."""
        if SoundLoader is None:
            LOGGER.warning("Kivy audio is unavailable in this environment.")
            return
        for key, path in AUDIO_PATHS.items():
            sound = self._load_sound(path)
            if sound is not None:
                self.sounds[key] = sound

    def _load_sound(self, path: Path) -> Any | None:
        """Load an individual sound or log a warning."""
        if not path.exists():
            LOGGER.warning("Optional audio file missing: %s", path)
            return None
        try:
            return SoundLoader.load(str(path))
        except Exception as exc:  # pragma: no cover - depends on runtime codecs
            LOGGER.warning("Failed to load audio file %s: %s", path, exc)
            return None

    def play_effect(self, name: str) -> None:
        """Play a short effect if available."""
        if self.settings.muted:
            return
        sound = self.sounds.get(name)
        if sound is not None:
            sound.volume = self.settings.effects_volume
            sound.play()

    def play_theme(self) -> None:
        """Play looping theme music if available."""
        if self.settings.muted:
            return
        sound = self.sounds.get("theme")
        if sound is not None:
            sound.loop = True
            sound.volume = self.settings.music_volume
            sound.play()

    def stop_all(self) -> None:
        """Stop any loaded sound."""
        for sound in self.sounds.values():
            if sound is not None:
                sound.stop()

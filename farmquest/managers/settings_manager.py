"""Session settings and accessibility preferences."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SettingsManager:
    """Stores mutable runtime settings."""

    music_volume: float = 0.6
    effects_volume: float = 0.8
    muted: bool = False

    def toggle_mute(self) -> None:
        """Toggle mute state."""
        self.muted = not self.muted

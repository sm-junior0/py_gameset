"""Simple horizontal camera helper."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CameraSystem:
    """Tracks the camera x offset."""

    world_width: float
    view_width: float
    offset_x: float = 0.0

    def update(self, player_center_x: float) -> float:
        """Center the camera on the player and clamp to the world."""
        target = player_center_x - (self.view_width / 2)
        self.offset_x = max(0.0, min(target, max(0.0, self.world_width - self.view_width)))
        return self.offset_x

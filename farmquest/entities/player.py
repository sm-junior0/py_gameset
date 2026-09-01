"""Player data model."""

from __future__ import annotations

from dataclasses import dataclass

from farmquest.entities.level import RectEntity


@dataclass(slots=True)
class Player(RectEntity):
    """Mutable player physics state."""

    velocity_x: float = 0.0
    velocity_y: float = 0.0
    on_ground: bool = False
    avatar_id: str = "sunrise"

    def respawn(self, x: float, y: float) -> None:
        """Reset player position and velocity at a checkpoint."""
        self.x = x
        self.y = y
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.on_ground = False

"""Basic platform collision helpers."""

from __future__ import annotations

from farmquest.entities.level import RectEntity
from farmquest.entities.player import Player


def resolve_world_collisions(player: Player, solids: list[RectEntity], previous_x: float, previous_y: float) -> None:
    """Resolve player movement against world solids."""
    player.on_ground = False
    for solid in solids:
        if not player.intersects(solid):
            continue

        if previous_y >= solid.top and player.bottom < solid.top:
            player.y = solid.top
            player.velocity_y = 0.0
            player.on_ground = True
        elif previous_y + player.height <= solid.bottom and player.top > solid.bottom:
            player.y = solid.bottom - player.height
            player.velocity_y = 0.0
        elif previous_x + player.width <= solid.left and player.right > solid.left:
            player.x = solid.left - player.width
            player.velocity_x = 0.0
        elif previous_x >= solid.right and player.left < solid.right:
            player.x = solid.right
            player.velocity_x = 0.0

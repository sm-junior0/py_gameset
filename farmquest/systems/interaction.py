"""Interaction lookup for nearby world objects."""

from __future__ import annotations

from farmquest.entities.level import RectEntity
from farmquest.entities.player import Player


def find_interaction(player: Player, zones: list[RectEntity], radius: float = 60.0) -> RectEntity | None:
    """Return the first interaction zone close enough to the player."""
    for zone in zones:
        expanded = RectEntity(
            x=zone.x - radius,
            y=zone.y - radius,
            width=zone.width + (radius * 2),
            height=zone.height + (radius * 2),
        )
        if player.intersects(expanded):
            return zone
    return None

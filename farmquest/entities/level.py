"""Level data structures."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RectEntity:
    """A basic world-aligned rectangle."""

    x: float
    y: float
    width: float
    height: float
    label: str = ""
    kind: str = ""

    @property
    def left(self) -> float:
        return self.x

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y

    @property
    def top(self) -> float:
        return self.y + self.height

    def intersects(self, other: "RectEntity") -> bool:
        return (
            self.left < other.right
            and self.right > other.left
            and self.bottom < other.top
            and self.top > other.bottom
        )

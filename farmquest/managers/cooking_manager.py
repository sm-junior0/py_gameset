"""Simple order-based cooking mini-game logic."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CookingManager:
    """Handles the meal cooking sequence."""

    steps: list[str] = field(default_factory=lambda: ["heat pot", "add flour", "stir"])
    progress_index: int = 0

    @property
    def current_step(self) -> str:
        """Return the next required step."""
        return self.steps[self.progress_index] if self.progress_index < len(self.steps) else "done"

    def submit_step(self, step: str) -> bool:
        """Advance if the selected step matches the next requirement."""
        if self.progress_index < len(self.steps) and step == self.steps[self.progress_index]:
            self.progress_index += 1
            return True
        return False

    def is_complete(self) -> bool:
        """Return whether the recipe is finished."""
        return self.progress_index >= len(self.steps)

    def reset(self) -> None:
        """Reset the mini-game."""
        self.progress_index = 0

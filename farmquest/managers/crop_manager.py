"""Crop progression helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CropManager:
    """Tracks the visible maize growth stage."""

    stage: str = "seed"

    def set_stage(self, stage: str) -> None:
        """Update the crop stage."""
        self.stage = stage

    def reset(self) -> None:
        """Reset crop visuals for a new run."""
        self.stage = "seed"

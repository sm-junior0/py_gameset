"""Enumerations and results used by the game state machine."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ProgressState(str, Enum):
    """Ordered game progress states."""

    INTRODUCTION = "INTRODUCTION"
    EXPLORING = "EXPLORING"
    SEED_FOUND = "SEED_FOUND"
    SOIL_PREPARED = "SOIL_PREPARED"
    SEED_PLANTED = "SEED_PLANTED"
    CROP_WATERED = "CROP_WATERED"
    CROP_PROTECTED = "CROP_PROTECTED"
    CROP_GROWING = "CROP_GROWING"
    CROP_MATURE = "CROP_MATURE"
    CROP_HARVESTED = "CROP_HARVESTED"
    MAIZE_PROCESSED = "MAIZE_PROCESSED"
    MEAL_COOKED = "MEAL_COOKED"
    COMPLETED = "COMPLETED"


@dataclass(slots=True)
class ActionResult:
    """Outcome of a requested state transition."""

    success: bool
    message: str
    state_changed: bool = False

"""Objective and hint text for the current session."""

from __future__ import annotations

from dataclasses import dataclass, field

from farmquest.config import DATA_ROOT
from farmquest.entities.game_state import ProgressState
from farmquest.utilities.json_loader import load_json


@dataclass
class ObjectiveManager:
    """Provides objective text and anti-stuck hints."""

    objectives: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.objectives:
            self.objectives = load_json(DATA_ROOT / "objectives.json")

    def objective_for(self, state: ProgressState) -> str:
        """Return the primary objective text."""
        return self.objectives.get(state.value, "")

    def hint_for(self, state: ProgressState) -> str:
        """Return a contextual hint for a stalled player."""
        hints = {
            ProgressState.INTRODUCTION: "Move right, jump over the first obstacle, and learn the controls.",
            ProgressState.EXPLORING: "The first quiz marker is ahead. Answer it before searching for the seed.",
            ProgressState.SEED_FOUND: "The farm plot is farther right. Look for the brown soil patch.",
            ProgressState.SOIL_PREPARED: "Planting unlocks after you answer the second question.",
            ProgressState.SEED_PLANTED: "The water source is just ahead of the field.",
            ProgressState.CROP_WATERED: "Pull the weed beside the crop and answer the crop-care question.",
            ProgressState.CROP_PROTECTED: "Use the growth marker to advance the crop to the next stage.",
            ProgressState.CROP_GROWING: "The transition is accelerated for gameplay. Stay near the crop.",
            ProgressState.CROP_MATURE: "The maize is ready. Interact at the harvest marker.",
            ProgressState.CROP_HARVESTED: "Carry the harvest to the mill on the right.",
            ProgressState.MAIZE_PROCESSED: "The kitchen is next. Complete the cooking steps in order.",
            ProgressState.MEAL_COOKED: "Serve the maize meal at the final station.",
            ProgressState.COMPLETED: "Restart or return to the title screen for the next player.",
        }
        return hints.get(state, "")

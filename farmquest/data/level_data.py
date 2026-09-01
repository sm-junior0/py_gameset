"""Static level layout data for the prototype."""

from __future__ import annotations

from farmquest.config import GROUND_Y, WORLD_WIDTH
from farmquest.entities.level import RectEntity


def build_level() -> dict[str, list[RectEntity] | float]:
    """Create a simple side-scrolling farm layout."""
    solids = [
        RectEntity(0, 0, WORLD_WIDTH, GROUND_Y, kind="ground"),
        RectEntity(420, 180, 180, 24, label="log bridge", kind="platform"),
        RectEntity(900, 210, 160, 24, label="rock ledge", kind="platform"),
        RectEntity(1600, 160, 220, 20, label="fence hop", kind="platform"),
        RectEntity(2870, 150, 180, 20, label="field ridge", kind="platform"),
    ]
    hazards = [
        RectEntity(760, GROUND_Y, 120, 28, label="mud hazard", kind="hazard"),
        RectEntity(2060, GROUND_Y, 100, 28, label="ditch", kind="hazard"),
    ]
    checkpoints = [
        RectEntity(100, GROUND_Y, 40, 140, label="start checkpoint", kind="checkpoint"),
        RectEntity(1420, GROUND_Y, 40, 140, label="field checkpoint", kind="checkpoint"),
        RectEntity(3320, GROUND_Y, 40, 140, label="mill checkpoint", kind="checkpoint"),
        RectEntity(4620, GROUND_Y, 40, 140, label="kitchen checkpoint", kind="checkpoint"),
    ]
    interactions = [
        RectEntity(520, GROUND_Y, 80, 120, label="Question 1", kind="question_1"),
        RectEntity(1120, 250, 60, 60, label="Hidden Seed", kind="collect_seed"),
        RectEntity(1880, GROUND_Y, 120, 140, label="Prepare Soil", kind="prepare_soil"),
        RectEntity(2160, GROUND_Y, 90, 120, label="Question 2", kind="question_2"),
        RectEntity(2460, GROUND_Y, 100, 140, label="Plant Seed", kind="plant_seed"),
        RectEntity(2860, GROUND_Y, 120, 140, label="Water Crop", kind="water_crop"),
        RectEntity(3160, GROUND_Y, 90, 120, label="Question 3", kind="question_3"),
        RectEntity(3360, GROUND_Y, 100, 120, label="Remove Weed", kind="protect_crop"),
        RectEntity(3620, GROUND_Y, 110, 120, label="Grow Crop", kind="start_growth"),
        RectEntity(3880, GROUND_Y, 110, 120, label="Finish Growth", kind="mature_crop"),
        RectEntity(4140, GROUND_Y, 100, 120, label="Harvest", kind="harvest_crop"),
        RectEntity(4480, GROUND_Y, 120, 140, label="Mill", kind="process_maize"),
        RectEntity(4900, GROUND_Y, 120, 140, label="Kitchen", kind="cook_meal"),
        RectEntity(5300, GROUND_Y, 100, 120, label="Serve Meal", kind="serve_meal"),
    ]
    return {
        "solids": solids,
        "hazards": hazards,
        "checkpoints": checkpoints,
        "interactions": interactions,
        "spawn_x": 110.0,
        "spawn_y": GROUND_Y,
    }

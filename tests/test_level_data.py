from farmquest.config import GROUND_Y
from farmquest.data.level_data import build_level


def test_hazards_are_reachable_above_ground() -> None:
    level = build_level()
    hazards = level["hazards"]
    assert hazards
    assert all(hazard.y >= GROUND_Y for hazard in hazards)

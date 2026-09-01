from farmquest.entities.game_state import ProgressState
from farmquest.managers.game_state_manager import GameStateManager


def answer_correctly(state_manager: GameStateManager, question_id: str) -> None:
    result = state_manager.submit_question(question_id, 0)
    assert result["correct"] is True


def test_valid_state_progression() -> None:
    manager = GameStateManager()
    assert manager.start_game().success is True
    answer_correctly(manager, "question_1")
    assert manager.attempt_action("collect_seed").success is True
    assert manager.attempt_action("prepare_soil").success is True
    answer_correctly(manager, "question_2")
    assert manager.attempt_action("plant_seed").success is True
    assert manager.attempt_action("water_crop").success is True
    assert manager.attempt_action("protect_crop").success is True
    answer_correctly(manager, "question_3")
    assert manager.attempt_action("start_growth").success is True
    assert manager.attempt_action("mature_crop").success is True
    assert manager.attempt_action("harvest_crop").success is True
    assert manager.attempt_action("process_maize").success is True
    for step in ["heat pot", "add flour", "stir"]:
        assert manager.cooking_manager.submit_step(step) is True
    assert manager.attempt_action("cook_meal").success is True
    assert manager.attempt_action("serve_meal").success is True
    assert manager.state == ProgressState.COMPLETED


def test_invalid_action_order_is_blocked() -> None:
    manager = GameStateManager()
    manager.start_game()
    result = manager.attempt_action("plant_seed")
    assert result.success is False
    assert "prepare the soil" in result.message.lower()
    assert manager.state == ProgressState.EXPLORING


def test_reset_returns_clean_session() -> None:
    manager = GameStateManager()
    manager.start_game()
    answer_correctly(manager, "question_1")
    manager.attempt_action("collect_seed")
    manager.reset()
    assert manager.state == ProgressState.INTRODUCTION
    assert manager.seed_collected is False
    assert manager.score_manager.total_score == 30

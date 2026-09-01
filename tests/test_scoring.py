from farmquest.managers.game_state_manager import GameStateManager
from farmquest.managers.score_manager import ScoreManager


def test_score_calculation_and_reward_thresholds() -> None:
    score = ScoreManager()
    score.record_question("question_1", True)
    score.record_question("question_2", True)
    score.record_question("question_3", False)
    score.record_mistake()
    for stage in [
        "seed_found",
        "soil_prepared",
        "seed_planted",
        "crop_watered",
        "crop_protected",
        "crop_growing",
        "crop_mature",
        "crop_harvested",
    ]:
        score.record_stage_completion(stage)
    assert score.knowledge_score == 27
    assert score.accuracy_score == 27
    assert score.completion_score == 24
    assert score.total_score == 78
    assert score.reward_label == "Silver Agriculture Explorer"


def test_quiz_first_attempt_scoring() -> None:
    manager = GameStateManager()
    manager.start_game()
    wrong = manager.submit_question("question_1", 1)
    assert wrong["correct"] is False
    correct = manager.submit_question("question_1", 0)
    assert correct["correct"] is True
    assert manager.score_manager.knowledge_score == 0
    assert manager.score_manager.mistakes == 1


def test_completion_reward_gold() -> None:
    score = ScoreManager()
    for question in ["question_1", "question_2", "question_3"]:
        score.record_question(question, True)
    for stage in [
        "seed_found",
        "soil_prepared",
        "seed_planted",
        "crop_watered",
        "crop_protected",
        "crop_growing",
        "crop_mature",
        "crop_harvested",
        "maize_processed",
        "meal_cooked",
    ]:
        score.record_stage_completion(stage)
    assert score.total_score == 100
    assert score.reward_label == "Gold Agriculture Explorer"

"""Primary game progression state machine."""

from __future__ import annotations

from dataclasses import dataclass, field

from farmquest.entities.game_state import ActionResult, ProgressState
from farmquest.managers.cooking_manager import CookingManager
from farmquest.managers.crop_manager import CropManager
from farmquest.managers.objective_manager import ObjectiveManager
from farmquest.managers.quiz_manager import QuizManager
from farmquest.managers.score_manager import ScoreManager


@dataclass
class GameStateManager:
    """Enforces the farm-to-table action order."""

    state: ProgressState = ProgressState.INTRODUCTION
    avatar_id: str = "sunrise"
    seed_collected: bool = False
    soil_prepared: bool = False
    question_1_done: bool = False
    question_2_done: bool = False
    question_3_done: bool = False
    growth_started: bool = False
    processed: bool = False
    meal_cooked: bool = False
    score_manager: ScoreManager = field(default_factory=ScoreManager)
    quiz_manager: QuizManager = field(default_factory=QuizManager)
    objective_manager: ObjectiveManager = field(default_factory=ObjectiveManager)
    crop_manager: CropManager = field(default_factory=CropManager)
    cooking_manager: CookingManager = field(default_factory=CookingManager)

    def select_avatar(self, avatar_id: str) -> None:
        """Store the chosen avatar appearance."""
        self.avatar_id = avatar_id

    def start_game(self) -> ActionResult:
        """Begin exploration after the tutorial."""
        if self.state != ProgressState.INTRODUCTION:
            return ActionResult(False, "The session has already started.")
        self.state = ProgressState.EXPLORING
        return ActionResult(True, "Explore the farm and find the first question marker.", True)

    def submit_question(self, question_id: str, selected_index: int) -> dict[str, object]:
        """Evaluate a question and update scoring flags."""
        result = self.quiz_manager.submit_answer(question_id, selected_index)
        self.score_manager.record_question(question_id, bool(result["first_attempt_correct"]))
        if not bool(result["correct"]):
            self.score_manager.record_mistake()
        if bool(result["correct"]):
            if question_id == "question_1":
                self.question_1_done = True
            elif question_id == "question_2":
                self.question_2_done = True
            elif question_id == "question_3":
                self.question_3_done = True
        return result

    def attempt_action(self, action: str) -> ActionResult:
        """Try to perform the next world action."""
        handlers = {
            "collect_seed": self._collect_seed,
            "prepare_soil": self._prepare_soil,
            "plant_seed": self._plant_seed,
            "water_crop": self._water_crop,
            "protect_crop": self._protect_crop,
            "start_growth": self._start_growth,
            "mature_crop": self._mature_crop,
            "harvest_crop": self._harvest_crop,
            "process_maize": self._process_maize,
            "cook_meal": self._cook_meal,
            "serve_meal": self._serve_meal,
        }
        handler = handlers[action]
        result = handler()
        if not result.success:
            self.score_manager.record_mistake()
        return result

    def _collect_seed(self) -> ActionResult:
        if self.state != ProgressState.EXPLORING or not self.question_1_done:
            return ActionResult(False, "Answer the first agriculture question before searching for the seed.")
        self.seed_collected = True
        self.state = ProgressState.SEED_FOUND
        self.score_manager.record_stage_completion("seed_found")
        return ActionResult(True, "You found the hidden maize seed.", True)

    def _prepare_soil(self) -> ActionResult:
        if self.state != ProgressState.SEED_FOUND:
            return ActionResult(False, "Find the maize seed before preparing the soil.")
        self.soil_prepared = True
        self.state = ProgressState.SOIL_PREPARED
        self.score_manager.record_stage_completion("soil_prepared")
        return ActionResult(True, "The soil is ready for planting.", True)

    def _plant_seed(self) -> ActionResult:
        if self.state != ProgressState.SOIL_PREPARED or not self.question_2_done:
            return ActionResult(False, "Answer the planting question and prepare the soil before planting.")
        self.state = ProgressState.SEED_PLANTED
        self.crop_manager.set_stage("seed")
        self.score_manager.record_stage_completion("seed_planted")
        return ActionResult(True, "The maize seed has been planted.", True)

    def _water_crop(self) -> ActionResult:
        if self.state != ProgressState.SEED_PLANTED:
            return ActionResult(False, "Plant the maize seed before watering the crop.")
        self.state = ProgressState.CROP_WATERED
        self.score_manager.record_stage_completion("crop_watered")
        return ActionResult(True, "The crop has enough water.", True)

    def _protect_crop(self) -> ActionResult:
        if self.state != ProgressState.CROP_WATERED:
            return ActionResult(False, "Water the crop before removing the weed.")
        self.state = ProgressState.CROP_PROTECTED
        self.score_manager.record_stage_completion("crop_protected")
        return ActionResult(True, "The weed is removed and the crop is protected.", True)

    def _start_growth(self) -> ActionResult:
        if self.state != ProgressState.CROP_PROTECTED or not self.question_3_done:
            return ActionResult(False, "Remove the weed and answer the crop-care question before growth.")
        self.state = ProgressState.CROP_GROWING
        self.growth_started = True
        self.crop_manager.set_stage("growing")
        self.score_manager.record_stage_completion("crop_growing")
        return ActionResult(True, "Time passes quickly here for gameplay. The maize begins to grow.", True)

    def _mature_crop(self) -> ActionResult:
        if self.state != ProgressState.CROP_GROWING:
            return ActionResult(False, "Start the growth transition before maturing the crop.")
        self.state = ProgressState.CROP_MATURE
        self.crop_manager.set_stage("mature")
        self.score_manager.record_stage_completion("crop_mature")
        return ActionResult(True, "The maize is now mature and ready to harvest.", True)

    def _harvest_crop(self) -> ActionResult:
        if self.state != ProgressState.CROP_MATURE:
            return ActionResult(False, "Wait for the maize to mature before harvesting.")
        self.state = ProgressState.CROP_HARVESTED
        self.score_manager.record_stage_completion("crop_harvested")
        return ActionResult(True, "You harvested the mature maize.", True)

    def _process_maize(self) -> ActionResult:
        if self.state != ProgressState.CROP_HARVESTED:
            return ActionResult(False, "Harvest the maize before taking it to the mill.")
        self.state = ProgressState.MAIZE_PROCESSED
        self.processed = True
        self.score_manager.record_stage_completion("maize_processed")
        return ActionResult(True, "The mill turns the maize into flour.", True)

    def _cook_meal(self) -> ActionResult:
        if self.state != ProgressState.MAIZE_PROCESSED:
            return ActionResult(False, "Process the maize at the mill before cooking.")
        if not self.cooking_manager.is_complete():
            return ActionResult(False, "Finish the cooking steps in the correct order first.")
        self.state = ProgressState.MEAL_COOKED
        self.meal_cooked = True
        self.score_manager.record_stage_completion("meal_cooked")
        return ActionResult(True, "The maize meal is cooked and ready to serve.", True)

    def _serve_meal(self) -> ActionResult:
        if self.state != ProgressState.MEAL_COOKED:
            return ActionResult(False, "Cook the maize meal before serving it.")
        self.state = ProgressState.COMPLETED
        self.score_manager.record_stage_completion("meal_served")
        self.score_manager.finalize()
        return ActionResult(True, "The meal is served. Farm-to-table complete!", True)

    def current_objective(self) -> str:
        """Return the current top-level objective."""
        return self.objective_manager.objective_for(self.state)

    def current_hint(self) -> str:
        """Return a hint for the current state."""
        return self.objective_manager.hint_for(self.state)

    def results(self) -> dict[str, object]:
        """Expose final scoring and a short summary."""
        summary = self.score_manager.summary()
        summary["process_summary"] = (
            "Seed found -> soil prepared -> planted -> watered -> protected -> "
            "grew -> harvested -> milled -> cooked -> served."
        )
        return summary

    def reset(self) -> None:
        """Reset the session for a new player."""
        self.state = ProgressState.INTRODUCTION
        self.seed_collected = False
        self.soil_prepared = False
        self.question_1_done = False
        self.question_2_done = False
        self.question_3_done = False
        self.growth_started = False
        self.processed = False
        self.meal_cooked = False
        self.score_manager.reset()
        self.quiz_manager.reset()
        self.crop_manager.reset()
        self.cooking_manager.reset()

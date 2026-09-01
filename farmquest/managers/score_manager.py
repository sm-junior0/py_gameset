"""Score tracking for the FarmQuest session."""

from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic

from farmquest.config import DATA_ROOT
from farmquest.utilities.json_loader import load_json


@dataclass
class ScoreManager:
    """Tracks knowledge, accuracy, completion, and timing."""

    started_at: float = field(default_factory=monotonic)
    completed_at: float | None = None
    first_attempt_correct_questions: set[str] = field(default_factory=set)
    completed_stages: set[str] = field(default_factory=set)
    mistakes: int = 0

    QUESTION_WEIGHTS = {"question_1": 14, "question_2": 13, "question_3": 13}
    COMPLETION_TOTAL = 30
    ACCURACY_TOTAL = 30
    REQUIRED_STAGE_COUNT = 10

    def record_question(self, question_id: str, first_attempt_correct: bool) -> None:
        """Record first-attempt knowledge credit for a quiz question."""
        if first_attempt_correct:
            self.first_attempt_correct_questions.add(question_id)

    def record_stage_completion(self, stage_name: str) -> None:
        """Record a major stage completion once."""
        self.completed_stages.add(stage_name)

    def record_mistake(self) -> None:
        """Record an accuracy penalty."""
        self.mistakes += 1

    def finalize(self) -> None:
        """Stop the timer when the run is complete."""
        if self.completed_at is None:
            self.completed_at = monotonic()

    @property
    def knowledge_score(self) -> int:
        """Score from correct first-attempt quiz answers."""
        return sum(
            weight
            for question_id, weight in self.QUESTION_WEIGHTS.items()
            if question_id in self.first_attempt_correct_questions
        )

    @property
    def accuracy_score(self) -> int:
        """Accuracy starts high and drops for mistakes."""
        return max(0, self.ACCURACY_TOTAL - (self.mistakes * 3))

    @property
    def completion_score(self) -> int:
        """Completion points scale with required milestones reached."""
        progress = min(len(self.completed_stages), self.REQUIRED_STAGE_COUNT)
        return round((progress / self.REQUIRED_STAGE_COUNT) * self.COMPLETION_TOTAL)

    @property
    def total_score(self) -> int:
        """Combined total score out of 100."""
        return min(100, self.knowledge_score + self.accuracy_score + self.completion_score)

    @property
    def completion_time(self) -> float:
        """Elapsed session time in seconds."""
        end_time = self.completed_at if self.completed_at is not None else monotonic()
        return max(0.0, end_time - self.started_at)

    @property
    def reward_label(self) -> str:
        """Reward tier from configured thresholds."""
        reward_data = load_json(DATA_ROOT / "rewards.json")
        if self.total_score >= reward_data["gold_min"]:
            return reward_data["gold_label"]
        if self.total_score >= reward_data["silver_min"]:
            return reward_data["silver_label"]
        return reward_data["participant_label"]

    def summary(self) -> dict[str, object]:
        """Return a serializable results payload."""
        return {
            "knowledge_score": self.knowledge_score,
            "accuracy_score": self.accuracy_score,
            "completion_score": self.completion_score,
            "total_score": self.total_score,
            "completion_time": self.completion_time,
            "reward": self.reward_label,
        }

    def reset(self) -> None:
        """Reset the score state for the next player."""
        self.started_at = monotonic()
        self.completed_at = None
        self.first_attempt_correct_questions.clear()
        self.completed_stages.clear()
        self.mistakes = 0

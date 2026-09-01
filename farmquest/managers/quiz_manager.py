"""Quiz loading and evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field

from farmquest.config import DATA_ROOT
from farmquest.utilities.json_loader import load_json


@dataclass
class QuizAttempt:
    """Stored player interaction with a question."""

    question_id: str
    attempts: int = 0
    answered_correctly: bool = False


@dataclass
class QuizManager:
    """Manages quiz prompts and answer results."""

    questions: list[dict[str, object]] = field(default_factory=list)
    attempts: dict[str, QuizAttempt] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.questions:
            self.questions = load_json(DATA_ROOT / "questions.json")
        # Agricultural wording must be approved by an agricultural subject-matter expert before public release.

    def get_question(self, question_id: str) -> dict[str, object]:
        """Return the question payload by id."""
        for question in self.questions:
            if question["id"] == question_id:
                return question
        raise KeyError(f"Unknown question id: {question_id}")

    def submit_answer(self, question_id: str, selected_index: int) -> dict[str, object]:
        """Evaluate a player's answer and return feedback."""
        question = self.get_question(question_id)
        attempt = self.attempts.setdefault(question_id, QuizAttempt(question_id=question_id))
        attempt.attempts += 1
        is_correct = selected_index == int(question["correct_index"])
        if is_correct:
            attempt.answered_correctly = True
        return {
            "correct": is_correct,
            "first_attempt_correct": is_correct and attempt.attempts == 1,
            "feedback": question["feedback_correct"] if is_correct else question["feedback_incorrect"],
            "correct_index": question["correct_index"],
        }

    def was_answered(self, question_id: str) -> bool:
        """Check whether a question has been completed."""
        attempt = self.attempts.get(question_id)
        return bool(attempt and attempt.answered_correctly)

    def reset(self) -> None:
        """Clear all question attempts for a new player."""
        self.attempts.clear()

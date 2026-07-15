from dataclasses import dataclass, field
from datetime import datetime

from sapere.domain.enums import BloomLevel, Difficulty, EnergyLevel, ExerciseLevel, ReviewScore


@dataclass(frozen=True)
class Subject:
    id: int
    name: str
    description: str = ""
    mode: str = "academic"
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class Topic:
    id: int
    subject_id: int
    name: str
    parent_topic_id: int | None = None
    description: str = ""
    bloom_level: BloomLevel = BloomLevel.UNDERSTAND
    difficulty: Difficulty = Difficulty.MEDIUM
    sort_order: int = 0
    mastery_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class Flashcard:
    id: int
    topic_id: int
    question: str
    answer: str
    hint: str = ""
    ease_factor: float = 2.5
    interval_days: int = 0
    repetitions: int = 0
    next_review_at: datetime = field(default_factory=datetime.now)
    total_reviews: int = 0
    total_correct: int = 0
    last_score: int | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def after_review(self, score: ReviewScore) -> "Flashcard":
        from datetime import timedelta

        if score >= ReviewScore.GOOD:
            new_ef = max(
                1.3,
                self.ease_factor + (0.1 - (5 - score) * (0.08 + (5 - score) * 0.02)),
            )
            if self.repetitions == 0:
                new_interval = 1
            elif self.repetitions == 1:
                new_interval = 6
            else:
                new_interval = round(self.interval_days * self.ease_factor)
            new_repetitions = self.repetitions + 1
        else:
            new_ef = self.ease_factor
            new_interval = 1 if score == ReviewScore.AGAIN else max(1, self.interval_days // 2)
            new_repetitions = 0

        return Flashcard(
            id=self.id,
            topic_id=self.topic_id,
            question=self.question,
            answer=self.answer,
            hint=self.hint,
            ease_factor=new_ef,
            interval_days=new_interval,
            repetitions=new_repetitions,
            next_review_at=datetime.now() + timedelta(days=new_interval),
            total_reviews=self.total_reviews + 1,
            total_correct=self.total_correct + (1 if score >= ReviewScore.GOOD else 0),
            last_score=int(score),
            created_at=self.created_at,
            updated_at=datetime.now(),
        )


@dataclass
class StudySession:
    id: int | None = None
    subject_id: int | None = None
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: datetime | None = None
    duration_seconds: int = 0
    energy_start: EnergyLevel | None = None
    energy_end: EnergyLevel | None = None
    pomodoro_blocks: int = 0
    is_complete: int = 0


@dataclass
class FlashcardReview:
    id: int | None = None
    flashcard_id: int = 0
    session_id: int | None = None
    score: ReviewScore = ReviewScore.AGAIN
    response_time_ms: int | None = None
    reviewed_at: datetime = field(default_factory=datetime.now)

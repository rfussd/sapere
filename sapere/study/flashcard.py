import structlog

from sapere.infrastructure import database
from sapere.domain.enums import ReviewScore
from sapere.domain.models import Flashcard
from sapere.study.scheduler import calculate_sm2

logger = structlog.get_logger()


def get_due_flashcards(subject_id: int | None = None, limit: int = 20) -> list[dict]:
    return database.get_due_flashcards(subject_id=subject_id, limit=limit)


def get_interleaved_flashcards(subject_id: int, limit: int = 20) -> list[dict]:
    current = database.get_due_flashcards(subject_id=subject_id, limit=int(limit * 0.6))

    others = database.get_connection().execute(
        """SELECT f.* FROM flashcards f
           JOIN topics t ON f.topic_id = t.id
           WHERE t.subject_id != ? AND f.next_review_at <= datetime('now')
           ORDER BY f.next_review_at ASC LIMIT ?""",
        (subject_id, int(limit * 0.4) + 5),
    ).fetchall()
    database.get_connection().close()

    other_fcs = [dict(r) for r in others]

    result = []
    other_idx = 0
    for fc in current:
        result.append(fc)
        if other_idx < len(other_fcs):
            result.append(other_fcs[other_idx])
            other_idx += 1

    return result[:limit]


def review_flashcard(
    flashcard_id: int,
    score: ReviewScore,
    session_id: int | None = None,
    response_time_ms: int | None = None,
) -> dict:
    fc_data = database.get_connection().execute(
        "SELECT * FROM flashcards WHERE id = ?", (flashcard_id,)
    ).fetchone()

    if not fc_data:
        raise ValueError(f"Flashcard {flashcard_id} no encontrada")

    fc = dict(fc_data)
    result = calculate_sm2(
        current_ease_factor=fc["ease_factor"],
        current_interval=fc["interval_days"],
        current_repetitions=fc["repetitions"],
        score=score,
    )

    database.update_flashcard_after_review(
        flashcard_id=flashcard_id,
        ease_factor=result["ease_factor"],
        interval_days=result["interval_days"],
        repetitions=result["repetitions"],
        next_review_at=result["next_review_at"],
        total_reviews=fc["total_reviews"] + 1,
        total_correct=fc["total_correct"] + (1 if score >= ReviewScore.GOOD else 0),
        last_score=int(score),
    )

    database.insert_review(
        flashcard_id=flashcard_id,
        session_id=session_id,
        score=int(score),
        response_time_ms=response_time_ms,
    )

    logger.info(
        "flashcard_reviewed",
        flashcard_id=flashcard_id,
        score=int(score),
        new_interval=result["interval_days"],
    )

    return result

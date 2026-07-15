import json
import os
import structlog

from sapere.infrastructure import database
from sapere.domain.enums import ReviewScore

logger = structlog.get_logger()

SAVE_PATH = "data/session_save.json"


def save_session_state(
    subject_id: int,
    session_id: int,
    flashcard_index: int,
    flashcard_ids: list[int],
    reviewed_count: int,
) -> None:
    data = {
        "subject_id": subject_id,
        "session_id": session_id,
        "flashcard_index": flashcard_index,
        "flashcard_ids": flashcard_ids,
        "reviewed_count": reviewed_count,
    }
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(base, SAVE_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f)
    logger.info("session_saved", subject_id=subject_id)


def load_session_state() -> dict | None:
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(base, SAVE_PATH)
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
        if data.get("session_id") and data.get("flashcard_ids"):
            return data
    return None


def clear_session_save() -> None:
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(base, SAVE_PATH)
    if os.path.exists(path):
        os.remove(path)


def resume_flashcards(save_data: dict) -> list[dict]:
    ids = save_data.get("flashcard_ids", [])
    if not ids:
        return []
    placeholders = ",".join("?" for _ in ids)
    conn = database.get_connection()
    rows = conn.execute(
        f"SELECT * FROM flashcards WHERE id IN ({placeholders})",
        ids,
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

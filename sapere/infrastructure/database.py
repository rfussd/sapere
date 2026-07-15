import sqlite3
import os
from datetime import datetime, timedelta
from typing import Any

from sapere.config import config

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS migrations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    applied_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS subjects (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    description TEXT    NOT NULL DEFAULT '',
    mode        TEXT    NOT NULL DEFAULT 'academic',  -- academic, language, tech
    is_active   INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS topics (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id      INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    parent_topic_id INTEGER REFERENCES topics(id) ON DELETE SET NULL,
    name            TEXT    NOT NULL,
    description     TEXT    NOT NULL DEFAULT '',
    bloom_level     INTEGER NOT NULL DEFAULT 2,
    difficulty      INTEGER NOT NULL DEFAULT 3,
    sort_order      INTEGER NOT NULL DEFAULT 0,
    mastery_score   REAL    NOT NULL DEFAULT 0.0,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_topics_subject ON topics(subject_id);
CREATE INDEX IF NOT EXISTS idx_topics_parent ON topics(parent_topic_id);

CREATE TABLE IF NOT EXISTS flashcards (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id        INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    question        TEXT    NOT NULL,
    answer          TEXT    NOT NULL,
    hint            TEXT    NOT NULL DEFAULT '',
    ease_factor     REAL    NOT NULL DEFAULT 2.5,
    interval_days   INTEGER NOT NULL DEFAULT 0,
    repetitions     INTEGER NOT NULL DEFAULT 0,
    next_review_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    total_reviews   INTEGER NOT NULL DEFAULT 0,
    total_correct   INTEGER NOT NULL DEFAULT 0,
    last_score      INTEGER,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_flashcards_topic ON flashcards(topic_id);
CREATE INDEX IF NOT EXISTS idx_flashcards_review ON flashcards(next_review_at);

CREATE TABLE IF NOT EXISTS study_sessions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id      INTEGER REFERENCES subjects(id),
    started_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    ended_at        TEXT,
    duration_seconds INTEGER NOT NULL DEFAULT 0,
    energy_start    INTEGER,
    energy_end      INTEGER,
    pomodoro_blocks INTEGER NOT NULL DEFAULT 0,
    is_complete     INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_sessions_subject ON study_sessions(subject_id);
CREATE INDEX IF NOT EXISTS idx_sessions_date ON study_sessions(started_at);

CREATE TABLE IF NOT EXISTS flashcard_reviews (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    flashcard_id    INTEGER NOT NULL REFERENCES flashcards(id) ON DELETE CASCADE,
    session_id      INTEGER REFERENCES study_sessions(id),
    score           INTEGER NOT NULL CHECK (score BETWEEN 1 AND 4),
    response_time_ms INTEGER,
    reviewed_at     TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_reviews_flashcard ON flashcard_reviews(flashcard_id);
CREATE INDEX IF NOT EXISTS idx_reviews_session ON flashcard_reviews(session_id);

CREATE TABLE IF NOT EXISTS daily_streaks (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT    NOT NULL UNIQUE,
    minutes_studied INTEGER NOT NULL DEFAULT 0,
    sessions_count  INTEGER NOT NULL DEFAULT 0,
    topics_reviewed INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_streaks_date ON daily_streaks(date);

CREATE TABLE IF NOT EXISTS event_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type      TEXT    NOT NULL,
    entity_type     TEXT,
    entity_id       INTEGER,
    payload         TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_event_type ON event_log(event_type);

CREATE TABLE IF NOT EXISTS llm_cache (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    provider        TEXT    NOT NULL,
    prompt_hash     TEXT    NOT NULL UNIQUE,
    request_text    TEXT    NOT NULL,
    response_text   TEXT    NOT NULL,
    tokens_used     INTEGER,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    hit_count       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS exercises (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id          INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    level             INTEGER NOT NULL DEFAULT 1,
    question          TEXT    NOT NULL,
    answer            TEXT,
    explanation       TEXT,
    scaffolding_level INTEGER NOT NULL DEFAULT 1,
    created_at        TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_exercises_topic ON exercises(topic_id);

CREATE TABLE IF NOT EXISTS feynman_attempts (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id         INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    session_id       INTEGER REFERENCES study_sessions(id),
    user_explanation TEXT    NOT NULL,
    ai_evaluation    TEXT,
    passed           INTEGER NOT NULL DEFAULT 0,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_feynman_topic ON feynman_attempts(topic_id);
"""


def get_db_path() -> str:
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, config.db_path)


def get_connection() -> sqlite3.Connection:
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def ensure_schema() -> None:
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
        existing = conn.execute("PRAGMA table_info(subjects)").fetchall()
        columns = [row[1] for row in existing]
        if "mode" not in columns:
            conn.execute("ALTER TABLE subjects ADD COLUMN mode TEXT NOT NULL DEFAULT 'academic'")
            conn.commit()
    finally:
        conn.close()


def log_event(event_type: str, entity_type: str = "", entity_id: int = 0, payload: str = "") -> None:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO event_log (event_type, entity_type, entity_id, payload) VALUES (?, ?, ?, ?)",
            (event_type, entity_type, entity_id, payload),
        )
        conn.commit()
    finally:
        conn.close()


def insert_subject(name: str, description: str = "", mode: str = "academic") -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO subjects (name, description, mode) VALUES (?, ?, ?)",
            (name, description, mode),
        )
        conn.commit()
        return cursor.lastrowid or 0
    finally:
        conn.close()


def get_all_subjects() -> list[dict[str, Any]]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM subjects WHERE is_active = 1 ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_subject(subject_id: int) -> dict[str, Any] | None:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def insert_topic(
    subject_id: int,
    name: str,
    parent_topic_id: int | None = None,
    description: str = "",
    bloom_level: int = 2,
    difficulty: int = 3,
    sort_order: int = 0,
) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO topics (subject_id, parent_topic_id, name, description, bloom_level, difficulty, sort_order)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (subject_id, parent_topic_id, name, description, bloom_level, difficulty, sort_order),
        )
        conn.commit()
        return cursor.lastrowid or 0
    finally:
        conn.close()


def get_topics_for_subject(subject_id: int) -> list[dict[str, Any]]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM topics WHERE subject_id = ? ORDER BY sort_order",
            (subject_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def insert_flashcard(
    topic_id: int,
    question: str,
    answer: str,
    hint: str = "",
) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO flashcards (topic_id, question, answer, hint) VALUES (?, ?, ?, ?)",
            (topic_id, question, answer, hint),
        )
        conn.commit()
        return cursor.lastrowid or 0
    finally:
        conn.close()


def get_due_flashcards(subject_id: int | None = None, limit: int = 20) -> list[dict[str, Any]]:
    conn = get_connection()
    try:
        if subject_id:
            rows = conn.execute(
                """SELECT f.* FROM flashcards f
                   JOIN topics t ON f.topic_id = t.id
                   WHERE t.subject_id = ? AND f.next_review_at <= datetime('now')
                   ORDER BY f.next_review_at ASC LIMIT ?""",
                (subject_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT f.* FROM flashcards f
                   WHERE f.next_review_at <= datetime('now')
                   ORDER BY f.next_review_at ASC LIMIT ?""",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_flashcard_after_review(
    flashcard_id: int,
    ease_factor: float,
    interval_days: int,
    repetitions: int,
    next_review_at: str,
    total_reviews: int,
    total_correct: int,
    last_score: int,
) -> None:
    conn = get_connection()
    try:
        conn.execute(
            """UPDATE flashcards SET
               ease_factor = ?, interval_days = ?, repetitions = ?,
               next_review_at = ?, total_reviews = ?, total_correct = ?,
               last_score = ?, updated_at = datetime('now')
               WHERE id = ?""",
            (ease_factor, interval_days, repetitions, next_review_at, total_reviews, total_correct, last_score, flashcard_id),
        )
        conn.commit()
    finally:
        conn.close()


def insert_review(
    flashcard_id: int,
    session_id: int | None,
    score: int,
    response_time_ms: int | None = None,
) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO flashcard_reviews (flashcard_id, session_id, score, response_time_ms) VALUES (?, ?, ?, ?)",
            (flashcard_id, session_id, score, response_time_ms),
        )
        conn.commit()
    finally:
        conn.close()


def start_study_session(subject_id: int | None = None, energy_start: int = 3) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO study_sessions (subject_id, energy_start) VALUES (?, ?)",
            (subject_id, energy_start),
        )
        conn.commit()
        return cursor.lastrowid or 0
    finally:
        conn.close()


def end_study_session(session_id: int, energy_end: int) -> None:
    conn = get_connection()
    try:
        conn.execute(
            """UPDATE study_sessions SET
               ended_at = datetime('now'), is_complete = 1, energy_end = ?,
               duration_seconds = CAST((julianday('now') - julianday(started_at)) * 86400 AS INTEGER)
               WHERE id = ?""",
            (energy_end, session_id),
        )
        conn.commit()
    finally:
        conn.close()


def record_daily_streak(minutes: int, sessions: int, topics: int) -> None:
    conn = get_connection()
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        existing = conn.execute("SELECT id FROM daily_streaks WHERE date = ?", (today,)).fetchone()
        if existing:
            conn.execute(
                """UPDATE daily_streaks SET
                   minutes_studied = minutes_studied + ?,
                   sessions_count = sessions_count + ?,
                   topics_reviewed = topics_reviewed + ?
                   WHERE date = ?""",
                (minutes, sessions, topics, today),
            )
        else:
            conn.execute(
                "INSERT INTO daily_streaks (date, minutes_studied, sessions_count, topics_reviewed) VALUES (?, ?, ?, ?)",
                (today, minutes, sessions, topics),
            )
        conn.commit()
    finally:
        conn.close()


def get_streak_count() -> int:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT date FROM daily_streaks ORDER BY date DESC"
        ).fetchall()
        if not rows:
            return 0
        streak = 0
        current = datetime.now()
        for r in rows:
            row_date = datetime.strptime(r["date"], "%Y-%m-%d")
            expected = current - timedelta(days=streak)
            if row_date.strftime("%Y-%m-%d") == expected.strftime("%Y-%m-%d"):
                streak += 1
            else:
                break
        return streak
    finally:
        conn.close()


def get_subject_progress(subject_id: int) -> dict[str, Any]:
    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT
                 COUNT(f.id) AS total_flashcards,
                 SUM(CASE WHEN f.next_review_at <= datetime('now') THEN 1 ELSE 0 END) AS due_flashcards,
                 AVG(t.mastery_score) AS avg_mastery
               FROM flashcards f
               JOIN topics t ON f.topic_id = t.id
               WHERE t.subject_id = ?""",
            (subject_id,),
        ).fetchone()
        return dict(row) if row else {"total_flashcards": 0, "due_flashcards": 0, "avg_mastery": 0.0}
    finally:
        conn.close()



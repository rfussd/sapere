import pytest

from sapere.infrastructure.database import (
    ensure_schema,
    insert_subject,
    insert_topic,
    insert_flashcard,
    get_all_subjects,
    get_topics_for_subject,
    get_due_flashcards,
    start_study_session,
    end_study_session,
)


class TestDatabase:
    @pytest.fixture(autouse=True)
    def setup_db(self):
        ensure_schema()

    def test_insert_and_get_subjects(self):
        subject_id = insert_subject("Test DB", "Test description")
        assert subject_id > 0
        subjects = get_all_subjects()
        assert len(subjects) >= 1

    def test_insert_and_get_topics(self):
        subject_id = insert_subject("Test Topics", "")
        topic_id = insert_topic(subject_id, "Test Topic", description="A test")
        assert topic_id > 0
        topics = get_topics_for_subject(subject_id)
        assert len(topics) >= 1

    def test_insert_flashcard(self):
        subject_id = insert_subject("Test FC", "")
        topic_id = insert_topic(subject_id, "Test Topic")
        fc_id = insert_flashcard(topic_id, "Question?", "Answer!")
        assert fc_id > 0

    def test_get_due_flashcards(self):
        subject_id = insert_subject("Test Due", "")
        topic_id = insert_topic(subject_id, "Test Topic")
        insert_flashcard(topic_id, "Q1", "A1")
        due = get_due_flashcards(subject_id=subject_id, limit=10)
        assert len(due) >= 1

    def test_study_session_lifecycle(self):
        session_id = start_study_session(subject_id=None, energy_start=3)
        assert session_id > 0
        end_study_session(session_id, energy_end=2)

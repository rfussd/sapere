import pytest

from sapere.domain.models import Flashcard
from sapere.domain.enums import ReviewScore
from datetime import datetime, timedelta


class TestFlashcardModel:
    def test_after_review_good(self):
        fc = Flashcard(
            id=1,
            topic_id=1,
            question="Test?",
            answer="Yes",
            ease_factor=2.5,
            interval_days=0,
            repetitions=0,
            next_review_at=datetime.now(),
        )
        new_fc = fc.after_review(ReviewScore.GOOD)
        assert new_fc.repetitions == 1
        assert new_fc.total_reviews == 1
        assert new_fc.total_correct == 1
        assert new_fc.interval_days == 1
        assert new_fc.id == fc.id

    def test_after_review_again(self):
        fc = Flashcard(
            id=1,
            topic_id=1,
            question="Test?",
            answer="Yes",
            ease_factor=2.5,
            interval_days=10,
            repetitions=3,
            next_review_at=datetime.now(),
            total_reviews=3,
            total_correct=3,
        )
        new_fc = fc.after_review(ReviewScore.AGAIN)
        assert new_fc.repetitions == 0
        assert new_fc.total_reviews == 4
        assert new_fc.total_correct == 3
        assert new_fc.interval_days == 1

    def test_after_review_hard(self):
        fc = Flashcard(
            id=1,
            topic_id=1,
            question="Test?",
            answer="Yes",
            ease_factor=2.5,
            interval_days=4,
            repetitions=2,
            next_review_at=datetime.now(),
        )
        new_fc = fc.after_review(ReviewScore.HARD)
        assert new_fc.repetitions == 0
        assert new_fc.interval_days == 2
        assert new_fc.total_reviews == 1

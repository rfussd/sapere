import pytest
from datetime import datetime, timedelta

from sapere.domain.enums import ReviewScore
from sapere.study.scheduler import calculate_sm2


class TestSM2Scheduler:
    def test_new_card_good_score(self):
        result = calculate_sm2(
            current_ease_factor=2.5, current_interval=0, current_repetitions=0, score=ReviewScore.GOOD
        )
        assert result["repetitions"] == 1
        assert result["interval_days"] == 1

    def test_new_card_again_score(self):
        result = calculate_sm2(
            current_ease_factor=2.5, current_interval=0, current_repetitions=0, score=ReviewScore.AGAIN
        )
        assert result["repetitions"] == 0
        assert result["interval_days"] == 1

    def test_ease_factor_never_below_minimum(self):
        result = calculate_sm2(
            current_ease_factor=1.5, current_interval=1, current_repetitions=1, score=ReviewScore.AGAIN
        )
        assert result["ease_factor"] >= 1.3

    def test_interval_grows_with_good_scores(self):
        result = calculate_sm2(
            current_ease_factor=2.5, current_interval=6, current_repetitions=2, score=ReviewScore.GOOD
        )
        assert result["interval_days"] > 6
        assert result["repetitions"] == 3

    def test_next_review_at_is_future(self):
        result = calculate_sm2(
            current_ease_factor=2.5, current_interval=1, current_repetitions=1, score=ReviewScore.GOOD
        )
        next_review = datetime.strptime(result["next_review_at"], "%Y-%m-%d %H:%M:%S")
        assert next_review > datetime.now()

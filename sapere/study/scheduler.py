from datetime import datetime, timedelta

from sapere.domain.enums import ReviewScore


def calculate_sm2(
    current_ease_factor: float,
    current_interval: int,
    current_repetitions: int,
    score: ReviewScore,
) -> dict:
    if score >= ReviewScore.GOOD:
        new_ef = max(
            1.3,
            current_ease_factor + (0.1 - (5 - score) * (0.08 + (5 - score) * 0.02)),
        )
        if current_repetitions == 0:
            new_interval = 1
        elif current_repetitions == 1:
            new_interval = 6
        else:
            new_interval = round(current_interval * current_ease_factor)
        new_repetitions = current_repetitions + 1
    else:
        new_ef = current_ease_factor
        new_interval = 1 if score == ReviewScore.AGAIN else max(1, current_interval // 2)
        new_repetitions = 0

    return {
        "ease_factor": new_ef,
        "interval_days": new_interval,
        "repetitions": new_repetitions,
        "next_review_at": (datetime.now() + timedelta(days=new_interval)).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    }

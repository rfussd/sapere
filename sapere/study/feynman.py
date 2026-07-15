import json
import structlog

from sapere.infrastructure import database
from sapere.llm.base import LLMProvider
from sapere.llm.prompts import FEYNMAN_EVALUATION_PROMPT
from sapere.utils.json_parser import robust_json_parse

logger = structlog.get_logger()


def evaluate_explanation(
    llm: LLMProvider,
    topic_id: int,
    topic_name: str,
    user_explanation: str,
    session_id: int | None = None,
) -> dict:
    logger.info("feynman_evaluate_start", topic_id=topic_id, topic_name=topic_name)

    prompt = FEYNMAN_EVALUATION_PROMPT.format(
        topic=topic_name, user_explanation=user_explanation
    )
    response_text = llm.call_with_json(prompt)

    evaluation = robust_json_parse(response_text)

    passed = evaluation.get("passed", False)
    ai_evaluation = json.dumps(evaluation, ensure_ascii=False)

    conn = database.get_connection()
    try:
        conn.execute(
            """INSERT INTO feynman_attempts (topic_id, session_id, user_explanation, ai_evaluation, passed)
               VALUES (?, ?, ?, ?, ?)""",
            (topic_id, session_id, user_explanation, ai_evaluation, 1 if passed else 0),
        )
        conn.commit()
    finally:
        conn.close()

    logger.info("feynman_evaluate_complete", topic_id=topic_id, passed=passed)

    return {
        "understood": evaluation.get("understood", []),
        "missing": evaluation.get("missing", []),
        "confused": evaluation.get("confused", []),
        "clarity_score": evaluation.get("clarity_score", 0),
        "passed": passed,
    }

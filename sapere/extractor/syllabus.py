import structlog

from sapere.infrastructure import database
from sapere.llm.base import LLMProvider
from sapere.llm.prompts import (
    LANGUAGE_SYLLABUS_PROMPT,
    SYLLABUS_ANALYSIS_PROMPT,
    TECH_SYLLABUS_PROMPT,
)
from sapere.utils.json_parser import robust_json_parse

logger = structlog.get_logger()

MODE_PROMPTS = {
    "academic": SYLLABUS_ANALYSIS_PROMPT,
    "language": LANGUAGE_SYLLABUS_PROMPT,
    "tech": TECH_SYLLABUS_PROMPT,
}


def process_syllabus(
    llm: LLMProvider, subject_name: str, raw_text: str, mode: str = "academic"
) -> dict:
    logger.info("process_syllabus_start", subject=subject_name, mode=mode, text_length=len(raw_text))

    subject_id = database.insert_subject(subject_name, "", mode)
    database.log_event("syllabus_uploaded", "subject", subject_id, f"mode={mode}")

    prompt_template = MODE_PROMPTS.get(mode, SYLLABUS_ANALYSIS_PROMPT)
    prompt = prompt_template.format(text=raw_text[:25000])
    response_text = llm.call_with_json(prompt)

    data = robust_json_parse(response_text)

    topics_created = 0
    flashcards_created = 0

    for i, topic_data in enumerate(data.get("topics", [])):
        topic_id = database.insert_topic(
            subject_id=subject_id,
            name=topic_data["name"],
            description=topic_data.get("description", ""),
            bloom_level=topic_data.get("bloom_level", 2),
            difficulty=topic_data.get("difficulty", 3),
            sort_order=i,
        )
        topics_created += 1

        for fc_data in topic_data.get("flashcards", []):
            database.insert_flashcard(
                topic_id=topic_id,
                question=fc_data["question"],
                answer=fc_data["answer"],
                hint=fc_data.get("hint", ""),
            )
            flashcards_created += 1

    logger.info(
        "process_syllabus_complete",
        subject_id=subject_id,
        topics=topics_created,
        flashcards=flashcards_created,
    )

    return {
        "subject_id": subject_id,
        "topics_created": topics_created,
        "flashcards_created": flashcards_created,
    }

import json
import structlog

from sapere.llm.base import LLMProvider
from sapere.llm.prompts import EXERCISE_GENERATION_PROMPT
from sapere.domain.enums import ExerciseLevel

logger = structlog.get_logger()


def generate_exercises(
    llm: LLMProvider,
    topic_name: str,
    level: ExerciseLevel = ExerciseLevel.BASIC,
    scaffolding: int = 3,
    count: int = 3,
    context: str = "",
) -> list[dict]:
    prompt = EXERCISE_GENERATION_PROMPT.format(
        topic=topic_name,
        level=int(level),
        scaffolding=scaffolding,
        count=count,
        context=context or "Sin contexto adicional",
    )

    response_text = llm.call_with_json(prompt)
    data = _parse_json(response_text)

    exercises = data.get("exercises", [])
    logger.info("exercises_generated", topic=topic_name, count=len(exercises))
    return exercises


def generate_curiosity_gap(llm: LLMProvider, topic_name: str, description: str = "") -> str:
    prompt = f"""Crea un acertijo, paradoja o pregunta intrigante sobre el tema "{topic_name}" 
que SOLO se pueda responder entendiendo el concepto.

La pregunta debe generar CURIOSIDAD y un vacio de informacion que motive a aprender.
NO des la respuesta. Solo la pregunta.

Contexto adicional: {description}

Ejemplo para "Derivadas": "Si tu velocidad en un auto es 0 km/h en este instante exacto... 
¿como es posible que te estes moviendo?"

Responde SOLO con la pregunta/acertijo, sin introducciones ni explicaciones."""

    response = llm.call(prompt)
    return response.strip()


def generate_confidence_question(question: str, answer: str) -> str:
    return f"""Pregunta: {question}

Respuesta correcta: {answer}

Ademas de verificar si la respuesta es correcta, califica tu CONFIANZA:
1 = Adivine completamente, no tenia idea
2 = Inseguro, dude mucho
3 = Algo seguro, creo que es correcto
4 = Seguro, confio en mi respuesta
5 = Totalmente seguro, lo domino"""


def _parse_json(text: str) -> dict:
    from sapere.utils.json_parser import robust_json_parse

    return robust_json_parse(text)

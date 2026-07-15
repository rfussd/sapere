import json
import structlog

from google import genai
from google.genai import types

from sapere.config import config
from sapere.llm.base import AbstractLLM, RateLimitError

logger = structlog.get_logger()


class GeminiFlash(AbstractLLM):
    def __init__(self, api_key: str = "", model: str = ""):
        self.api_key = api_key or config.gemini_api_key
        self.model = model or config.gemini_model
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY no configurada. Crea un archivo .env con tu API key.")
        self.client = genai.Client(api_key=self.api_key)

    def call(self, prompt: str, system_prompt: str = "") -> str:
        try:
            contents = []
            if system_prompt:
                contents.append(system_prompt)
            contents.append(prompt)

            response = self.client.models.generate_content(
                model=self.model,
                contents="\n\n".join(contents),
                config=types.GenerateContentConfig(
                    max_output_tokens=config.max_tokens,
                    temperature=0.7,
                ),
            )
            if not response.text:
                raise ValueError("Gemini devolvio una respuesta vacia")
            logger.info("gemini_call_success", model=self.model, tokens=response.usage_metadata)
            return response.text
        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "rate" in error_str or "quota" in error_str or "resource" in error_str:
                raise RateLimitError(f"Gemini rate limit: {e}") from e
            logger.error("gemini_call_error", error=str(e))
            raise

    def call_with_json(self, prompt: str, system_prompt: str = "") -> str:
        return self.call(
            prompt + "\n\nResponde UNICAMENTE con JSON valido, sin markdown, sin explicaciones adicionales.",
            system_prompt,
        )

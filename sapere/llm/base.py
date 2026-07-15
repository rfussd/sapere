from abc import ABC, abstractmethod
import time
import structlog

logger = structlog.get_logger()


class LLMError(Exception):
    pass


class RateLimitError(LLMError):
    pass


class AbstractLLM(ABC):
    @abstractmethod
    def call(self, prompt: str, system_prompt: str = "") -> str:
        ...

    @abstractmethod
    def call_with_json(self, prompt: str, system_prompt: str = "") -> str:
        ...


class LLMProvider:
    def __init__(self, primary: AbstractLLM, fallback: AbstractLLM | None = None):
        self.primary = primary
        self.fallback = fallback

    def call(self, prompt: str, system_prompt: str = "", max_retries: int = 5) -> str:
        for attempt in range(max_retries):
            try:
                logger.info("llm_call_attempt", provider=self.primary.__class__.__name__, attempt=attempt + 1)
                return self.primary.call(prompt, system_prompt)
            except RateLimitError:
                wait = 10 * (2 ** attempt)
                logger.warning("llm_rate_limited", attempt=attempt + 1, wait_seconds=wait)
                time.sleep(wait)
            except Exception as e:
                logger.error("llm_call_failed", provider=self.primary.__class__.__name__, error=str(e))
                if self.fallback:
                    logger.info("llm_fallback", fallback=self.fallback.__class__.__name__)
                    try:
                        return self.fallback.call(prompt, system_prompt)
                    except Exception as fb_e:
                        logger.error("llm_fallback_failed", error=str(fb_e))
                if attempt == max_retries - 1:
                    raise LLMError(f"Todas las rutas de LLM fallaron: {e}") from e
                time.sleep(wait)

        raise LLMError("Maximos reintentos excedidos")

    def call_with_json(self, prompt: str, system_prompt: str = "", max_retries: int = 5) -> str:
        for attempt in range(max_retries):
            try:
                logger.info("llm_json_call", provider=self.primary.__class__.__name__, attempt=attempt + 1)
                return self.primary.call_with_json(prompt, system_prompt)
            except RateLimitError:
                wait = 10 * (2 ** attempt)
                logger.warning("llm_rate_limited", attempt=attempt + 1, wait_seconds=wait)
                time.sleep(wait)
            except Exception as e:
                logger.error("llm_json_failed", provider=self.primary.__class__.__name__, error=str(e))
                if self.fallback:
                    logger.info("llm_fallback", fallback=self.fallback.__class__.__name__)
                    try:
                        return self.fallback.call_with_json(prompt, system_prompt)
                    except Exception as fb_e:
                        logger.error("llm_fallback_failed", error=str(fb_e))
                if attempt == max_retries - 1:
                    raise LLMError(f"Todas las rutas de LLM fallaron: {e}") from e
                time.sleep(wait)

        raise LLMError("Maximos reintentos excedidos")

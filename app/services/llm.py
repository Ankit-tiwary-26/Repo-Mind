import time
import logging
from groq import Groq
from app.config import settings

logger = logging.getLogger(__name__)
_client = Groq(api_key=settings.groq_api_key)


def chat(system_prompt: str, user_prompt: str, temperature: float = 0.2, max_retries: int = 3) -> str:
    """Blocking LLM call with retry logic for rate limits and transient errors."""
    for attempt in range(max_retries):
        try:
            resp = _client.chat.completions.create(
                model=settings.groq_model,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return resp.choices[0].message.content
        except Exception as e:
            logger.warning(f"LLM call attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                time.sleep(wait)
            else:
                raise RuntimeError(f"LLM call failed after {max_retries} attempts: {e}") from e


def chat_stream(system_prompt: str, user_prompt: str, temperature: float = 0.2):
    """Streaming LLM call. Yields content chunks as strings."""
    try:
        stream = _client.chat.completions.create(
            model=settings.groq_model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content
    except Exception as e:
        logger.error(f"LLM streaming failed: {e}")
        yield f"\n\n[Error: {e}]"

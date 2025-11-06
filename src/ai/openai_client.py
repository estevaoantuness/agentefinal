"""OpenAI Client - MAIN LLM for text processing.

This is the PRIMARY client for text generation.
Groq is ONLY for audio processing, NOT for text.
"""

import os
import json
import time
from typing import List, Dict, Optional
from openai import OpenAI, RateLimitError, APIConnectionError, APIError

from src.utils.logger import logger


class OpenAIClient:
    """OpenAI Client for GPT-4o-mini (PRIMARY text processor)."""

    def __init__(self):
        """Initialize OpenAI client."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '500'))
        self.temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))

        logger.info(f"OpenAI Client initialized: model={self.model}")

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        functions: Optional[List[Dict]] = None,
        function_call: Optional[str] = None,
        max_retries: int = 3
    ) -> Dict:
        """
        Call OpenAI Chat Completion with retry logic.

        Args:
            messages: Message history list
            functions: List of function definitions for function calling
            function_call: "auto" or specific function name
            max_retries: Maximum retry attempts

        Returns:
            Response message object
        """
        for attempt in range(max_retries):
            try:
                kwargs = {
                    'model': self.model,
                    'messages': messages,
                    'max_tokens': self.max_tokens,
                    'temperature': self.temperature,
                }

                if functions:
                    # OpenAI uses tools parameter
                    kwargs['tools'] = [{'type': 'function', 'function': f} for f in functions]
                    if function_call:
                        kwargs['tool_choice'] = "auto"

                logger.debug(f"OpenAI request: {len(messages)} messages, model={self.model}")

                response = self.client.chat.completions.create(**kwargs)

                result = response.choices[0].message
                logger.info(f"OpenAI response received (tokens: {response.usage.total_tokens})")
                return result

            except RateLimitError as e:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"OpenAI rate limit hit. Waiting {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                if attempt == max_retries - 1:
                    raise

            except APIConnectionError as e:
                logger.error(f"Connection error with OpenAI: {e}")
                if attempt == max_retries - 1:
                    raise

            except APIError as e:
                logger.error(f"OpenAI API error: {e}")
                if attempt == max_retries - 1:
                    raise

        raise RuntimeError(f"Failed to get response from OpenAI after {max_retries} attempts")

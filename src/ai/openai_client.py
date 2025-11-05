"""OpenAI Client with retry logic and token counting."""
import os
import json
import time
from typing import List, Dict, Optional
from openai import OpenAI, APIError, RateLimitError, APIConnectionError

from src.utils.logger import logger


class OpenAIClient:
    """Client for OpenAI API with error handling."""

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
                    kwargs['functions'] = functions
                    kwargs['function_call'] = function_call or "auto"

                logger.debug(f"OpenAI request: {len(messages)} messages, model={self.model}")

                response = self.client.chat.completions.create(**kwargs)

                result = response.choices[0].message
                logger.info(f"OpenAI response received")
                return result

            except RateLimitError as e:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"Rate limit hit. Waiting {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                if attempt == max_retries - 1:
                    raise

            except APIConnectionError as e:
                logger.error(f"Connection error with OpenAI: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2)

            except APIError as e:
                logger.error(f"OpenAI API error: {e}")
                raise

        raise Exception("Max retries exceeded")

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.model)
            return len(encoding.encode(text))
        except Exception as e:
            logger.warning(f"Could not count tokens: {e}")
            # Rough estimate: 1 token ≈ 4 characters
            return len(text) // 4

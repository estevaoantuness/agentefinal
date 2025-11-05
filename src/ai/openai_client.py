"""Groq Client with retry logic and token counting."""
import os
import json
import time
from typing import List, Dict, Optional
from groq import Groq, APIError, RateLimitError, APIConnectionError

from src.utils.logger import logger


class OpenAIClient:
    """Client for Groq API with error handling (compatible with OpenAI interface)."""

    def __init__(self):
        """Initialize Groq client."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        self.client = Groq(api_key=api_key)
        self.model = os.getenv('OPENAI_MODEL', 'mixtral-8x7b-32768')
        self.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '500'))
        self.temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))

        logger.info(f"Groq Client initialized: model={self.model}")

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        functions: Optional[List[Dict]] = None,
        function_call: Optional[str] = None,
        max_retries: int = 3
    ) -> Dict:
        """
        Call Groq Chat Completion with retry logic.

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

                logger.debug(f"Groq request: {len(messages)} messages, model={self.model}")

                response = self.client.chat.completions.create(**kwargs)

                result = response.choices[0].message
                logger.info(f"Groq response received")
                return result

            except RateLimitError as e:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"Rate limit hit. Waiting {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                if attempt == max_retries - 1:
                    raise

            except APIConnectionError as e:
                logger.error(f"Connection error with Groq: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2)

            except APIError as e:
                logger.error(f"Groq API error: {e}")
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

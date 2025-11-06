"""OpenAI Client - MAIN LLM for text processing with full system prompt."""

import os
import json
import time
from typing import List, Dict, Optional
from openai import OpenAI, RateLimitError, APIConnectionError, APIError

from src.utils.logger import logger
from .system_prompt import (
    get_system_prompt,
    get_function_definitions,
    MODEL_CONFIG,
    SYSTEM_MESSAGES
)


class OpenAIClient:
    """OpenAI Client for GPT-4o-mini with complete Pangeia Bot system prompt."""

    def __init__(self):
        """Initialize OpenAI client."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        self.client = OpenAI(api_key=api_key)
        self.model = MODEL_CONFIG["model"]
        self.temperature = MODEL_CONFIG["temperature"]
        self.max_tokens = MODEL_CONFIG["max_tokens"]
        self.top_p = MODEL_CONFIG["top_p"]
        self.frequency_penalty = MODEL_CONFIG["frequency_penalty"]
        self.presence_penalty = MODEL_CONFIG["presence_penalty"]

        logger.info(f"OpenAI Client initialized: model={self.model}, "
                   f"temp={self.temperature}, tokens={self.max_tokens}")

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        user_id: str = None,
        user_name: str = None,
        functions: Optional[List[Dict]] = None,
        function_call: Optional[str] = None,
        max_retries: int = 3
    ) -> Dict:
        """
        Call OpenAI Chat Completion with Pangeia Bot system prompt.

        Args:
            messages: Message history list
            user_id: User ID for logging
            user_name: User name for personalization
            functions: List of function definitions (uses defaults if None)
            function_call: "auto" or specific function name
            max_retries: Maximum retry attempts

        Returns:
            Response object with content, function_call, and metadata
        """
        for attempt in range(max_retries):
            try:
                # Build full message list without duplicating system prompt
                full_messages = [m.copy() for m in messages] if messages else []

                if not full_messages:
                    full_messages = [{
                        "role": "system",
                        "content": get_system_prompt(user_name)
                    }]
                elif full_messages[0].get("role") == "system":
                    # Refresh system prompt to keep personalization up to date
                    full_messages[0]["content"] = get_system_prompt(user_name)
                else:
                    full_messages.insert(0, {
                        "role": "system",
                        "content": get_system_prompt(user_name)
                    })

                # Build API call parameters
                kwargs = {
                    'model': self.model,
                    'messages': full_messages,
                    'temperature': self.temperature,
                    'max_tokens': self.max_tokens,
                    'top_p': self.top_p,
                    'frequency_penalty': self.frequency_penalty,
                    'presence_penalty': self.presence_penalty,
                }

                # Add user ID if provided (for tracking)
                if user_id:
                    kwargs['user'] = user_id

                # Add functions if available
                if functions is None:
                    functions = get_function_definitions()

                tools = []
                if functions:
                    for f in functions:
                        if not isinstance(f, dict):
                            continue

                        if f.get('type') == 'function' and 'function' in f:
                            tools.append(f)
                        elif 'name' in f:
                            tools.append({
                                'type': 'function',
                                'function': {
                                    'name': f.get('name'),
                                    'description': f.get('description', ''),
                                    'parameters': f.get('parameters', {'type': 'object'})
                                }
                            })

                if tools:
                    kwargs['tools'] = tools
                    if function_call is not None:
                        kwargs['tool_choice'] = function_call

                logger.debug(f"OpenAI request: {len(messages)} messages, "
                            f"model={self.model}, user={user_name or user_id}")

                # Call OpenAI API
                response = self.client.chat.completions.create(**kwargs)

                message = response.choices[0].message

                # Build result object
                result = {
                    'content': message.content or "",
                    'function_call': None,
                    'finish_reason': response.choices[0].finish_reason,
                    'usage': {
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens,
                    }
                }

                # Handle tool calls (function calling)
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    tool_call = message.tool_calls[0]

                    arguments = tool_call.function.arguments
                    raw_arguments = arguments
                    if isinstance(arguments, str):
                        try:
                            parsed_arguments = json.loads(arguments)
                        except json.JSONDecodeError:
                            logger.warning(
                                "Failed to parse tool arguments as JSON; returning raw string"
                            )
                            parsed_arguments = arguments
                    else:
                        parsed_arguments = arguments

                    result['function_call'] = {
                        'id': getattr(tool_call, 'id', None),
                        'name': tool_call.function.name,
                        'arguments': parsed_arguments,
                        'arguments_json': raw_arguments if isinstance(raw_arguments, str) else json.dumps(raw_arguments)
                    }
                    logger.info(f"OpenAI function call: {tool_call.function.name}")

                logger.info(f"OpenAI response: finish_reason={result['finish_reason']}, "
                           f"tokens={result['usage']['total_tokens']}")

                return result

            except RateLimitError as e:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"OpenAI rate limit. Waiting {wait_time}s... "
                             f"(attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                if attempt == max_retries - 1:
                    raise

            except APIConnectionError as e:
                logger.error(f"OpenAI connection error: {e}")
                if attempt == max_retries - 1:
                    raise

            except APIError as e:
                logger.error(f"OpenAI API error: {e}")
                if attempt == max_retries - 1:
                    raise

        # Should not reach here
        raise RuntimeError(f"Failed to get response from OpenAI after {max_retries} attempts")

    def get_system_message(self, user_name: str = None) -> Dict[str, str]:
        """Get system message for conversation."""
        return {
            "role": "system",
            "content": get_system_prompt(user_name)
        }

    def get_error_response(self, error_key: str = 'error_generic') -> str:
        """Get a system error message."""
        return SYSTEM_MESSAGES.get(error_key, SYSTEM_MESSAGES['error_generic'])

"""Groq Client - ONLY for audio processing (speech-to-text, text-to-speech).

This client is ISOLATED to audio processing only.
OpenAI is the primary LLM for text generation.
"""

import os
import time
from groq import Groq, APIError, RateLimitError, APIConnectionError

from src.utils.logger import logger


class GroqAudioClient:
    """Groq Client for audio processing (transcription, etc)."""

    def __init__(self):
        """Initialize Groq client for audio only."""
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            logger.warning("GROQ_API_KEY not found - audio processing disabled")
            self.client = None
            return

        self.client = Groq(api_key=api_key)
        logger.info("Groq Audio Client initialized (for audio processing only)")

    def transcribe_audio(self, audio_file_path: str, max_retries: int = 3) -> str:
        """
        Transcribe audio file using Groq.

        Args:
            audio_file_path: Path to audio file
            max_retries: Maximum retry attempts

        Returns:
            Transcribed text
        """
        if not self.client:
            logger.error("Groq client not initialized")
            return None

        for attempt in range(max_retries):
            try:
                with open(audio_file_path, 'rb') as audio_file:
                    transcript = self.client.audio.transcriptions.create(
                        file=audio_file,
                        model="whisper-large-v3"
                    )

                logger.info(f"Audio transcribed successfully")
                return transcript.text

            except RateLimitError as e:
                wait_time = 2 ** attempt
                logger.warning(f"Groq rate limit. Waiting {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                if attempt == max_retries - 1:
                    raise

            except APIConnectionError as e:
                logger.error(f"Connection error with Groq: {e}")
                if attempt == max_retries - 1:
                    raise

            except APIError as e:
                logger.error(f"Groq API error: {e}")
                if attempt == max_retries - 1:
                    raise

        return None

# Global audio client instance
_audio_client = None


def get_audio_client() -> GroqAudioClient:
    """Get or create Groq audio client."""
    global _audio_client
    if _audio_client is None:
        _audio_client = GroqAudioClient()
    return _audio_client

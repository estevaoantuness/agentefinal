"""Text normalization utilities."""
import re
import unicodedata
from typing import Optional


class TextNormalizer:
    """Utility class to normalize text, numbers, and phones."""

    NUMBER_MAP = {
        "zero": 0,
        "um": 1,
        "uma": 1,
        "dois": 2,
        "duas": 2,
        "três": 3,
        "tres": 3,
        "quatro": 4,
        "cinco": 5,
        "seis": 6,
        "sete": 7,
        "oito": 8,
        "nove": 9,
        "dez": 10,
    }

    @staticmethod
    def remove_accents(text: str) -> str:
        """Remove diacritics from text."""
        if not text:
            return text
        normalized = unicodedata.normalize("NFD", text)
        return "".join(char for char in normalized if unicodedata.category(char) != "Mn")

    @classmethod
    def convert_written_numbers(cls, text: str) -> str:
        """Convert written numbers (portuguese) to digits."""
        if not text:
            return text

        def replace_match(match: re.Match) -> str:
            word = match.group(0)
            return str(cls.NUMBER_MAP.get(word, word))

        pattern = re.compile(r"\b(" + "|".join(cls.NUMBER_MAP.keys()) + r")\b", re.IGNORECASE)
        return pattern.sub(lambda m: replace_match(m).lower(), text)

    @staticmethod
    def normalize_phone(phone: Optional[str]) -> Optional[str]:
        """Normalize phone numbers by removing non-digits and ensuring country code."""
        if not phone:
            return phone
        digits = re.sub(r"\D", "", phone)
        if not digits:
            return None
        if digits.startswith("55"):
            return digits
        if digits.startswith("0"):
            digits = digits[1:]
        if len(digits) < 11:
            digits = "55" + digits
        return digits

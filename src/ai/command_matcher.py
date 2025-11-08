"""NLP-like command matching with normalization and slots."""

import json
import re
from typing import Optional, Dict, Any

import yaml

from src.utils.logger import logger
from src.utils.text_normalizer import TextNormalizer
from src.ai.slot_tracker import SlotTracker


class CommandMatcher:
    """Intent matcher powered by regex + slot tracking."""

    def __init__(self, intents_path: str = "config/intents.yaml"):
        self.normalizer = TextNormalizer()
        self.slot_tracker = SlotTracker()
        self.intents = self._load_intents(intents_path)

    def _load_intents(self, path: str) -> Dict[str, Any]:
        try:
            with open(path, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)
                return config.get("intents", {})
        except FileNotFoundError:
            logger.warning(f"Intents config not found: {path}")
            return {}
        except yaml.YAMLError as exc:
            logger.error(f"Failed to parse intents config: {exc}")
            return {}

    def match(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Try to match user message to a known command pattern.

        Args:
            message: User message text

        Returns:
            Dict with 'function' and 'arguments' or None if no high-confidence match
        """
        if not message or not isinstance(message, str):
            return None

        normalized = self.normalizer.remove_accents(message.lower().strip())
        normalized = self.normalizer.convert_written_numbers(normalized)

        best_match = None
        best_confidence = 0.0

        for intent_name, intent_data in self.intents.items():
            patterns = intent_data.get("patterns", [])
            synonyms = intent_data.get("synonyms", [])
            confidence = float(intent_data.get("confidence", 0))

            candidates = patterns + [re.escape(s.lower()) for s in synonyms]

            for pattern in candidates:
                try:
                    if re.search(pattern, normalized, re.IGNORECASE):
                        if confidence > best_confidence:
                            args = self._extract_arguments(intent_name, normalized, pattern)
                            missing = self.slot_tracker.check_missing_slots(intent_name, args)
                            best_match = {
                                "function": intent_name,
                                "arguments": args,
                                "confidence": confidence,
                                "missing_slots": missing,
                            }
                            best_confidence = confidence
                        break
                except re.error as exc:
                    logger.warning(f"Invalid regex '{pattern}': {exc}")

        return best_match

    def _extract_arguments(
        self,
        function_name: str,
        message: str,
        regex_match: re.Match
    ) -> Dict[str, Any]:
        """
        Extract function arguments from matched message.

        Args:
            function_name: Name of the matched function
            message: Original message (lowercased)
            regex_match: The regex match object

        Returns:
            Dictionary of arguments for the function
        """

        if function_name == 'view_tasks':
            # Check for status filter
            if 'pendente' in message or 'nao iniciada' in message:
                return {'filter_status': 'pending'}
            elif 'andamento' in message or 'começada' in message:
                return {'filter_status': 'in_progress'}
            elif 'concluída' in message or 'completa' in message or 'feita' in message:
                return {'filter_status': 'completed'}
            return {'filter_status': 'all'}

        elif function_name == 'create_task':
            # Extract task title from message
            # Look for patterns: "criar tarefa: title" or "nova tarefa title"
            title_match = re.search(
                r'(?:criar|nova|adicionar|inserir|cria|add)\s+tarefa[:\s]+(.+)',
                message,
                re.IGNORECASE
            )
            if title_match:
                title = title_match.group(1).strip()
                return {'title': title}
            return {}

        elif function_name in ['mark_done', 'mark_progress']:
            # Extract task numbers from the message
            numbers = re.findall(r'\b(\d+)\b', message)
            task_numbers = [int(n) for n in numbers if 0 < int(n) < 1000]
            return {'task_numbers': task_numbers if task_numbers else []}

        elif function_name in ['view_progress', 'get_help']:
            # These don't need arguments
            return {}

        return {}


# Global singleton instance
command_matcher = CommandMatcher()

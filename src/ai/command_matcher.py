"""
NLP-like command matching system for reliable intent detection.

Provides fallback command recognition when LLM function calling fails.
Uses regex patterns to detect common user intents before calling Groq.
"""

import re
import json
from typing import Optional, Dict, Any
from src.utils.logger import logger


class CommandMatcher:
    """Simple but reliable command pattern matching system."""

    def __init__(self):
        """Initialize command patterns for common intents."""
        # Regex patterns for each command - multiple synonyms per command
        self.patterns = {
            'view_tasks': [
                r'\b(minhas?\s+tarefa|ver\s+tarefa|lista|listar|mostrar\s+tarefa|quais?\s+tarefa)',
                r'\b(o\s+que\s+tenho|que\s+tenho\s+(pra\s+)?fazer|tarefas?)',
                r'\b(tarefas?\s+(pendente|em\s+andamento|concluída))',
                r'\b(task|todo)',
            ],
            'create_task': [
                r'\b(criar|nova|adicionar|inserir)\s+tarefa',
                r'\bpreciso\s+(fazer|criar)',
                r'\b(tarefa|to-?do):\s+',
                r'\b(cria|add)\s+',
            ],
            'mark_done': [
                r'\b(feito|concluí|completei|finalizei|terminei)\s+(\d+)',
                r'\bmarcar?\s+(como\s+)?(feita|completa|concluída)\s+(\d+)',
                r'\b(done|complete)\s+(\d+)',
                r'\b(pronta|pronto)\s+(\d+)',
            ],
            'mark_progress': [
                r'\b(comecei|iniciei|estou\s+fazendo|comeco|inicio)\s+(\d+)',
                r'\bem\s+andamento\s+(\d+)',
                r'\b(working\s+on|started)\s+(\d+)',
                r'\b(andamento|progresso)\s+(\d+)',
            ],
            'view_progress': [
                r'\b(meu\s+progresso|como\s+(estou\s+)?indo|qual\s+(é\s+)?meu\s+progresso)',
                r'\b(relatório|status)',
                r'\b(progress|how.*going)',
            ],
            'get_help': [
                r'\b(ajuda|help|comandos?|o\s+que\s+(você\s+)?(faz|pode|consegue))',
                r'\b(como\s+funciona|como\s+usar)',
            ],
        }

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

        message_lower = message.lower().strip()

        # Try each command pattern
        for function_name, patterns in self.patterns.items():
            for pattern in patterns:
                try:
                    match = re.search(pattern, message_lower, re.IGNORECASE)
                    if match:
                        logger.info(
                            f"Command matched: {function_name} "
                            f"(pattern: {pattern[:40]}...)"
                        )

                        # Extract arguments based on function type
                        args = self._extract_arguments(
                            function_name,
                            message_lower,
                            match
                        )

                        return {
                            'function': function_name,
                            'arguments': args,
                            'confidence': 'high'
                        }
                except Exception as e:
                    logger.warning(f"Error matching pattern '{pattern}': {e}")
                    continue

        return None

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
            return {}  # Let LLM handle title extraction in conversation

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

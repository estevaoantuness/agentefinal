"""Utilities to humanize bot responses."""
import random
from typing import List, Dict, Any, Optional

import yaml

from src.ai.motivator import Motivator
from src.utils.logger import logger


class MessageHumanizer:
    """Load templates and generate natural responses."""

    def __init__(self, templates_path: str = "config/response_templates.yaml"):
        self.templates = self._load_templates(templates_path)
        self.motivator = Motivator()

    def _load_templates(self, path: str) -> Dict[str, List[Dict[str, Any]]]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data or {}
        except FileNotFoundError:
            logger.warning(f"Response templates not found at {path}")
            return {}
        except yaml.YAMLError as exc:
            logger.error(f"Could not parse response templates: {exc}")
            return {}

    def _choose_template(self, category: str) -> Optional[str]:
        options = self.templates.get(category, [])
        if not options:
            return None
        weights = [tpl.get("weight", 1) for tpl in options]
        return random.choices(options, weights=weights, k=1)[0].get("template")

    def humanize_confirmation(self, task_name: str, action: str) -> str:
        template = self._choose_template("confirmation") or "✅ {action}: {task_name}"
        return template.format(action=action or "Tarefa", task_name=task_name or "tarefa")

    def humanize_list(self, tasks: List[str], progress: Optional[Dict[str, Any]] = None) -> str:
        template = self._choose_template("task_list") or "📋 Tarefas:\n{body}"
        body = "\n".join(tasks)
        motivation = ""
        if progress:
            percentage = progress.get("percentage", 0)
            motivation = self.motivator.get_motivation(percentage)
        return template.format(body=body, motivation=motivation)

    def humanize_progress(self, stats: Dict[str, Any]) -> str:
        template = self._choose_template("progress_report") or (
            "📊 Progresso: {completed}/{total} ({percentage:.1f}%). {motivation}"
        )
        motivation = self.motivator.get_motivation(stats.get("percentage", 0))
        return template.format(
            total=stats.get("total", 0),
            completed=stats.get("completed", 0),
            pending=stats.get("pending", 0),
            in_progress=stats.get("in_progress", 0),
            percentage=stats.get("percentage", 0.0),
            motivation=motivation
        )

    def chunk_long_message(self, text: str, max_length: int = 160) -> List[str]:
        if not text:
            return []
        if len(text) <= max_length:
            return [text]
        words = text.split()
        chunks: List[str] = []
        current: List[str] = []
        for word in words:
            if sum(len(w) + 1 for w in current) + len(word) > max_length:
                chunks.append(" ".join(current).strip())
                current = [word]
            else:
                current.append(word)
        if current:
            chunks.append(" ".join(current).strip())
        return chunks

    def add_contextual_emoji(self, text: str, context: Optional[str]) -> str:
        if not text:
            return text
        emojis_by_context = {
            "create_task": "🆕",
            "mark_done": "✅",
            "mark_progress": "⏳",
            "view_tasks": "📋",
            "view_progress": "📊",
            "greeting": "😊",
            "default": "💬",
        }
        chosen = emojis_by_context.get(context or "", emojis_by_context["default"])
        emoji_count = sum(1 for char in text if char in emojis_by_context.values())
        if emoji_count >= 2:
            return text
        if chosen and chosen not in text:
            return f"{chosen} {text}" if not text.startswith(chosen) else text
        return text

    def humanize_error(self, message: str) -> str:
        template = self._choose_template("error") or "Ops! {message}"
        return template.format(message=message)

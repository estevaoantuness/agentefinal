"""Motivational helper utilities."""
from typing import Optional


class Motivator:
    """Provide motivational messages and emojis based on progress."""

    def get_motivation(self, progress_percentage: float) -> str:
        if progress_percentage >= 70:
            return "Você tá arrasando! 🔥"
        if progress_percentage >= 30:
            return "Belo ritmo, continue assim! 💪"
        return "Vamos lá, uma de cada vez!"

    def get_emoji_by_status(self, task_status: Optional[str]) -> str:
        status = (task_status or "").lower()
        if status == "completed":
            return "✅"
        if status == "in_progress":
            return "🔄"
        if status == "pending":
            return "⬜"
        return "💡"

"""Helper utility functions."""
from datetime import datetime, timedelta
from typing import Optional
import re
import phonenumbers
from dateutil import parser
import pytz

from src.config.settings import settings


def normalize_phone_number(phone: str) -> str:
    """
    Normalize phone number to E.164 format.

    Args:
        phone: Raw phone number

    Returns:
        Normalized phone number
    """
    try:
        # Parse with default region BR
        parsed = phonenumbers.parse(phone, "BR")
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        # If parsing fails, return cleaned version
        return re.sub(r'\D', '', phone)


def parse_datetime_natural(text: str, base_time: Optional[datetime] = None) -> Optional[datetime]:
    """
    Parse natural language datetime expressions.

    Args:
        text: Natural language datetime string
        base_time: Base datetime for relative expressions

    Returns:
        Parsed datetime or None
    """
    if base_time is None:
        tz = pytz.timezone(settings.TIMEZONE)
        base_time = datetime.now(tz)

    text_lower = text.lower().strip()

    # Relative times
    if "amanhã" in text_lower or "amanha" in text_lower:
        return base_time + timedelta(days=1)
    elif "hoje" in text_lower:
        return base_time
    elif "próxima semana" in text_lower or "proxima semana" in text_lower:
        return base_time + timedelta(weeks=1)
    elif "próximo mês" in text_lower or "proximo mes" in text_lower:
        return base_time + timedelta(days=30)

    # Hours/minutes
    hours_match = re.search(r'em (\d+) hora[s]?', text_lower)
    if hours_match:
        hours = int(hours_match.group(1))
        return base_time + timedelta(hours=hours)

    minutes_match = re.search(r'em (\d+) minuto[s]?', text_lower)
    if minutes_match:
        minutes = int(minutes_match.group(1))
        return base_time + timedelta(minutes=minutes)

    # Try parsing with dateutil
    try:
        return parser.parse(text, default=base_time, fuzzy=True)
    except (ValueError, TypeError):
        return None


def format_task_list(tasks: list) -> str:
    """
    Format a list of tasks for WhatsApp display.

    Args:
        tasks: List of Task objects

    Returns:
        Formatted string
    """
    if not tasks:
        return "📋 Você não tem tarefas no momento."

    lines = ["📋 *Suas Tarefas*\n"]

    for i, task in enumerate(tasks, 1):
        status_emoji = {
            "pending": "⏳",
            "in_progress": "🔄",
            "completed": "✅",
            "cancelled": "❌"
        }.get(task.status, "📌")

        priority_emoji = {
            "low": "🔵",
            "medium": "🟡",
            "high": "🟠",
            "urgent": "🔴"
        }.get(task.priority, "⚪")

        line = f"{i}. {status_emoji} {priority_emoji} *{task.title}*"

        if task.due_date:
            due_str = task.due_date.strftime("%d/%m/%Y")
            line += f" - 📅 {due_str}"

        if task.category:
            line += f" - 🏷️ {task.category.name}"

        lines.append(line)

    return "\n".join(lines)


def extract_task_info(message: str) -> dict:
    """
    Extract task information from natural language message.

    Args:
        message: User message

    Returns:
        Dictionary with extracted info
    """
    info = {
        "title": None,
        "due_date": None,
        "priority": "medium"
    }

    # Try to extract title (simplified)
    title_patterns = [
        r'criar tarefa[:\s]+(.+)',
        r'nova tarefa[:\s]+(.+)',
        r'adicionar tarefa[:\s]+(.+)',
        r'tarefa[:\s]+(.+)'
    ]

    for pattern in title_patterns:
        match = re.search(pattern, message.lower())
        if match:
            info["title"] = match.group(1).strip()
            break

    # Extract priority
    if any(word in message.lower() for word in ["urgente", "urgência"]):
        info["priority"] = "urgent"
    elif any(word in message.lower() for word in ["alta prioridade", "importante"]):
        info["priority"] = "high"
    elif any(word in message.lower() for word in ["baixa prioridade"]):
        info["priority"] = "low"

    # Extract due date
    info["due_date"] = parse_datetime_natural(message)

    return info

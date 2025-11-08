"""Slack webhook notifier for task events."""
import json
from typing import Optional

import requests

from src.config.settings import settings
from src.utils.logger import logger


class SlackNotifier:
    """Send formatted notifications to Slack via Incoming Webhooks."""

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or settings.SLACK_WEBHOOK_URL

    def _post(self, payload: dict) -> bool:
        if not self.webhook_url:
            return False
        try:
            resp = requests.post(
                self.webhook_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=5
            )
            resp.raise_for_status()
            return True
        except requests.RequestException as exc:  # pragma: no cover
            logger.error(f"Slack webhook failed: {exc}")
            return False

    def notify_task_created(self, task_name: str, user_name: Optional[str]) -> bool:
        text = f"🆕 Tarefa criada por {user_name or 'usuário'}: *{task_name}*"
        return self._post({"text": text})

    def notify_task_completed(self, task_name: str, user_name: Optional[str]) -> bool:
        text = f"✅ {user_name or 'Usuário'} concluiu: *{task_name}*"
        return self._post({"text": text})

    def notify_progress(self, user_name: str, completed: int, total: int, percentage: float) -> bool:
        text = (
            f"📊 Progresso de {user_name or 'usuário'}: {completed}/{total} tarefas "
            f"({percentage:.1f}%)."
        )
        return self._post({"text": text})


slack_notifier = SlackNotifier()

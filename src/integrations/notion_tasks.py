"""
Notion Task Manager - Manages Groq's interaction with Notion task database.

This module provides an interface for Groq to:
- Read all tasks from Notion database
- Update task status and progress
- Format task information for AI comprehension
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from notion_client import Client
from src.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class NotionTaskReader:
    """Read and manage tasks from Notion database for Groq."""

    def __init__(self):
        """Initialize Notion client and database ID."""
        self.client = Client(auth=settings.NOTION_API_KEY)
        self.db_id = os.getenv('NOTION_GROQ_TASKS_DB_ID')

        if not self.db_id:
            logger.warning("NOTION_GROQ_TASKS_DB_ID not configured - Groq task management disabled")

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all tasks from Notion database.

        Returns:
            List of task dictionaries with all properties
        """
        if not self.db_id:
            logger.warning("Cannot get tasks - NOTION_GROQ_TASKS_DB_ID not set")
            return []

        try:
            response = self.client.databases.query(database_id=self.db_id)
            tasks = []

            for page in response.get('results', []):
                task = self._parse_task_page(page)
                if task:
                    tasks.append(task)

            logger.info(f"Retrieved {len(tasks)} tasks from Notion")
            return tasks

        except Exception as e:
            logger.error(f"Error retrieving tasks from Notion: {e}")
            return []

    def get_tasks_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get tasks filtered by status.

        Args:
            status: Status to filter by (e.g., 'Not Started', 'In Progress', 'Completed')

        Returns:
            List of tasks matching the status
        """
        if not self.db_id:
            return []

        try:
            response = self.client.databases.query(
                database_id=self.db_id,
                filter={
                    "property": "Status",
                    "status": {"equals": status}
                }
            )

            tasks = []
            for page in response.get('results', []):
                task = self._parse_task_page(page)
                if task:
                    tasks.append(task)

            logger.info(f"Retrieved {len(tasks)} tasks with status '{status}'")
            return tasks

        except Exception as e:
            logger.error(f"Error retrieving tasks with status '{status}': {e}")
            return []

    def get_high_priority_tasks(self) -> List[Dict[str, Any]]:
        """
        Get high priority and urgent tasks.

        Returns:
            List of high/urgent priority tasks
        """
        if not self.db_id:
            return []

        try:
            response = self.client.databases.query(
                database_id=self.db_id,
                filter={
                    "or": [
                        {"property": "Priority", "select": {"equals": "High"}},
                        {"property": "Priority", "select": {"equals": "Urgent"}}
                    ]
                }
            )

            tasks = []
            for page in response.get('results', []):
                task = self._parse_task_page(page)
                if task:
                    tasks.append(task)

            logger.info(f"Retrieved {len(tasks)} high priority tasks")
            return tasks

        except Exception as e:
            logger.error(f"Error retrieving high priority tasks: {e}")
            return []

    def update_task_status(self, task_id: str, new_status: str) -> bool:
        """
        Update task status in Notion.

        Args:
            task_id: Notion page ID of the task
            new_status: New status (Not Started, In Progress, Completed, On Hold, Blocked)

        Returns:
            True if update successful, False otherwise
        """
        try:
            self.client.pages.update(
                page_id=task_id,
                properties={
                    "Status": {
                        "status": {"name": new_status}
                    }
                }
            )
            logger.info(f"Updated task {task_id} status to '{new_status}'")
            return True

        except Exception as e:
            logger.error(f"Error updating task status: {e}")
            return False

    def update_task_progress(self, task_id: str, progress_percent: float) -> bool:
        """
        Update task progress percentage.

        Args:
            task_id: Notion page ID of the task
            progress_percent: Progress percentage (0-100)

        Returns:
            True if update successful, False otherwise
        """
        # Clamp progress to valid range
        progress = max(0, min(100, progress_percent))
        progress_decimal = progress / 100

        try:
            self.client.pages.update(
                page_id=task_id,
                properties={
                    "Progress": {
                        "number": progress_decimal
                    }
                }
            )
            logger.info(f"Updated task {task_id} progress to {progress}%")
            return True

        except Exception as e:
            logger.error(f"Error updating task progress: {e}")
            return False

    def format_for_groq(self, tasks: List[Dict[str, Any]]) -> str:
        """
        Format tasks in a way Groq can easily understand and process.

        Args:
            tasks: List of task dictionaries

        Returns:
            Formatted string representation of tasks for Groq
        """
        if not tasks:
            return "Não há tarefas no banco de dados."

        formatted = "📋 **TAREFAS GERENCIADAS PELO GROQ**\n\n"

        for i, task in enumerate(tasks, 1):
            formatted += f"{i}. **{task.get('title', 'Untitled')}**\n"

            if task.get('status'):
                formatted += f"   Status: {task['status']}\n"

            if task.get('priority'):
                formatted += f"   Prioridade: {task['priority']}\n"

            if task.get('progress') is not None:
                progress_pct = task['progress'] * 100
                formatted += f"   Progresso: {progress_pct:.0f}%\n"

            if task.get('effort_hours'):
                formatted += f"   Esforço estimado: {task['effort_hours']} horas\n"

            if task.get('due_date'):
                formatted += f"   Prazo: {task['due_date']}\n"

            if task.get('description'):
                formatted += f"   Descrição: {task['description']}\n"

            formatted += "\n"

        return formatted

    def format_summary_for_groq(self, tasks: List[Dict[str, Any]]) -> str:
        """
        Create a concise summary of tasks for Groq's decision-making.

        Args:
            tasks: List of task dictionaries

        Returns:
            Compact JSON string for Groq to analyze
        """
        summary = {
            "total_tasks": len(tasks),
            "by_status": {},
            "by_priority": {},
            "average_progress": 0,
            "tasks": []
        }

        total_progress = 0

        for task in tasks:
            # Count by status
            status = task.get('status', 'Unknown')
            summary['by_status'][status] = summary['by_status'].get(status, 0) + 1

            # Count by priority
            priority = task.get('priority', 'Unknown')
            summary['by_priority'][priority] = summary['by_priority'].get(priority, 0) + 1

            # Track progress
            progress = task.get('progress', 0)
            total_progress += progress

            # Add task summary
            task_summary = {
                "id": task.get('id'),
                "title": task.get('title'),
                "status": status,
                "priority": priority,
                "progress": progress,
                "effort": task.get('effort_hours'),
                "due": task.get('due_date')
            }
            summary['tasks'].append(task_summary)

        if tasks:
            summary['average_progress'] = round(total_progress / len(tasks), 2)

        return json.dumps(summary, ensure_ascii=False, indent=2)

    def _parse_task_page(self, page: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse a Notion page into a task dictionary.

        Args:
            page: Raw Notion page object

        Returns:
            Dictionary with task properties or None if parsing fails
        """
        try:
            properties = page.get('properties', {})

            task = {
                'id': page.get('id'),
                'created': page.get('created_time'),
                'updated': page.get('last_edited_time')
            }

            # Extract title
            title_prop = properties.get('Task Name', {})
            if title_prop.get('type') == 'title':
                title_text = title_prop.get('title', [])
                task['title'] = title_text[0]['text']['content'] if title_text else 'Untitled'

            # Extract status
            status_prop = properties.get('Status', {})
            if status_prop.get('type') == 'status':
                task['status'] = status_prop.get('status', {}).get('name', 'Not Started')

            # Extract priority
            priority_prop = properties.get('Priority', {})
            if priority_prop.get('type') == 'select':
                task['priority'] = priority_prop.get('select', {}).get('name', 'Medium')

            # Extract progress
            progress_prop = properties.get('Progress', {})
            if progress_prop.get('type') == 'number':
                progress_value = progress_prop.get('number', 0)
                task['progress'] = progress_value if progress_value else 0

            # Extract effort hours
            effort_prop = properties.get('Effort Hours', {})
            if effort_prop.get('type') == 'number':
                task['effort_hours'] = effort_prop.get('number')

            # Extract due date
            due_prop = properties.get('Due Date', {})
            if due_prop.get('type') == 'date':
                date_obj = due_prop.get('date', {})
                if date_obj:
                    task['due_date'] = date_obj.get('start')

            # Extract description
            desc_prop = properties.get('Description', {})
            if desc_prop.get('type') == 'rich_text':
                desc_text = desc_prop.get('rich_text', [])
                task['description'] = desc_text[0]['text']['content'] if desc_text else None

            # Extract category
            category_prop = properties.get('Category', {})
            if category_prop.get('type') == 'select':
                task['category'] = category_prop.get('select', {}).get('name')

            # Extract tags
            tags_prop = properties.get('Tags', {})
            if tags_prop.get('type') == 'multi_select':
                tags = tags_prop.get('multi_select', [])
                task['tags'] = [tag['name'] for tag in tags]

            return task

        except Exception as e:
            logger.error(f"Error parsing task page: {e}")
            return None


# Singleton instance for easy access
_notion_task_reader = None


def get_notion_task_reader() -> NotionTaskReader:
    """Get singleton instance of NotionTaskReader."""
    global _notion_task_reader
    if _notion_task_reader is None:
        _notion_task_reader = NotionTaskReader()
    return _notion_task_reader

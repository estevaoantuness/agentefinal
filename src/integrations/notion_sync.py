"""Notion API integration for task synchronization."""
import os
from notion_client import Client
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from src.config.settings import settings
from src.database.models import Task, User, TaskStatus, TaskPriority
from src.utils.logger import logger


class NotionSync:
    """Notion synchronization service."""

    def __init__(self):
        self.client = Client(auth=settings.NOTION_API_KEY)
        self.default_database_id = settings.NOTION_DATABASE_ID
        # Allow overriding property names via env vars when the Notion DB uses custom labels
        self.title_props = [
            os.getenv("NOTION_TITLE_PROPERTY") or "Nome",
            "Name",
            "Título",
            "Title",
        ]
        self.status_props = [
            os.getenv("NOTION_STATUS_PROPERTY") or "Status",
        ]
        self.priority_props = [
            os.getenv("NOTION_PRIORITY_PROPERTY") or "Prioridade",
            "Priority",
        ]
        self.description_props = [
            os.getenv("NOTION_DESCRIPTION_PROPERTY") or "Descrição",
            "Description",
            "Notas",
        ]
        self.due_date_props = [
            os.getenv("NOTION_DUE_DATE_PROPERTY") or "Prazo",
            "Due Date",
            "Deadline",
        ]

    def _resolve_database_id(self, user: Optional[User] = None) -> Optional[str]:
        if user and getattr(user, "notion_database_id", None):
            return user.notion_database_id
        return self.default_database_id

    def _get_property(self, props: Dict[str, Any], candidates: List[str]) -> Optional[Dict[str, Any]]:
        """Return the first non-null Notion property dict matching the candidate list."""
        for name in candidates:
            value = props.get(name)
            if value is not None:
                return value
        return None

    def _task_to_notion_properties(self, task: Task) -> Dict[str, Any]:
        """
        Convert Task object to Notion properties format.

        Args:
            task: Task object

        Returns:
            Notion properties dictionary
        """
        title_key = self.title_props[0]
        status_key = self.status_props[0]
        priority_key = self.priority_props[0]
        description_key = self.description_props[0]
        due_date_key = self.due_date_props[0]

        properties = {
            title_key: {
                "title": [
                    {
                        "text": {
                            "content": task.title
                        }
                    }
                ]
            },
            status_key: {
                "select": {
                    "name": {
                        "pending": "A Fazer",
                        "in_progress": "Em Andamento",
                        "completed": "Concluído",
                        "cancelled": "Cancelado"
                    }.get(task.status, "A Fazer")
                }
            },
            priority_key: {
                "select": {
                    "name": {
                        "low": "Baixa",
                        "medium": "Média",
                        "high": "Alta",
                        "urgent": "Urgente"
                    }.get(task.priority, "Média")
                }
            }
        }

        # Add description
        if task.description:
            properties[description_key] = {
                "rich_text": [
                    {
                        "text": {
                            "content": task.description[:2000]  # Notion limit
                        }
                    }
                ]
            }

        # Add due date
        if task.due_date:
            properties[due_date_key] = {
                "date": {
                    "start": task.due_date.isoformat()
                }
            }

        return properties

    def _notion_to_task_data(self, notion_page: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Notion page to Task data.

        Args:
            notion_page: Notion page object

        Returns:
            Task data dictionary
        """
        props = notion_page.get("properties", {}) or {}

        # Extract title
        title_property = self._get_property(props, self.title_props) or {}
        title_prop = title_property.get("title", []) if isinstance(title_property, dict) else []
        title = title_prop[0]["text"]["content"] if title_prop else "Untitled"

        # Extract status (handle both select and status property types)
        status_property = self._get_property(props, self.status_props) or {}
        status_block = status_property.get("status", {}) or status_property.get("select", {})
        status_name = status_block.get("name", "A Fazer") if isinstance(status_block, dict) else "A Fazer"
        status = {
            "A Fazer": TaskStatus.PENDING,
            "Em Andamento": TaskStatus.IN_PROGRESS,
            "Concluído": TaskStatus.COMPLETED,
            "Cancelado": TaskStatus.CANCELLED
        }.get(status_name, TaskStatus.PENDING)

        # Extract priority
        priority_property = self._get_property(props, self.priority_props) or {}
        priority_select = priority_property.get("select", {}) if isinstance(priority_property, dict) else {}
        priority_name = priority_select.get("name", "Média")
        priority = {
            "Baixa": TaskPriority.LOW,
            "Média": TaskPriority.MEDIUM,
            "Alta": TaskPriority.HIGH,
            "Urgente": TaskPriority.URGENT
        }.get(priority_name, TaskPriority.MEDIUM)

        # Extract description
        description_property = self._get_property(props, self.description_props) or {}
        desc_prop = description_property.get("rich_text", []) if isinstance(description_property, dict) else []
        description = desc_prop[0]["text"]["content"] if desc_prop else None

        # Extract due date
        due_date_property = self._get_property(props, self.due_date_props) or {}
        date_prop = due_date_property.get("date") if isinstance(due_date_property, dict) else None
        due_date = None
        if date_prop and date_prop.get("start"):
            try:
                due_date = datetime.fromisoformat(date_prop["start"].replace("Z", "+00:00"))
            except ValueError as e:
                logger.warning(f"Failed to parse date from Notion: {e}")

        return {
            "title": title,
            "description": description,
            "status": status,
            "priority": priority,
            "due_date": due_date,
            "notion_id": notion_page["id"]
        }

    def create_task_in_notion(self, task: Task, database_id: Optional[str]) -> Optional[str]:
        """
        Create a task in Notion.

        Args:
            task: Task object

        Returns:
            Notion page ID or None
        """
        database_id = database_id or self.default_database_id
        if not database_id:
            logger.warning("No Notion database configured for create_task_in_notion")
            return None

        try:
            properties = self._task_to_notion_properties(task)

            response = self.client.pages.create(
                parent={"database_id": database_id},
                properties=properties
            )

            notion_id = response["id"]
            logger.info(f"Task {task.id} created in Notion: {notion_id}")

            return notion_id

        except Exception as e:
            logger.error(f"Error creating task in Notion: {e}")
            return None

    def update_task_in_notion(self, task: Task) -> bool:
        """
        Update a task in Notion.

        Args:
            task: Task object with notion_id

        Returns:
            Success status
        """
        if not task.notion_id:
            logger.warning(f"Task {task.id} has no notion_id")
            return False

        try:
            properties = self._task_to_notion_properties(task)

            self.client.pages.update(
                page_id=task.notion_id,
                properties=properties
            )

            logger.info(f"Task {task.id} updated in Notion")
            return True

        except Exception as e:
            logger.error(f"Error updating task in Notion: {e}")
            return False

    def sync_from_notion_to_db(self, user: User, db: Session) -> int:
        """
        Sync tasks from Notion to database.

        Args:
            user: User object
            db: Database session

        Returns:
            Number of tasks synced
        """
        database_id = self._resolve_database_id(user)
        if not database_id:
            logger.warning(
                f"User {user.id} has no Notion database configured and no global database set"
            )
            return 0

        def _query_database():
            """Query database without filters to avoid status type mismatches."""
            # Query without filters - get all tasks (filter by status later if needed)
            return self.client.databases.query(
                database_id=database_id
            )

        try:
            # Query Notion database
            response = _query_database()

            synced_count = 0

            for page in response.get("results", []):
                notion_id = page["id"]
                task_data = self._notion_to_task_data(page)

                # Filter: Only sync if user is in Assignees or Assignee field
                props = page.get("properties", {}) or {}
                assignees_property = self._get_property(props, self.assignees_props) or {}
                assignees_list = assignees_property.get("multi_select", []) if isinstance(assignees_property, dict) else []
                assignee_names = [a.get("name", "") for a in assignees_list if isinstance(a, dict)]

                # Check if user.name is in assignees
                user_name_lower = (user.name or "").lower().strip()
                is_assigned = any(user_name_lower in name.lower() for name in assignee_names) if user_name_lower else False

                # Skip if not assigned to this user (unless no assignees at all)
                if assignee_names and not is_assigned:
                    logger.debug(f"Skipping task (not assigned to {user.name}): {task_data.get('title')}")
                    continue

                # Check if task exists
                task = db.query(Task).filter(
                    Task.notion_id == notion_id,
                    Task.user_id == user.id
                ).first()

                if task:
                    # Update existing task
                    for key, value in task_data.items():
                        if key != "notion_id":
                            setattr(task, key, value)
                    task.last_synced_at = datetime.utcnow()
                else:
                    # Create new task
                    task = Task(
                        user_id=user.id,
                        **task_data
                    )
                    task.last_synced_at = datetime.utcnow()
                    db.add(task)

                synced_count += 1

            db.commit()
            logger.info(f"Synced {synced_count} tasks from Notion for user {user.id}")

            return synced_count

        except Exception as e:
            logger.error(f"Error syncing from Notion: {e}")
            db.rollback()
            return 0

    def sync_from_db_to_notion(self, user: User, db: Session) -> int:
        """
        Sync tasks from database to Notion.

        Args:
            user: User object
            db: Database session

        Returns:
            Number of tasks synced
        """
        database_id = self._resolve_database_id(user)
        if not database_id:
            logger.warning(f"User {user.id} has no Notion database configured for sync_to_notion")
            return 0

        try:
            # Get tasks that need syncing (no notion_id or updated after last sync)
            tasks = db.query(Task).filter(
                Task.user_id == user.id,
                Task.status != TaskStatus.CANCELLED
            ).all()

            synced_count = 0

            for task in tasks:
                if not task.notion_id:
                    # Create in Notion
                    notion_id = self.create_task_in_notion(task, database_id)
                    if notion_id:
                        task.notion_id = notion_id
                        task.last_synced_at = datetime.utcnow()
                        synced_count += 1
                elif not task.last_synced_at or task.updated_at > task.last_synced_at:
                    # Update in Notion
                    if self.update_task_in_notion(task):
                        task.last_synced_at = datetime.utcnow()
                        synced_count += 1

            db.commit()
            logger.info(f"Synced {synced_count} tasks to Notion for user {user.id}")

            return synced_count

        except Exception as e:
            logger.error(f"Error syncing to Notion: {e}")
            db.rollback()
            return 0

    def bidirectional_sync(self, user: User, db: Session) -> Dict[str, int]:
        """
        Perform bidirectional sync between Notion and database.

        Args:
            user: User object
            db: Database session

        Returns:
            Sync statistics
        """
        from_notion = self.sync_from_notion_to_db(user, db)
        to_notion = self.sync_from_db_to_notion(user, db)

        return {
            "from_notion": from_notion,
            "to_notion": to_notion,
            "total": from_notion + to_notion
        }


# Global Notion sync instance
notion_sync = NotionSync()

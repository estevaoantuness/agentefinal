"""Notion API integration for task synchronization."""
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
        self.database_id = settings.NOTION_DATABASE_ID

    def _task_to_notion_properties(self, task: Task) -> Dict[str, Any]:
        """
        Convert Task object to Notion properties format.

        Args:
            task: Task object

        Returns:
            Notion properties dictionary
        """
        properties = {
            "Nome": {
                "title": [
                    {
                        "text": {
                            "content": task.title
                        }
                    }
                ]
            },
            "Status": {
                "select": {
                    "name": {
                        "pending": "A Fazer",
                        "in_progress": "Em Andamento",
                        "completed": "Concluído",
                        "cancelled": "Cancelado"
                    }.get(task.status, "A Fazer")
                }
            },
            "Prioridade": {
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
            properties["Descrição"] = {
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
            properties["Prazo"] = {
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
        props = notion_page.get("properties", {})

        # Extract title
        title_prop = props.get("Nome", {}).get("title", [])
        title = title_prop[0]["text"]["content"] if title_prop else "Untitled"

        # Extract status
        status_prop = props.get("Status", {}).get("select", {})
        status_name = status_prop.get("name", "A Fazer")
        status = {
            "A Fazer": TaskStatus.PENDING,
            "Em Andamento": TaskStatus.IN_PROGRESS,
            "Concluído": TaskStatus.COMPLETED,
            "Cancelado": TaskStatus.CANCELLED
        }.get(status_name, TaskStatus.PENDING)

        # Extract priority
        priority_prop = props.get("Prioridade", {}).get("select", {})
        priority_name = priority_prop.get("name", "Média")
        priority = {
            "Baixa": TaskPriority.LOW,
            "Média": TaskPriority.MEDIUM,
            "Alta": TaskPriority.HIGH,
            "Urgente": TaskPriority.URGENT
        }.get(priority_name, TaskPriority.MEDIUM)

        # Extract description
        desc_prop = props.get("Descrição", {}).get("rich_text", [])
        description = desc_prop[0]["text"]["content"] if desc_prop else None

        # Extract due date
        date_prop = props.get("Prazo", {}).get("date")
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

    def create_task_in_notion(self, task: Task) -> Optional[str]:
        """
        Create a task in Notion.

        Args:
            task: Task object

        Returns:
            Notion page ID or None
        """
        try:
            properties = self._task_to_notion_properties(task)

            response = self.client.pages.create(
                parent={"database_id": self.database_id},
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
        if not user.notion_database_id:
            logger.warning(f"User {user.id} has no Notion database configured")
            return 0

        try:
            # Query Notion database
            response = self.client.databases.query(
                database_id=user.notion_database_id,
                filter={
                    "property": "Status",
                    "select": {
                        "does_not_equal": "Arquivado"
                    }
                }
            )

            synced_count = 0

            for page in response.get("results", []):
                notion_id = page["id"]
                task_data = self._notion_to_task_data(page)

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
                    notion_id = self.create_task_in_notion(task)
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

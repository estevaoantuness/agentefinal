"""LangChain tools for task management."""
from langchain.tools import Tool
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from src.database.models import Task, Category, Reminder, TaskStatus, TaskPriority
from src.utils.helpers import parse_datetime_natural, format_task_list
from src.utils.logger import logger


def create_task_tool(user_id: int, db: Session) -> Tool:
    """
    Create a tool for creating tasks.

    Args:
        user_id: User ID
        db: Database session

    Returns:
        LangChain Tool
    """
    def create_task(input_str: str) -> str:
        """
        Create a new task.
        Input should be in format: "title|description|priority|due_date"
        Example: "Revisar relatório|Revisar o relatório mensal|high|amanhã"
        """
        try:
            parts = input_str.split("|")
            title = parts[0].strip() if len(parts) > 0 else "Nova Tarefa"
            description = parts[1].strip() if len(parts) > 1 else None
            priority = parts[2].strip().lower() if len(parts) > 2 else "medium"
            due_date_str = parts[3].strip() if len(parts) > 3 else None

            # Parse due date
            due_date = None
            if due_date_str:
                due_date = parse_datetime_natural(due_date_str)

            # Validate priority
            if priority not in ["low", "medium", "high", "urgent"]:
                priority = "medium"

            # Create task
            task = Task(
                user_id=user_id,
                title=title,
                description=description,
                priority=priority,
                due_date=due_date,
                status=TaskStatus.PENDING
            )
            db.add(task)
            db.commit()
            db.refresh(task)

            logger.info(f"Task created: {task.id} - {task.title}")

            due_str = f" para {due_date.strftime('%d/%m/%Y')}" if due_date else ""
            return f"✅ Tarefa criada com sucesso: '{title}'{due_str}"

        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return f"❌ Erro ao criar tarefa: {str(e)}"

    return Tool(
        name="create_task",
        func=create_task,
        description="Cria uma nova tarefa. Use formato: title|description|priority|due_date"
    )


def list_tasks_tool(user_id: int, db: Session) -> Tool:
    """
    Create a tool for listing tasks.

    Args:
        user_id: User ID
        db: Database session

    Returns:
        LangChain Tool
    """
    def list_tasks(input_str: str) -> str:
        """
        List user tasks. Input can be: "all", "pending", "completed", "today"
        """
        try:
            filter_type = input_str.strip().lower() if input_str else "pending"

            query = db.query(Task).filter(Task.user_id == user_id)

            if filter_type == "pending":
                query = query.filter(Task.status == TaskStatus.PENDING)
            elif filter_type == "completed":
                query = query.filter(Task.status == TaskStatus.COMPLETED)
            elif filter_type == "today":
                today = datetime.now().date()
                query = query.filter(
                    Task.due_date >= today,
                    Task.due_date < today + datetime.timedelta(days=1)
                )

            tasks = query.order_by(Task.due_date.asc().nullslast()).all()

            return format_task_list(tasks)

        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            return f"❌ Erro ao listar tarefas: {str(e)}"

    return Tool(
        name="list_tasks",
        func=list_tasks,
        description="Lista tarefas do usuário. Input: 'all', 'pending', 'completed', ou 'today'"
    )


def update_task_tool(user_id: int, db: Session) -> Tool:
    """
    Create a tool for updating tasks.

    Args:
        user_id: User ID
        db: Database session

    Returns:
        LangChain Tool
    """
    def update_task(input_str: str) -> str:
        """
        Update a task. Input format: "task_id|field|value"
        Example: "1|status|completed" or "2|title|Novo título"
        """
        try:
            parts = input_str.split("|")
            if len(parts) < 3:
                return "❌ Formato inválido. Use: task_id|field|value"

            task_id = int(parts[0].strip())
            field = parts[1].strip().lower()
            value = parts[2].strip()

            # Get task
            task = db.query(Task).filter(
                Task.id == task_id,
                Task.user_id == user_id
            ).first()

            if not task:
                return f"❌ Tarefa #{task_id} não encontrada"

            # Update field
            if field == "status":
                if value.lower() in ["completed", "completa", "feita"]:
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = datetime.utcnow()
                elif value.lower() in ["pending", "pendente"]:
                    task.status = TaskStatus.PENDING
                elif value.lower() in ["in_progress", "em andamento"]:
                    task.status = TaskStatus.IN_PROGRESS
            elif field == "title":
                task.title = value
            elif field == "description":
                task.description = value
            elif field == "priority":
                if value.lower() in ["low", "medium", "high", "urgent"]:
                    task.priority = value.lower()
            elif field == "due_date":
                task.due_date = parse_datetime_natural(value)

            db.commit()
            logger.info(f"Task updated: {task_id}")

            return f"✅ Tarefa '{task.title}' atualizada com sucesso"

        except Exception as e:
            logger.error(f"Error updating task: {e}")
            return f"❌ Erro ao atualizar tarefa: {str(e)}"

    return Tool(
        name="update_task",
        func=update_task,
        description="Atualiza uma tarefa. Formato: task_id|field|value"
    )


def create_reminder_tool(user_id: int, db: Session) -> Tool:
    """
    Create a tool for creating reminders.

    Args:
        user_id: User ID
        db: Database session

    Returns:
        LangChain Tool
    """
    def create_reminder(input_str: str) -> str:
        """
        Create a reminder. Input format: "task_id|when|message"
        Example: "1|em 2 horas|Lembrete para revisar relatório"
        """
        try:
            parts = input_str.split("|")
            if len(parts) < 2:
                return "❌ Formato inválido. Use: task_id|when|message"

            task_id = int(parts[0].strip())
            when_str = parts[1].strip()
            message = parts[2].strip() if len(parts) > 2 else None

            # Get task
            task = db.query(Task).filter(
                Task.id == task_id,
                Task.user_id == user_id
            ).first()

            if not task:
                return f"❌ Tarefa #{task_id} não encontrada"

            # Parse time
            scheduled_time = parse_datetime_natural(when_str)
            if not scheduled_time:
                return f"❌ Não consegui entender o horário: {when_str}"

            # Create reminder
            reminder = Reminder(
                task_id=task_id,
                user_id=user_id,
                scheduled_time=scheduled_time,
                message=message or f"Lembrete: {task.title}"
            )
            db.add(reminder)
            db.commit()

            logger.info(f"Reminder created for task {task_id}")

            time_str = scheduled_time.strftime("%d/%m/%Y às %H:%M")
            return f"⏰ Lembrete criado para {time_str}"

        except Exception as e:
            logger.error(f"Error creating reminder: {e}")
            return f"❌ Erro ao criar lembrete: {str(e)}"

    return Tool(
        name="create_reminder",
        func=create_reminder,
        description="Cria um lembrete para uma tarefa. Formato: task_id|when|message"
    )


def get_tools(user_id: int, db: Session) -> list:
    """
    Get all available tools for the agent.

    Args:
        user_id: User ID
        db: Database session

    Returns:
        List of tools
    """
    return [
        create_task_tool(user_id, db),
        list_tasks_tool(user_id, db),
        update_task_tool(user_id, db),
        create_reminder_tool(user_id, db)
    ]

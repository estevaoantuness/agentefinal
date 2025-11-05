"""Execute functions called by OpenAI."""
import json
from typing import Dict, Any

from src.utils.logger import logger


class FunctionExecutor:
    """Execute functions called by OpenAI."""

    def execute(self, function_name: str, arguments: Dict[str, Any], user_id: str) -> str:
        """
        Execute function and return result.

        Args:
            function_name: Function name
            arguments: Function arguments
            user_id: User ID

        Returns:
            Function result as JSON string
        """
        logger.info(f"Executing function: {function_name} with args: {arguments}")

        try:
            if function_name == "view_tasks":
                return self._view_tasks(user_id, arguments)

            elif function_name == "create_task":
                return self._create_task(user_id, arguments)

            elif function_name == "mark_done":
                return self._mark_done(user_id, arguments)

            elif function_name == "mark_progress":
                return self._mark_progress(user_id, arguments)

            elif function_name == "view_progress":
                return self._view_progress(user_id)

            elif function_name == "get_help":
                return self._get_help()

            else:
                return json.dumps({
                    "success": False,
                    "error": f"Unknown function: {function_name}"
                })

        except Exception as e:
            logger.error(f"Error executing function {function_name}: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    def _view_tasks(self, user_id: str, arguments: Dict) -> str:
        """Execute view_tasks."""
        try:
            from src.database.session import SessionLocal
            from src.database.models import Task, TaskStatus

            db = SessionLocal()
            try:
                filter_status = arguments.get('filter_status', 'all')
                query = db.query(Task).filter(Task.user_id == int(user_id))

                if filter_status != 'all':
                    query = query.filter(Task.status == TaskStatus[filter_status.upper()])

                tasks = query.all()

                if not tasks:
                    return json.dumps({
                        "success": True,
                        "data": "You have no tasks yet. Create one with 'criar tarefa'!"
                    })

                task_list = []
                for i, task in enumerate(tasks, 1):
                    task_list.append(f"{i}. {task.title} ({task.status.value})")

                return json.dumps({
                    "success": True,
                    "data": "\n".join(task_list)
                })
            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error in view_tasks: {e}")
            return json.dumps({
                "success": False,
                "error": f"Error listing tasks: {str(e)}"
            })

    def _create_task(self, user_id: str, arguments: Dict) -> str:
        """Execute create_task."""
        try:
            from src.database.session import SessionLocal
            from src.database.models import Task, TaskStatus, TaskPriority
            from datetime import datetime

            title = arguments.get('title', '')
            description = arguments.get('description', '')
            priority = arguments.get('priority', 'medium')

            if not title:
                return json.dumps({
                    "success": False,
                    "error": "Task title is required"
                })

            db = SessionLocal()
            try:
                # Create new task
                task = Task(
                    user_id=int(user_id),
                    title=title,
                    description=description,
                    status=TaskStatus.PENDING,
                    priority=TaskPriority[priority.upper()] if priority else TaskPriority.MEDIUM
                )
                db.add(task)
                db.commit()

                return json.dumps({
                    "success": True,
                    "data": f"✅ Task '{title}' created successfully!"
                })
            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error in create_task: {e}")
            return json.dumps({
                "success": False,
                "error": f"Error creating task: {str(e)}"
            })

    def _mark_done(self, user_id: str, arguments: Dict) -> str:
        """Execute mark_done."""
        try:
            from src.database.session import SessionLocal
            from src.database.models import Task, TaskStatus

            task_numbers = arguments.get('task_numbers', [])

            if not task_numbers:
                return json.dumps({
                    "success": False,
                    "error": "No task numbers provided"
                })

            db = SessionLocal()
            try:
                # Get all tasks for user in order
                tasks = db.query(Task).filter(Task.user_id == int(user_id)).all()
                results = []

                for task_num in task_numbers:
                    if 0 < task_num <= len(tasks):
                        task = tasks[task_num - 1]
                        task.status = TaskStatus.COMPLETED
                        db.commit()
                        results.append(f"✅ Task '{task.title}' marked as completed")
                    else:
                        results.append(f"❌ Task {task_num} not found")

                return json.dumps({
                    "success": True,
                    "data": "\n".join(results)
                })
            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error in mark_done: {e}")
            return json.dumps({
                "success": False,
                "error": f"Error marking tasks done: {str(e)}"
            })

    def _mark_progress(self, user_id: str, arguments: Dict) -> str:
        """Execute mark_progress."""
        try:
            from src.database.session import SessionLocal
            from src.database.models import Task, TaskStatus

            task_numbers = arguments.get('task_numbers', [])

            if not task_numbers:
                return json.dumps({
                    "success": False,
                    "error": "No task numbers provided"
                })

            db = SessionLocal()
            try:
                # Get all tasks for user in order
                tasks = db.query(Task).filter(Task.user_id == int(user_id)).all()
                results = []

                for task_num in task_numbers:
                    if 0 < task_num <= len(tasks):
                        task = tasks[task_num - 1]
                        task.status = TaskStatus.IN_PROGRESS
                        db.commit()
                        results.append(f"⏳ Task '{task.title}' marked as in progress")
                    else:
                        results.append(f"❌ Task {task_num} not found")

                return json.dumps({
                    "success": True,
                    "data": "\n".join(results)
                })
            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error in mark_progress: {e}")
            return json.dumps({
                "success": False,
                "error": f"Error marking tasks in progress: {str(e)}"
            })

    def _view_progress(self, user_id: str) -> str:
        """Execute view_progress."""
        try:
            from src.database.session import SessionLocal
            from src.database.models import Task, TaskStatus

            db = SessionLocal()
            try:
                tasks = db.query(Task).filter(Task.user_id == int(user_id)).all()

                total = len(tasks)
                completed = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
                in_progress = len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS])
                pending = len([t for t in tasks if t.status == TaskStatus.PENDING])

                percentage = (completed / total * 100) if total > 0 else 0

                return json.dumps({
                    "success": True,
                    "data": {
                        "total": total,
                        "completed": completed,
                        "in_progress": in_progress,
                        "pending": pending,
                        "percentage": round(percentage, 1)
                    }
                })
            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error in view_progress: {e}")
            return json.dumps({
                "success": False,
                "error": f"Error getting progress: {str(e)}"
            })

    def _get_help(self) -> str:
        """Execute get_help."""
        help_text = """
Olá! 👋 Sou Pangeia, seu assistente de produtividade no WhatsApp.

Posso ajudar com:
📋 Ver tarefas - "minhas tarefas", "tarefas pendentes"
✨ Criar tarefa - "nova tarefa", "cria uma tarefa de..."
✅ Marcar como feito - "feito 1", "concluí a primeira"
⏳ Marcar em andamento - "comecei a 1", "em andamento 2"
📊 Ver progresso - "meu progresso", "como estou indo"

Exemplos:
- "minhas tarefas"
- "criar tarefa: reunião com cliente amanhã"
- "feito 1 2 3"
- "em andamento 4"
- "meu progresso"

Sempre disponível para ajudar! 🚀
"""
        return json.dumps({
            "success": True,
            "data": help_text
        })


# Global instance
function_executor = FunctionExecutor()

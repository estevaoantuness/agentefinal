"""Execute functions called by OpenAI."""
import json
from typing import Dict, Any

from src.utils.logger import logger
from src.integrations.notion_tasks import get_notion_task_reader


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

            elif function_name == "mark_onboarded":
                return self._mark_onboarded(user_id, arguments)

            elif function_name == "check_onboarding_status":
                return self._check_onboarding_status(user_id)

            elif function_name == "get_notion_tasks":
                return self._get_notion_tasks(user_id, arguments)

            elif function_name == "update_notion_task_status":
                return self._update_notion_task_status(user_id, arguments)

            elif function_name == "sync_notion":
                return self._sync_notion(user_id, arguments)

            elif function_name == "set_reminder":
                return self._set_reminder(user_id, arguments)

            elif function_name == "list_reminders":
                return self._list_reminders(user_id)

            elif function_name == "create_category":
                return self._create_category(user_id, arguments)

            elif function_name == "assign_category":
                return self._assign_category(user_id, arguments)

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

    def _mark_onboarded(self, user_id: str, arguments: Dict) -> str:
        """Mark user as completed onboarding in Notion."""
        try:
            from src.database.session import SessionLocal
            from src.database.models import User
            from src.integrations.notion_users import notion_user_manager

            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == int(user_id)).first()
                if not user:
                    return json.dumps({
                        "success": False,
                        "error": "User not found"
                    })

                # Mark onboarding complete in Notion
                success = notion_user_manager.mark_onboarding_complete(user.phone_number)

                if success:
                    return json.dumps({
                        "success": True,
                        "data": "✅ Onboarding completed and recorded in Notion!"
                    })
                else:
                    return json.dumps({
                        "success": False,
                        "error": "Could not record onboarding in Notion"
                    })
            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error in mark_onboarded: {e}")
            return json.dumps({
                "success": False,
                "error": f"Error marking onboarding: {str(e)}"
            })

    def _check_onboarding_status(self, user_id: str) -> str:
        """Check if user has completed onboarding in Notion."""
        try:
            from src.database.session import SessionLocal
            from src.database.models import User
            from src.integrations.notion_users import notion_user_manager

            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == int(user_id)).first()
                if not user:
                    return json.dumps({
                        "success": False,
                        "error": "User not found"
                    })

                # Check onboarding status in Notion
                is_onboarded = notion_user_manager.get_onboarding_status(user.phone_number)

                if is_onboarded:
                    return json.dumps({
                        "success": True,
                        "data": "✅ You have already completed onboarding!"
                    })
                else:
                    return json.dumps({
                        "success": True,
                        "data": "⏳ You haven't completed onboarding yet. Let's start!"
                    })
            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error in check_onboarding_status: {e}")
            return json.dumps({
                "success": False,
                "error": f"Error checking onboarding status: {str(e)}"
            })

    def _get_notion_tasks(self, user_id: str, arguments: Dict) -> str:
        """Get tasks from Notion database for Groq to read and analyze."""
        try:
            # Get format and filters from arguments
            format_type = arguments.get('format', 'formatted')
            status_filter = arguments.get('status_filter', 'all')

            task_reader = get_notion_task_reader()

            # Get tasks based on filter
            if status_filter != 'all':
                # Map filter names to Notion status format
                status_map = {
                    'not_started': 'Not Started',
                    'in_progress': 'In Progress',
                    'completed': 'Completed',
                    'on_hold': 'On Hold',
                    'blocked': 'Blocked'
                }
                status_name = status_map.get(status_filter, 'Not Started')
                tasks = task_reader.get_tasks_by_status(status_name)
            else:
                tasks = task_reader.get_all_tasks()

            # Format response based on requested format
            if format_type == 'summary':
                # Return JSON summary for analysis, but ensure consistency with current tasks
                formatted_data = task_reader.format_summary_for_groq(tasks)

                def _build_summary(task_list):
                    summary = {
                        "total_tasks": len(task_list),
                        "by_status": {},
                        "by_priority": {},
                        "average_progress": 0,
                        "tasks": []
                    }
                    total_progress = 0

                    for task in task_list:
                        status = task.get('status', 'Unknown')
                        summary["by_status"][status] = summary["by_status"].get(status, 0) + 1

                        priority = task.get('priority', 'Unknown')
                        summary["by_priority"][priority] = summary["by_priority"].get(priority, 0) + 1

                        progress = task.get('progress', 0) or 0
                        total_progress += progress

                        summary["tasks"].append({
                            "id": task.get('id'),
                            "title": task.get('title'),
                            "status": status,
                            "priority": priority,
                            "progress": progress
                        })

                    if task_list:
                        summary["average_progress"] = round(total_progress / len(task_list), 2)

                    return summary

                expected_summary = _build_summary(tasks)

                try:
                    summary_payload = (
                        json.loads(formatted_data)
                        if isinstance(formatted_data, str)
                        else formatted_data
                    )
                except (TypeError, ValueError):
                    summary_payload = None

                if not isinstance(summary_payload, dict):
                    formatted_data = json.dumps(expected_summary, ensure_ascii=False, indent=2)
                else:
                    # Overwrite/merge ensuring current tasks and metadata are accurate
                    summary_payload['total_tasks'] = expected_summary['total_tasks']
                    summary_payload['by_status'] = expected_summary['by_status']
                    summary_payload['by_priority'] = expected_summary['by_priority']
                    summary_payload['average_progress'] = expected_summary['average_progress']

                    existing_tasks = summary_payload.get('tasks') or []
                    if len(existing_tasks) != len(expected_summary['tasks']):
                        summary_payload['tasks'] = expected_summary['tasks']
                    else:
                        for idx, task_entry in enumerate(existing_tasks):
                            expected_entry = expected_summary['tasks'][idx]
                            for key, value in expected_entry.items():
                                if key not in task_entry or task_entry[key] in (None, ''):
                                    task_entry[key] = value

                    formatted_data = json.dumps(summary_payload, ensure_ascii=False, indent=2)
            elif format_type == 'by_status':
                # Group tasks by status
                by_status = {}
                for task in tasks:
                    status = task.get('status', 'Unknown')
                    if status not in by_status:
                        by_status[status] = []
                    by_status[status].append(task)
                formatted_data = json.dumps(by_status, ensure_ascii=False, indent=2)
            else:
                # Default: formatted readable list
                formatted_data = task_reader.format_for_groq(tasks)

            logger.info(f"Retrieved {len(tasks)} tasks from Notion")
            return json.dumps({
                "success": True,
                "data": formatted_data,
                "count": len(tasks)
            })

        except Exception as e:
            logger.error(f"Error in get_notion_tasks: {e}")
            return json.dumps({
                "success": False,
                "error": f"Error retrieving tasks from Notion: {str(e)}"
            })

    def _update_notion_task_status(self, user_id: str, arguments: Dict) -> str:
        """Update task status in Notion database."""
        try:
            # Get required arguments
            task_id = arguments.get('task_id')
            new_status = arguments.get('new_status')
            update_progress = arguments.get('update_progress')

            if not task_id or not new_status:
                return json.dumps({
                    "success": False,
                    "error": "task_id and new_status are required parameters"
                })

            task_reader = get_notion_task_reader()

            # Update status
            status_success = task_reader.update_task_status(task_id, new_status)

            if not status_success:
                return json.dumps({
                    "success": False,
                    "error": f"Could not update task status to '{new_status}'"
                })

            # Update progress if provided
            if update_progress is not None:
                progress_success = task_reader.update_task_progress(task_id, update_progress)
                progress_msg = f" and progress to {update_progress}%" if progress_success else ""
            else:
                progress_msg = ""

            logger.info(f"Updated task {task_id} status to '{new_status}'{progress_msg}")
            return json.dumps({
                "success": True,
                "data": f"✅ Task status updated to '{new_status}'{progress_msg}!"
            })

        except Exception as e:
            logger.error(f"Error in update_notion_task_status: {e}")
            return json.dumps({
                "success": False,
                "error": f"Error updating task status: {str(e)}"
            })


    def _sync_notion(self, user_id: str, arguments: Dict) -> str:
        """Synchronize tasks with Notion database."""
        try:
            from src.integrations.notion_sync import sync_all_tasks

            direction = arguments.get('direction', 'both')

            # Execute sync
            if direction in ['both', 'to_notion']:
                sync_all_tasks()

            logger.info(f"Notion sync completed for direction: {direction}")
            return json.dumps({
                "success": True,
                "data": f"✅ Notion sync completed ({direction} direction)!"
            })
        except Exception as e:
            logger.error(f"Error in sync_notion: {e}")
            return json.dumps({
                "success": False,
                "error": f"Error syncing with Notion: {str(e)}"
            })

    def _set_reminder(self, user_id: str, arguments: Dict) -> str:
        """Set a reminder for a task based on user request.

        This function handles USER-INITIATED reminders (e.g., "remind me in 5 minutes").

        NOTE: Proactive bot-generated reminders (bot deciding to remind user without being asked)
        are NOT allowed and require explicit authorization. Those must go through a separate
        mechanism that is controlled by the user.
        """
        try:
            task_number = arguments.get('task_number')
            reminder_datetime = arguments.get('reminder_datetime')

            if not task_number or not reminder_datetime:
                return json.dumps({
                    "success": False,
                    "error": "task_number and reminder_datetime are required"
                })

            # For MVP: store reminder in database
            from src.database.session import SessionLocal
            from src.database.models import Task, Reminder
            from datetime import datetime

            db = SessionLocal()
            try:
                tasks = db.query(Task).filter(Task.user_id == int(user_id)).all()

                if task_number > len(tasks):
                    return json.dumps({
                        "success": False,
                        "error": f"Task {task_number} not found"
                    })

                task = tasks[task_number - 1]

                # Create reminder
                reminder = Reminder(
                    task_id=task.id,
                    reminder_time=reminder_datetime,
                    is_sent=False
                )
                db.add(reminder)
                db.commit()

                return json.dumps({
                    "success": True,
                    "data": f"✅ Reminder set for '{task.title}' at {reminder_datetime}!"
                })
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in set_reminder: {e}")
            return json.dumps({
                "success": False,
                "error": f"Error setting reminder: {str(e)}"
            })

    def _list_reminders(self, user_id: str) -> str:
        """List all reminders for the user."""
        try:
            from src.database.session import SessionLocal
            from src.database.models import Task, Reminder

            db = SessionLocal()
            try:
                # Get all tasks for user
                tasks = db.query(Task).filter(Task.user_id == int(user_id)).all()
                task_ids = [t.id for t in tasks]

                # Get active reminders
                if not task_ids:
                    return json.dumps({
                        "success": True,
                        "data": "No reminders set."
                    })

                reminders = db.query(Reminder).filter(
                    Reminder.task_id.in_(task_ids),
                    Reminder.is_sent == False
                ).all()

                if not reminders:
                    return json.dumps({
                        "success": True,
                        "data": "No active reminders."
                    })

                reminder_list = []
                for reminder in reminders:
                    task = db.query(Task).filter(Task.id == reminder.task_id).first()
                    reminder_list.append(f"• {task.title} @ {reminder.reminder_time}")

                return json.dumps({
                    "success": True,
                    "data": "\n".join(reminder_list) if reminder_list else "No reminders."
                })
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in list_reminders: {e}")
            return json.dumps({
                "success": False,
                "error": f"Error listing reminders: {str(e)}"
            })

    def _create_category(self, user_id: str, arguments: Dict) -> str:
        """Create a new task category."""
        try:
            name = arguments.get('name')
            emoji = arguments.get('emoji', '')
            color = arguments.get('color', '')

            if not name:
                return json.dumps({
                    "success": False,
                    "error": "Category name is required"
                })

            from src.database.session import SessionLocal
            from src.database.models import Category

            db = SessionLocal()
            try:
                # Check if category already exists
                existing = db.query(Category).filter(
                    Category.user_id == int(user_id),
                    Category.name == name
                ).first()

                if existing:
                    return json.dumps({
                        "success": False,
                        "error": f"Category '{name}' already exists"
                    })

                # Create category
                category = Category(
                    user_id=int(user_id),
                    name=name,
                    emoji=emoji,
                    color=color
                )
                db.add(category)
                db.commit()

                return json.dumps({
                    "success": True,
                    "data": f"✅ Category '{name}' {emoji} created!"
                })
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in create_category: {e}")
            return json.dumps({
                "success": False,
                "error": f"Error creating category: {str(e)}"
            })

    def _assign_category(self, user_id: str, arguments: Dict) -> str:
        """Assign a category to a task."""
        try:
            task_number = arguments.get('task_number')
            category_name = arguments.get('category_name')

            if not task_number or not category_name:
                return json.dumps({
                    "success": False,
                    "error": "task_number and category_name are required"
                })

            from src.database.session import SessionLocal
            from src.database.models import Task, Category

            db = SessionLocal()
            try:
                # Get task
                tasks = db.query(Task).filter(Task.user_id == int(user_id)).all()

                if task_number > len(tasks):
                    return json.dumps({
                        "success": False,
                        "error": f"Task {task_number} not found"
                    })

                task = tasks[task_number - 1]

                # Get category
                category = db.query(Category).filter(
                    Category.user_id == int(user_id),
                    Category.name == category_name
                ).first()

                if not category:
                    return json.dumps({
                        "success": False,
                        "error": f"Category '{category_name}' not found"
                    })

                # Assign category
                task.category_id = category.id
                db.commit()

                return json.dumps({
                    "success": True,
                    "data": f"✅ Task '{task.title}' assigned to '{category_name}' {category.emoji}!"
                })
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in assign_category: {e}")
            return json.dumps({
                "success": False,
                "error": f"Error assigning category: {str(e)}"
            })


# Global instance
function_executor = FunctionExecutor()

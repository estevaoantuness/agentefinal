"""Function definitions for OpenAI Function Calling."""

FUNCTION_DEFINITIONS = [
    {
        "name": "view_tasks",
        "description": "Show all user tasks organized by status (Pending, In Progress, Completed)",
        "parameters": {
            "type": "object",
            "properties": {
                "filter_status": {
                    "type": "string",
                    "enum": ["all", "pending", "in_progress", "completed", "today"],
                    "description": "Filter by specific status or show all tasks"
                }
            },
            "required": ["filter_status"]
        }
    },
    {
        "name": "create_task",
        "description": "Create a new task after collecting all necessary information",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Task title (e.g., 'Review report')"
                },
                "description": {
                    "type": "string",
                    "description": "Detailed task description"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "urgent"],
                    "description": "Task priority level"
                },
                "due_date": {
                    "type": "string",
                    "description": "Due date in natural language (e.g., 'tomorrow', 'next Friday')"
                }
            },
            "required": ["title"]
        }
    },
    {
        "name": "mark_done",
        "description": "Mark one or more tasks as completed (status = Completed)",
        "parameters": {
            "type": "object",
            "properties": {
                "task_numbers": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of task numbers to mark as done (e.g., [1, 2, 3])"
                }
            },
            "required": ["task_numbers"]
        }
    },
    {
        "name": "mark_progress",
        "description": "Mark one or more tasks as in progress (status = In Progress)",
        "parameters": {
            "type": "object",
            "properties": {
                "task_numbers": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of task numbers to mark as in progress"
                }
            },
            "required": ["task_numbers"]
        }
    },
    {
        "name": "view_progress",
        "description": "Show progress report with metrics and task statistics",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_help",
        "description": "Show help about how to use the assistant and available commands",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
]


def get_function_definitions():
    """Get list of function definitions."""
    return FUNCTION_DEFINITIONS

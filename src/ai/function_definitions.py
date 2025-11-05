"""Function definitions for Groq Function Calling (compatible format)."""

FUNCTION_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "view_tasks",
            "description": "Show all user tasks organized by status (Pending, In Progress, Completed)",
            "parameters": {
                "type": "object",
                "properties": {
                    "filter_status": {
                        "type": "string",
                        "enum": ["all", "pending", "in_progress", "completed"],
                        "description": "Filter by specific status (default: all)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task with title and optional description and priority",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Task title (required)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed task description (optional)"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                        "description": "Task priority level (default: medium)"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mark_done",
            "description": "Mark one or more tasks as completed",
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
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mark_progress",
            "description": "Mark one or more tasks as in progress",
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
        }
    },
    {
        "type": "function",
        "function": {
            "name": "view_progress",
            "description": "Show progress report with metrics and task statistics",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_help",
            "description": "Show help about how to use the assistant and available commands",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mark_onboarded",
            "description": "Mark the user as completed onboarding and record it in Notion database",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_onboarding_status",
            "description": "Check if the user has completed onboarding in the Notion database",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]


def get_function_definitions():
    """Get list of function definitions."""
    return FUNCTION_DEFINITIONS

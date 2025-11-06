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
    },
    {
        "type": "function",
        "function": {
            "name": "get_notion_tasks",
            "description": "Retrieve all tasks from Notion database for Groq to read, analyze, and manage. Returns formatted task list with titles, status, priority, progress, and due dates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "enum": ["formatted", "summary", "by_status"],
                        "description": "How to format the task list: 'formatted' for readable list, 'summary' for JSON analysis, 'by_status' for status-grouped tasks (default: formatted)"
                    },
                    "status_filter": {
                        "type": "string",
                        "enum": ["all", "not_started", "in_progress", "completed", "on_hold", "blocked"],
                        "description": "Filter tasks by status (default: all)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_notion_task_status",
            "description": "Update the status of a task in Notion database. Use this to mark tasks as started, in progress, completed, on hold, or blocked based on workflow changes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The Notion page ID of the task (from task_id field in task list)"
                    },
                    "new_status": {
                        "type": "string",
                        "enum": ["Not Started", "In Progress", "Completed", "On Hold", "Blocked"],
                        "description": "The new status for the task"
                    },
                    "update_progress": {
                        "type": "number",
                        "description": "Optional: update progress percentage (0-100) when changing status"
                    }
                },
                "required": ["task_id", "new_status"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sync_notion",
            "description": "Synchronize all tasks with Notion database bidirectionally - sync local tasks to Notion and pull updates from Notion",
            "parameters": {
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "enum": ["both", "to_notion", "from_notion"],
                        "description": "Direction of sync: 'both' for bidirectional, 'to_notion' to push local to Notion, 'from_notion' to pull from Notion (default: both)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_reminder",
            "description": "Set a reminder/notification for a task at a specific date and time. Reminder will be sent via WhatsApp at the scheduled time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_number": {
                        "type": "integer",
                        "description": "The task number to set reminder for"
                    },
                    "reminder_datetime": {
                        "type": "string",
                        "description": "When to send reminder in ISO format (e.g., '2024-11-06T14:30:00') or natural language (e.g., 'tomorrow at 9am', 'in 2 hours')"
                    }
                },
                "required": ["task_number", "reminder_datetime"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_reminders",
            "description": "List all active reminders for the user",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_category",
            "description": "Create a new task category to organize tasks",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Category name (e.g., 'Work', 'Personal', 'Shopping')"
                    },
                    "emoji": {
                        "type": "string",
                        "description": "Emoji to represent the category (optional, e.g., '💼' for Work)"
                    },
                    "color": {
                        "type": "string",
                        "description": "Color code (optional, e.g., 'red', 'blue', 'green')"
                    }
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "assign_category",
            "description": "Assign a category to a task for better organization",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_number": {
                        "type": "integer",
                        "description": "The task number to assign category to"
                    },
                    "category_name": {
                        "type": "string",
                        "description": "The category name to assign"
                    }
                },
                "required": ["task_number", "category_name"]
            }
        }
    }
]


def get_function_definitions():
    """Get list of function definitions."""
    return FUNCTION_DEFINITIONS

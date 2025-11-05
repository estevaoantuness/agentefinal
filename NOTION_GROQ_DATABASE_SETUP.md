# 🤖 Notion Database Setup for Groq Task Management

## Quick Setup (3-5 minutes)

### Step 1: Create Database in Notion

1. Go to your Notion workspace
2. Click **+ Add a page**
3. Select **Database → Table**
4. Name it: **"Groq Managed Tasks"**

### Step 2: Configure Properties

Add the following columns to your database:

| Property | Type | Description | Options |
|----------|------|-------------|---------|
| **Task Name** | Title | Task name/title | (auto-created) |
| **Status** | Select | Task status | `Not Started`, `In Progress`, `Completed`, `On Hold`, `Blocked` |
| **Priority** | Select | Priority level | `Low`, `Medium`, `High`, `Urgent` |
| **Due Date** | Date | When task is due | - |
| **Description** | Text | Detailed description | - |
| **Category** | Select | Task category | `Development`, `Design`, `Marketing`, `Operations`, `Support`, `Research`, `Other` |
| **Effort Hours** | Number | Estimated hours | - |
| **Progress** | Number | Completion % | Format as percentage |
| **Tags** | Multi-select | Task tags | `Urgent`, `Blocked`, `Review`, `Documentation`, `Testing` |
| **Notes** | Text | Additional notes | - |

### Step 3: Get Database ID

1. Open your "Groq Managed Tasks" database
2. Copy the URL: `https://notion.so/[DATABASE_ID]?v=...`
3. Extract the database ID (the long code between `/` and `?`)

Example URL: `https://notion.so/abc123def456...?v=abc`
Database ID: `abc123def456...`

### Step 4: Configure Environment Variable

1. Go to https://dashboard.render.com
2. Select your service: **pangeia-bot-final**
3. Go to **Settings → Environment**
4. Add new variable:
   ```
   NOTION_GROQ_TASKS_DB_ID=abc123def456...
   ```
5. Click **Save** (service will restart)

## Database Features for Groq

✅ **Status Tracking** - Five-state workflow (Not Started → In Progress → Completed)
✅ **Priority System** - Helps Groq prioritize tasks
✅ **Progress Tracking** - % completion for monitoring
✅ **Effort Estimation** - Hours needed for task planning
✅ **Categories** - Organize tasks by type
✅ **Due Dates** - Track deadlines
✅ **Tags** - Flexible labeling system
✅ **Descriptions** - Rich context for AI understanding
✅ **Timestamps** - Auto-tracked creation/modification dates

## Example Tasks

Add these sample tasks to test:

### Task 1: Setup Groq Integration
- **Status**: In Progress
- **Priority**: High
- **Effort Hours**: 4
- **Progress**: 75%
- **Due Date**: 2025-11-15
- **Category**: Development
- **Description**: Configure Groq API with Notion database connection

### Task 2: Create Database Schema
- **Status**: Completed
- **Priority**: High
- **Effort Hours**: 3
- **Progress**: 100%
- **Due Date**: 2025-11-10
- **Category**: Development
- **Description**: Design optimal database structure for Groq AI reading

### Task 3: Write Integration Tests
- **Status**: Not Started
- **Priority**: Medium
- **Effort Hours**: 5
- **Progress**: 0%
- **Due Date**: 2025-11-20
- **Category**: Testing
- **Description**: Test Groq-Notion integration with various task types

## How Groq Will Use This Database

1. **Query Tasks**: Groq reads all tasks from Notion database
2. **Understand Context**: Analyzes status, priority, due dates, descriptions
3. **Make Decisions**: Updates task status based on conversations
4. **Track Progress**: Monitors completion percentages
5. **Manage Priorities**: Suggests high-priority tasks to focus on

## API Integration

Once configured, add this code to `src/ai/function_executor.py`:

```python
from notion_client import Client
from src.config.settings import settings

class NotionTaskReader:
    def __init__(self):
        self.client = Client(auth=settings.NOTION_API_KEY)
        self.db_id = os.getenv('NOTION_GROQ_TASKS_DB_ID')

    def get_all_tasks(self):
        """Get all tasks from Notion for Groq to analyze."""
        if not self.db_id:
            return []

        response = self.client.databases.query(database_id=self.db_id)
        return response['results']

    def update_task_status(self, task_id, new_status):
        """Update task status based on Groq's decision."""
        self.client.pages.update(
            page_id=task_id,
            properties={
                "Status": {
                    "select": {"name": new_status}
                }
            }
        )
```

## Troubleshooting

### Database Not Found
- ✓ Verify database ID is correct (no extra characters)
- ✓ Check Notion integration has database access
- ✓ Confirm environment variable is set in Render

### Groq Can't Read Tasks
- ✓ Ensure all required properties exist
- ✓ Add at least 1-2 sample tasks
- ✓ Check Groq has `NOTION_API_KEY` configured

### Tasks Not Updating
- ✓ Verify write permissions in Notion integration
- ✓ Check that `NOTION_GROQ_TASKS_DB_ID` is correctly set
- ✓ Look for errors in Render logs

## Next Steps

1. ✅ Create database in Notion
2. ✅ Configure properties as described
3. ✅ Get database ID
4. ✅ Add to Render environment
5. ✅ Test by sending message to bot
6. ✅ Groq will start managing tasks!

---

**Status**: Ready to use
**Created**: 2025-11-05
**Last Updated**: 2025-11-05

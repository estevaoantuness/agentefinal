#!/usr/bin/env python3
"""
Create a structured Notion database for Groq task management.
Uses existing User Profiles database as parent.
"""
import os
import json
from notion_client import Client
from datetime import datetime

# Initialize Notion client
NOTION_API_KEY = os.getenv('NOTION_API_KEY', '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')
USERS_DB_ID = os.getenv('NOTION_USERS_DATABASE_ID', '29ea53b3e53c805c88dde0e2ab9e58b9')

client = Client(auth=NOTION_API_KEY)

def create_groq_tasks_database():
    """Create a Tasks database optimized for Groq within the existing workspace."""

    try:
        print("📋 Creating Groq Tasks Database...")
        print(f"Parent Database: {USERS_DB_ID}")

        # Create a new database within the workspace
        database = client.databases.create(
            parent={
                "type": "database_id",
                "database_id": USERS_DB_ID
            },
            title="Groq Managed Tasks",
            description="Task database synchronized with WhatsApp bot and Groq AI. Optimized for AI-driven task management.",
            properties={
                "Task Name": {
                    "id": "title",
                    "type": "title",
                    "title": {}
                },
                "Status": {
                    "type": "status",
                    "status": {
                        "options": [
                            {"name": "Not Started", "color": "default"},
                            {"name": "In Progress", "color": "blue"},
                            {"name": "Completed", "color": "green"},
                            {"name": "On Hold", "color": "gray"},
                            {"name": "Blocked", "color": "red"}
                        ]
                    }
                },
                "Priority": {
                    "type": "select",
                    "select": {
                        "options": [
                            {"name": "Low", "color": "gray"},
                            {"name": "Medium", "color": "yellow"},
                            {"name": "High", "color": "orange"},
                            {"name": "Urgent", "color": "red"}
                        ]
                    }
                },
                "Assigned User": {
                    "type": "people",
                    "people": {}
                },
                "Due Date": {
                    "type": "date",
                    "date": {}
                },
                "Description": {
                    "type": "rich_text",
                    "rich_text": {}
                },
                "Category": {
                    "type": "select",
                    "select": {
                        "options": [
                            {"name": "Development", "color": "blue"},
                            {"name": "Design", "color": "purple"},
                            {"name": "Marketing", "color": "pink"},
                            {"name": "Operations", "color": "green"},
                            {"name": "Support", "color": "yellow"},
                            {"name": "Research", "color": "orange"},
                            {"name": "Other", "color": "gray"}
                        ]
                    }
                },
                "Effort Hours": {
                    "type": "number",
                    "number": {
                        "format": "number"
                    }
                },
                "Progress": {
                    "type": "number",
                    "number": {
                        "format": "percent"
                    }
                },
                "Tags": {
                    "type": "multi_select",
                    "multi_select": {
                        "options": [
                            {"name": "Urgent", "color": "red"},
                            {"name": "Blocked", "color": "orange"},
                            {"name": "Review", "color": "blue"},
                            {"name": "Documentation", "color": "green"},
                            {"name": "Testing", "color": "purple"}
                        ]
                    }
                },
                "Notes": {
                    "type": "rich_text",
                    "rich_text": {}
                },
                "Created": {
                    "type": "created_time",
                    "created_time": {}
                },
                "Updated": {
                    "type": "last_edited_time",
                    "last_edited_time": {}
                }
            }
        )

        db_id = database["id"]
        print(f"✅ Database created successfully!")
        print(f"Database ID: {db_id}")

        return db_id

    except Exception as e:
        print(f"❌ Error creating database: {e}")
        print("\n📌 ALTERNATIVE: Manual Database Creation")
        print("If the API approach fails, you can manually:")
        print("1. Go to your Notion workspace")
        print("2. Create a new Database called 'Groq Managed Tasks'")
        print("3. Add the following properties:")
        print("   - Task Name (Title)")
        print("   - Status (Select: Not Started, In Progress, Completed, On Hold, Blocked)")
        print("   - Priority (Select: Low, Medium, High, Urgent)")
        print("   - Due Date (Date)")
        print("   - Description (Text)")
        print("   - Category (Select: Development, Design, Marketing, Operations, Support, Research, Other)")
        print("   - Effort Hours (Number)")
        print("   - Progress (Number %)")
        print("   - Tags (Multi-select)")
        return None


def add_sample_tasks(database_id):
    """Add example tasks to demonstrate structure."""

    if not database_id:
        print("⚠️  Skipping sample tasks - no database ID")
        return

    samples = [
        {
            "title": "Setup Groq API Integration",
            "status": "In Progress",
            "priority": "High",
            "description": "Configure Groq API with Notion database connection",
            "category": "Development",
            "effort": 4,
            "progress": 0.75,
            "due": "2025-11-15"
        },
        {
            "title": "Create Notion Database Schema",
            "status": "Completed",
            "priority": "High",
            "description": "Design optimal database structure for Groq AI reading",
            "category": "Development",
            "effort": 3,
            "progress": 1.0,
            "due": "2025-11-10"
        },
        {
            "title": "Write Integration Tests",
            "status": "Not Started",
            "priority": "Medium",
            "description": "Test Groq-Notion integration with various task types",
            "category": "Testing",
            "effort": 5,
            "progress": 0.0,
            "due": "2025-11-20"
        }
    ]

    for task in samples:
        try:
            client.pages.create(
                parent={"database_id": database_id},
                properties={
                    "Task Name": {
                        "title": [{"text": {"content": task["title"]}}]
                    },
                    "Status": {
                        "status": {"name": task["status"]}
                    },
                    "Priority": {
                        "select": {"name": task["priority"]}
                    },
                    "Description": {
                        "rich_text": [{"text": {"content": task["description"]}}]
                    },
                    "Category": {
                        "select": {"name": task["category"]}
                    },
                    "Effort Hours": {
                        "number": task["effort"]
                    },
                    "Progress": {
                        "number": task["progress"]
                    },
                    "Due Date": {
                        "date": {"start": task["due"]}
                    }
                }
            )
            print(f"  ✅ Added: {task['title']}")
        except Exception as e:
            print(f"  ⚠️  Could not add {task['title']}: {e}")


def main():
    """Main execution."""
    print("=" * 70)
    print("🚀 CREATING GROQ-OPTIMIZED NOTION DATABASE")
    print("=" * 70)
    print()

    # Create database
    database_id = create_groq_tasks_database()

    if database_id:
        print()
        print("=" * 70)
        print("📝 ADDING SAMPLE TASKS")
        print("=" * 70)
        print()
        add_sample_tasks(database_id)

        print()
        print("=" * 70)
        print("✨ SUMMARY")
        print("=" * 70)
        print(f"Database ID: {database_id}")
        print()
        print("📖 DATABASE FEATURES FOR GROQ:")
        print("  ✓ Status tracking (Not Started, In Progress, Completed, etc.)")
        print("  ✓ Priority levels (Low, Medium, High, Urgent)")
        print("  ✓ Progress percentage for completion tracking")
        print("  ✓ Effort estimation in hours")
        print("  ✓ Category system for organization")
        print("  ✓ Due dates for deadline tracking")
        print("  ✓ Tags for flexible organization")
        print("  ✓ Rich descriptions for context")
        print("  ✓ Timestamps (created/updated)")
        print()
        print("🔗 NEXT STEPS:")
        print("  1. Copy Database ID above")
        print("  2. Add to Render environment: NOTION_GROQ_TASKS_DB_ID=<database_id>")
        print("  3. Update function_executor.py to query this database")
        print("  4. Groq can now manage tasks directly in Notion!")
        print()
        print("=" * 70)

        # Save for reference
        with open("/tmp/notion_groq_db_id.txt", "w") as f:
            f.write(database_id)
        print(f"\n✅ Database ID saved to: /tmp/notion_groq_db_id.txt")

    else:
        print("\n⚠️  Manual setup required - see instructions above")


if __name__ == "__main__":
    main()

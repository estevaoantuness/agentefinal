#!/usr/bin/env python3
"""
List ALL accessible Notion databases - find IDs without needing to pass them
"""
import json
import os
from notion_client import Client

NOTION_API_KEY = os.getenv("NOTION_API_KEY")

if not NOTION_API_KEY:
    print("❌ ERROR: Set NOTION_API_KEY")
    print("\nUsage:")
    print("  export NOTION_API_KEY='your_key'")
    print("  python scripts/list_all_notion_databases.py")
    exit(1)

client = Client(auth=NOTION_API_KEY)

try:
    print("\n" + "="*70)
    print("🔍 SEARCHING FOR ALL ACCESSIBLE NOTION DATABASES")
    print("="*70)

    # Search for all databases
    response = client.search(
        query="",
        filter={"value": "database", "property": "object"}
    )

    databases = response.get("results", [])

    if not databases:
        print("\n❌ No databases found!")
        print("Make sure your Notion integration has access to your databases.")
        exit(1)

    print(f"\n✅ Found {len(databases)} database(s):\n")

    env_vars = {}

    for i, db in enumerate(databases, 1):
        db_id = db["id"]
        # Remove hyphens from ID for cleaner display
        db_id_clean = db_id.replace("-", "")

        # Try to get title
        title = "Unknown"
        if db.get("title"):
            title = db["title"][0].get("plain_text", "Unknown") if db["title"] else "Unknown"

        print(f"{i}. Database: {title}")
        print(f"   ID (with hyphens):    {db_id}")
        print(f"   ID (without hyphens): {db_id_clean}")
        print()

        env_vars[title] = {
            "with_hyphens": db_id,
            "without_hyphens": db_id_clean
        }

    print("="*70)
    print("📝 CONFIGURATION GUIDE")
    print("="*70)
    print("""
Based on the databases found, update your .env file:

NOTION_DATABASE_ID=<main tasks database ID>
NOTION_GROQ_TASKS_DB_ID=<groq tasks database ID>
NOTION_USERS_DATABASE_ID=<user profiles database ID>

The IDs can be used with or without hyphens.
""")

    print("\n📋 ENVIRONMENT VARIABLES FORMAT:")
    print("-" * 70)

    for i, (title, ids) in enumerate(env_vars.items(), 1):
        print(f"\n{i}. {title}")
        print(f"   NOTION_..._DB_ID={ids['without_hyphens']}")

    print("\n" + "="*70)

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nMake sure:")
    print("  1. NOTION_API_KEY is valid")
    print("  2. Your Notion integration has access to the databases")
    print("  3. The databases are shared with the integration")

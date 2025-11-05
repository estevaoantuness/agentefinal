#!/usr/bin/env python3
"""
Discover Notion database structure - prints all properties/columns
"""
import json
import os
from notion_client import Client

# Get from environment
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
# You'll need to pass this as argument or env var
USERS_DB_ID = os.getenv("NOTION_USERS_DATABASE_ID")

if not NOTION_API_KEY or not USERS_DB_ID:
    print("❌ ERROR: Set NOTION_API_KEY and NOTION_USERS_DATABASE_ID")
    print("\nUsage:")
    print("  export NOTION_API_KEY='your_key'")
    print("  export NOTION_USERS_DATABASE_ID='your_db_id'")
    print("  python scripts/discover_notion_structure.py")
    exit(1)

client = Client(auth=NOTION_API_KEY)

try:
    # Get database structure
    db = client.databases.retrieve(USERS_DB_ID)

    print("\n" + "="*60)
    print("📊 NOTION DATABASE STRUCTURE")
    print("="*60)
    print(f"\nDatabase ID: {db['id']}")
    print(f"Database Title: {db.get('title', [{}])[0].get('plain_text', 'N/A')}")

    print("\n📋 PROPERTIES (Columns):")
    print("-" * 60)

    properties = db.get("properties", {})

    for prop_name, prop_config in properties.items():
        prop_type = prop_config.get("type")
        print(f"\n✓ Property Name: '{prop_name}'")
        print(f"  Type: {prop_type}")

        # Show additional details based on type
        if prop_type == "select":
            options = prop_config.get("select", {}).get("options", [])
            print(f"  Options: {[opt['name'] for opt in options]}")
        elif prop_type == "multi_select":
            options = prop_config.get("multi_select", {}).get("options", [])
            print(f"  Options: {[opt['name'] for opt in options]}")

    print("\n" + "="*60)
    print("📝 EXAMPLE: Use these property names in your code:")
    print("="*60)
    print("""
Example for notion_users.py:

    # Get user by phone number
    response = self.client.databases.query(
        database_id=self.users_db_id,
        filter={
            "property": "Phone",  # Use actual property name from above
            "phone_number": {
                "equals": phone_number
            }
        }
    )

    # Update user onboarding
    self.client.pages.update(
        page_id=user_page["id"],
        properties={
            "Onboarded": {  # Use actual property name
                "checkbox": True
            },
            "Status": {  # Use actual property name
                "select": {
                    "name": "Active"  # Must match option from above
                }
            }
        }
    )
    """)

    print("\n✅ Copy the property names exactly as shown above!")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nMake sure:")
    print("  1. NOTION_API_KEY is valid")
    print("  2. NOTION_USERS_DATABASE_ID is correct")
    print("  3. Your Notion integration has access to the database")

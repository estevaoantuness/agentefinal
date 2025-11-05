"""Notion user profile and onboarding management."""
import os
from notion_client import Client
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from src.config.settings import settings
from src.database.models import User
from src.utils.logger import logger


class NotionUserManager:
    """Manage user profiles and onboarding status in Notion."""

    def __init__(self):
        """Initialize Notion client."""
        self.client = Client(auth=settings.NOTION_API_KEY)
        # Users database ID - should be set via environment variable
        self.users_db_id = os.getenv('NOTION_USERS_DATABASE_ID')

        if not self.users_db_id:
            logger.warning("NOTION_USERS_DATABASE_ID not configured")

    def get_user_by_phone(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        Find user in Notion by phone number.

        Args:
            phone_number: User phone number

        Returns:
            Notion page data or None
        """
        if not self.users_db_id:
            return None

        try:
            response = self.client.databases.query(
                database_id=self.users_db_id,
                filter={
                    "property": "Phone",  # Adjust property name as needed
                    "phone_number": {
                        "equals": phone_number
                    }
                }
            )

            if response.get("results"):
                return response["results"][0]

            return None

        except Exception as e:
            logger.error(f"Error querying user in Notion: {e}")
            return None

    def mark_onboarding_complete(self, phone_number: str) -> bool:
        """
        Mark user as completed onboarding in Notion.

        Args:
            phone_number: User phone number

        Returns:
            Success status
        """
        if not self.users_db_id:
            logger.warning("Cannot mark onboarding: NOTION_USERS_DATABASE_ID not set")
            return False

        try:
            # Find user in Notion
            user_page = self.get_user_by_phone(phone_number)
            if not user_page:
                logger.warning(f"User {phone_number} not found in Notion")
                return False

            # Update properties
            self.client.pages.update(
                page_id=user_page["id"],
                properties={
                    "Onboarding_Stage": {  # Actual property name from Notion
                        "select": {
                            "name": "completed"  # Use actual option from Notion
                        }
                    },
                    "Last_Profile_Update": {  # Use actual property name
                        "date": {
                            "start": datetime.utcnow().isoformat()
                        }
                    }
                }
            )

            logger.info(f"User {phone_number} marked as onboarded in Notion")
            return True

        except Exception as e:
            logger.error(f"Error marking onboarding in Notion: {e}")
            return False

    def get_onboarding_status(self, phone_number: str) -> bool:
        """
        Check if user has completed onboarding.

        Args:
            phone_number: User phone number

        Returns:
            Onboarding status
        """
        if not self.users_db_id:
            return False

        try:
            user_page = self.get_user_by_phone(phone_number)
            if not user_page:
                return False

            # Check onboarding property
            props = user_page.get("properties", {})
            onboarding_prop = props.get("Onboarding_Stage", {})

            # Check if status is "completed"
            select_option = onboarding_prop.get("select", {})
            stage_name = select_option.get("name", "")

            return stage_name == "completed"

        except Exception as e:
            logger.error(f"Error getting onboarding status: {e}")
            return False

    def sync_user_to_notion(self, user: User) -> Optional[str]:
        """
        Create or update user in Notion.

        Args:
            user: User object

        Returns:
            Notion page ID or None
        """
        if not self.users_db_id:
            logger.warning("Cannot sync user: NOTION_USERS_DATABASE_ID not set")
            return None

        try:
            # Check if user exists
            existing_page = self.get_user_by_phone(user.phone_number)

            properties = {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": user.name or user.phone_number
                            }
                        }
                    ]
                },
                "Phone": {
                    "phone_number": user.phone_number
                },
                "First_Interaction": {  # Use actual property name from Notion
                    "date": {
                        "start": user.created_at.isoformat()
                    }
                }
            }

            if existing_page:
                # Update existing
                self.client.pages.update(
                    page_id=existing_page["id"],
                    properties=properties
                )
                logger.info(f"User {user.phone_number} updated in Notion")
                return existing_page["id"]
            else:
                # Create new
                response = self.client.pages.create(
                    parent={"database_id": self.users_db_id},
                    properties=properties
                )
                logger.info(f"User {user.phone_number} created in Notion")
                return response["id"]

        except Exception as e:
            logger.error(f"Error syncing user to Notion: {e}")
            return None

    def get_all_active_users(self) -> list:
        """
        Get all active users from Notion.

        Returns:
            List of user pages
        """
        if not self.users_db_id:
            return []

        try:
            response = self.client.databases.query(
                database_id=self.users_db_id,
                filter={
                    "property": "Status",
                    "select": {
                        "equals": "Active"
                    }
                }
            )

            return response.get("results", [])

        except Exception as e:
            logger.error(f"Error getting active users from Notion: {e}")
            return []

    def update_user_notion_field(
        self,
        phone_number: str,
        field_name: str,
        field_value: Any
    ) -> bool:
        """
        Update a specific field for user in Notion.

        Args:
            phone_number: User phone number
            field_name: Field name in Notion
            field_value: New value

        Returns:
            Success status
        """
        if not self.users_db_id:
            return False

        try:
            user_page = self.get_user_by_phone(phone_number)
            if not user_page:
                return False

            # Generic update for simple text fields
            properties = {
                field_name: {
                    "rich_text": [
                        {
                            "text": {
                                "content": str(field_value)
                            }
                        }
                    ]
                }
            }

            self.client.pages.update(
                page_id=user_page["id"],
                properties=properties
            )

            logger.info(f"User {phone_number} field '{field_name}' updated in Notion")
            return True

        except Exception as e:
            logger.error(f"Error updating user field in Notion: {e}")
            return False


# Global instance
import os
notion_user_manager = NotionUserManager()

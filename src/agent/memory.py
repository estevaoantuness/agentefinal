"""Conversation memory management using database."""
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from typing import List
from sqlalchemy.orm import Session

from src.database.models import ConversationHistory
from src.utils.logger import logger


class DatabaseChatHistory(BaseChatMessageHistory):
    """Chat history stored in PostgreSQL database."""

    def __init__(self, user_id: int, phone_number: str, db: Session):
        self.user_id = user_id
        self.phone_number = phone_number
        self.db = db

    @property
    def messages(self) -> List[BaseMessage]:
        """Get messages from database."""
        try:
            # Get last 20 messages for context
            history = (
                self.db.query(ConversationHistory)
                .filter(ConversationHistory.user_id == self.user_id)
                .order_by(ConversationHistory.created_at.desc())
                .limit(20)
                .all()
            )

            # Reverse to chronological order
            history = list(reversed(history))

            messages = []
            for record in history:
                if record.role == "user":
                    messages.append(HumanMessage(content=record.content))
                elif record.role == "assistant":
                    messages.append(AIMessage(content=record.content))

            return messages

        except Exception as e:
            logger.error(f"Error loading messages: {e}")
            return []

    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the database."""
        try:
            role = "user" if isinstance(message, HumanMessage) else "assistant"

            history = ConversationHistory(
                user_id=self.user_id,
                phone_number=self.phone_number,
                role=role,
                content=message.content
            )
            self.db.add(history)
            self.db.commit()

        except Exception as e:
            logger.error(f"Error saving message: {e}")
            self.db.rollback()

    def clear(self) -> None:
        """Clear all messages for this user."""
        try:
            self.db.query(ConversationHistory).filter(
                ConversationHistory.user_id == self.user_id
            ).delete()
            self.db.commit()

        except Exception as e:
            logger.error(f"Error clearing messages: {e}")
            self.db.rollback()


def get_memory(user_id: int, phone_number: str, db: Session) -> ConversationBufferMemory:
    """
    Get conversation memory for a user.

    Args:
        user_id: User ID
        phone_number: Phone number
        db: Database session

    Returns:
        ConversationBufferMemory instance
    """
    chat_history = DatabaseChatHistory(user_id, phone_number, db)

    memory = ConversationBufferMemory(
        chat_memory=chat_history,
        memory_key="chat_history",
        return_messages=True,
        output_key="output"
    )

    return memory

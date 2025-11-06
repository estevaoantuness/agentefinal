"""Conversation history management per user."""
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

from src.utils.logger import logger
from src.ai.system_prompt import get_system_prompt


class ConversationManager:
    """Manages conversation history with OpenAI."""

    def __init__(self, max_messages: int = 5, timeout_minutes: int = 30):
        """
        Initialize conversation manager.

        Args:
            max_messages: Maximum messages in history
            timeout_minutes: Conversation timeout in minutes
        """
        self.conversations: Dict[str, Dict] = {}
        self.max_messages = max_messages
        self.timeout_minutes = timeout_minutes

    def get_or_create_conversation(self, user_id: str, user_name: str = None) -> List[Dict[str, str]]:
        """
        Get user conversation history or create new one.

        Args:
            user_id: User ID
            user_name: User's name for personalization (optional)

        Returns:
            List of message objects
        """
        # Check if conversation exists and not expired
        if user_id in self.conversations:
            conv = self.conversations[user_id]
            last_activity = conv['last_activity']

            if user_name and conv['messages']:
                first_message = conv['messages'][0]
                if first_message.get('role') == "system":
                    first_message['content'] = get_system_prompt(user_name=user_name)

            if datetime.now() - last_activity < timedelta(minutes=self.timeout_minutes):
                logger.debug(f"Existing conversation found for {user_id}")
                return conv['messages']
            else:
                logger.info(f"Conversation expired for {user_id}, creating new one")

        # Create new conversation with personalized system prompt
        self.conversations[user_id] = {
            'messages': [
                {"role": "system", "content": get_system_prompt(user_name=user_name)}
            ],
            'last_activity': datetime.now()
        }

        logger.info(f"New conversation created for {user_id}")
        return self.conversations[user_id]['messages']

    def add_message(self, user_id: str, role: str, content: str):
        """
        Add message to conversation history.

        Args:
            user_id: User ID
            role: "user", "assistant" or "function"
            content: Message content
        """
        messages = self.get_or_create_conversation(user_id)

        messages.append({
            "role": role,
            "content": content
        })

        # Limit history size (keep system prompt)
        if len(messages) > self.max_messages + 1:
            # Keep system prompt + last N messages
            messages = [messages[0]] + messages[-(self.max_messages):]
            self.conversations[user_id]['messages'] = messages

        # Update last activity
        self.conversations[user_id]['last_activity'] = datetime.now()

        logger.debug(f"Message added: {role} - {content[:50]}...")

    def add_function_result(
        self,
        user_id: str,
        function_name: str,
        result: str,
        tool_call_id: Optional[str] = None
    ):
        """
        Add function result to conversation history.

        Args:
            user_id: User ID
            function_name: Executed function name
            result: Function result
            tool_call_id: Tool call id to link with assistant message (optional)
        """
        messages = self.get_or_create_conversation(user_id)

        entry = {
            "role": "tool" if tool_call_id else "function",
            "name": function_name,
            "content": result
        }

        if tool_call_id:
            entry["tool_call_id"] = tool_call_id

        messages.append(entry)

        self.conversations[user_id]['last_activity'] = datetime.now()

        logger.debug(f"Function result added: {function_name}")

    def add_tool_call_message(self, user_id: str, tool_call: Dict[str, Any]):
        """
        Record assistant tool call message so OpenAI can correlate tool responses.

        Args:
            user_id: User ID
            tool_call: Tool call payload as expected by OpenAI API
        """
        messages = self.get_or_create_conversation(user_id)

        messages.append({
            "role": "assistant",
            "content": "",
            "tool_calls": [tool_call]
        })

        self.conversations[user_id]['last_activity'] = datetime.now()

        logger.debug(f"Assistant tool call recorded: {tool_call.get('function', {}).get('name')}")

    def clear_conversation(self, user_id: str):
        """
        Clear user conversation.

        Args:
            user_id: User ID
        """
        if user_id in self.conversations:
            del self.conversations[user_id]
            logger.info(f"Conversation cleared for {user_id}")

    def cleanup_expired(self):
        """Remove expired conversations."""
        now = datetime.now()
        expired = []

        for user_id, conv in self.conversations.items():
            if now - conv['last_activity'] > timedelta(minutes=self.timeout_minutes):
                expired.append(user_id)

        for user_id in expired:
            del self.conversations[user_id]

        if expired:
            logger.info(f"Removed {len(expired)} expired conversations")


# Global instance with extended history for production usage
conversation_manager = ConversationManager(max_messages=20)

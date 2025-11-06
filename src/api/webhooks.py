"""Webhook handlers for Evolution API - with OpenAI integration."""
import json
import re
from fastapi import APIRouter, Request, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from src.database.session import get_db
from src.database.models import User
from src.utils.logger import logger
from src.utils.helpers import normalize_phone_number
from src.integrations.evolution_api import evolution_client

# OpenAI integration
from src.ai.openai_client import OpenAIClient
from src.ai.conversation_manager import conversation_manager
from src.ai.function_executor import function_executor

# Notion integration
from src.integrations.notion_users import notion_user_manager

# Command matcher for reliable command detection
from src.ai.command_matcher import command_matcher

router = APIRouter()

# Initialize OpenAI client
openai_client = OpenAIClient()


def clean_response_text(text: str) -> str:
    """
    Clean response text by removing function call tags and markers.

    Handles multiple formats:
    - <function=...></function>
    - =function_name>{...}
    - <function_name>

    Args:
        text: Raw response text

    Returns:
        Cleaned response text
    """
    if not text:
        return ""

    # Remove XML-style function tags: <function=...></function>
    cleaned = re.sub(r'<function=.*?></function>', '', text, flags=re.DOTALL)

    # Remove arrow-style function calls: =function_name>{...}
    cleaned = re.sub(r'=\w+>\{[^}]*\}', '', cleaned)

    # Remove simple angle bracket function markers: <function_name>
    cleaned = re.sub(r'<\w+>', '', cleaned)

    # Strip extra whitespace
    return cleaned.strip()


def parse_text_function_call(text: str) -> Optional[Dict]:
    """
    Parse text-based function calls when tool_calls is not available.

    Formats supported:
    - =function_name>{"arg": "value"}
    - <function=function_name>{"arg": "value"}</function>

    Args:
        text: Response text potentially containing function calls

    Returns:
        Dict with 'name' and 'arguments' or None if no match
    """
    if not text:
        return None

    # Try arrow format: =function_name>{...}
    arrow_match = re.search(r'=(\w+)>(\{[^}]*\})', text)
    if arrow_match:
        try:
            return {
                'name': arrow_match.group(1),
                'arguments': arrow_match.group(2)
            }
        except Exception as e:
            logger.warning(f"Error parsing arrow-format function call: {e}")

    # Try XML format: <function=name>args</function>
    xml_match = re.search(r'<function=(\w+)>(.*?)</function>', text, re.DOTALL)
    if xml_match:
        try:
            return {
                'name': xml_match.group(1),
                'arguments': xml_match.group(2).strip()
            }
        except Exception as e:
            logger.warning(f"Error parsing XML-format function call: {e}")

    return None


async def process_incoming_message(
    phone_number: str,
    message_text: str,
    user_name: str,
    db: Session
):
    """
    Process incoming WhatsApp message with OpenAI.

    Args:
        phone_number: Sender phone number
        message_text: Message content
        user_name: Sender name
        db: Database session
    """
    try:
        # Normalize phone number
        normalized_phone = normalize_phone_number(phone_number)

        # Get or create user
        user = db.query(User).filter(User.phone_number == normalized_phone).first()
        is_new_user = False
        if not user:
            user = User(
                phone_number=normalized_phone,
                name=user_name
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            is_new_user = True
            logger.info(f"New user created: {normalized_phone}")

            # Sync new user to Notion in background
            try:
                notion_user_manager.sync_user_to_notion(user)
                logger.info(f"User {normalized_phone} synced to Notion")
            except Exception as e:
                logger.warning(f"Could not sync user {normalized_phone} to Notion: {e}")

        user_id = str(user.id)

        # Process with OpenAI - pass user name for personalization
        response_text = await process_with_openai(user_id, message_text, db, user_name=user.name)

        # Send response via Evolution API
        evolution_client.send_text_message(
            phone_number=phone_number,
            message=response_text
        )

        logger.info(f"Message processed for user {normalized_phone}")

    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)

        # Send error message to user
        try:
            evolution_client.send_text_message(
                phone_number=phone_number,
                message="Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente mais tarde."
            )
        except Exception as inner_e:
            logger.error(f"Failed to send error message to {phone_number}: {inner_e}")


async def process_with_openai(user_id: str, message: str, db: Session, user_name: str = None) -> str:
    """
    Process message with OpenAI and execute functions.

    Args:
        user_id: User ID
        message: User message
        db: Database session
        user_name: User's name for personalization

    Returns:
        Assistant response
    """
    try:
        # === PHASE 1: Try reliable command matching FIRST ===
        command_match = command_matcher.match(message)

        if command_match and command_match.get('confidence') == 'high':
            # Direct function execution for high-confidence matches
            logger.info(f"Direct command match: {command_match['function']}")

            function_result = function_executor.execute(
                command_match['function'],
                command_match['arguments'],
                user_id
            )

            # Parse function result
            result_data = json.loads(function_result)

            if result_data.get('success'):
                # Add to conversation history
                conversation_manager.add_message(user_id, "user", message)
                conversation_manager.add_function_result(
                    user_id,
                    command_match['function'],
                    function_result
                )

                # Get natural language response from LLM
                messages = conversation_manager.get_or_create_conversation(user_id, user_name=user_name)
                response = openai_client.chat_completion(
                    messages=messages,
                    user_id=user_id,
                    user_name=user_name
                )
                response_text = clean_response_text(response.get('content', ''))
                conversation_manager.add_message(user_id, "assistant", response_text)
                return response_text
            else:
                # Function failed, fall through to LLM
                logger.warning(f"Command execution failed: {result_data.get('error')}")

        # === PHASE 2: Use LLM with fallback function call parsing ===
        conversation_manager.add_message(user_id, "user", message)

        # Get conversation history with personalization
        messages = conversation_manager.get_or_create_conversation(user_id, user_name)

        logger.info(f"Calling OpenAI for user {user_id} with {len(messages)} messages in history")

        # Call OpenAI with function calling
        # Functions are loaded from system_prompt by default
        response = openai_client.chat_completion(
            messages=messages,
            user_id=user_id,
            user_name=user_name,
            function_call="auto"
        )

        # Variable to track if function was executed
        function_name = None
        function_args = None

        # Check if OpenAI wants to call a function (tool_calls)
        if response.get('function_call'):
            # Standard function_call format
            tool_call = response['function_call']
            function_name = tool_call.get('name')
            function_args = json.loads(tool_call.get('arguments', '{}'))
            logger.info(f"OpenAI called function via function_call: {function_name}")

        elif response.get('content'):
            # Fallback: Check for text-based function calls
            text_call = parse_text_function_call(response['content'])
            if text_call:
                function_name = text_call['name']
                try:
                    function_args = json.loads(text_call['arguments'])
                    logger.info(f"OpenAI called function via text format: {function_name}")
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse function args: {text_call['arguments']}")

        # Execute function if found
        if function_name and function_args:
            function_result = function_executor.execute(
                function_name,
                function_args,
                user_id
            )

            conversation_manager.add_function_result(
                user_id,
                function_name,
                function_result
            )

            # Get natural response
            messages = conversation_manager.get_or_create_conversation(user_id, user_name=user_name)
            final_response = openai_client.chat_completion(
                messages=messages,
                user_id=user_id,
                user_name=user_name
            )
            response_text = clean_response_text(final_response.get('content', ''))
        else:
            # Direct response - but clean function call leakage
            response_text = clean_response_text(response.get('content', ''))

        # Add assistant response to history
        conversation_manager.add_message(user_id, "assistant", response_text)

        return response_text

    except Exception as e:
        logger.error(f"Error processing with OpenAI: {e}", exc_info=True)
        return "Desculpe, tive um problema ao processar sua mensagem. Pode tentar novamente?"


@router.post("/webhook/evolution")
async def evolution_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Webhook endpoint for Evolution API.

    Args:
        request: FastAPI request
        background_tasks: Background tasks manager
        db: Database session

    Returns:
        Success response
    """
    try:
        payload = await request.json()
        logger.debug(f"Webhook received: {payload}")

        event = payload.get("event")
        data = payload.get("data", {})

        # Only process incoming messages
        if event != "messages.upsert":
            return {"status": "ignored", "event": event}

        # Extract message data
        message_data = data.get("message", {})
        key_data = data.get("key", {})

        # Ignore messages from ourselves
        if key_data.get("fromMe", False):
            return {"status": "ignored", "reason": "from_me"}

        # Extract message info
        phone_number = key_data.get("remoteJid", "").split("@")[0]
        push_name = data.get("pushName", "Unknown")

        # Get message text
        message_text = None
        if "conversation" in message_data:
            message_text = message_data["conversation"]
        elif "extendedTextMessage" in message_data:
            message_text = message_data["extendedTextMessage"].get("text")

        if not message_text:
            logger.debug("No text message found in webhook data")
            return {"status": "ignored", "reason": "no_text"}

        # Process message in background
        background_tasks.add_task(
            process_incoming_message,
            phone_number=phone_number,
            message_text=message_text,
            user_name=push_name,
            db=db
        )

        return {"status": "success", "message": "Processing"}

    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return {"status": "healthy", "service": "pangeia_agent"}


@router.get("/webhook/test")
async def test_webhook() -> Dict[str, str]:
    """
    Test endpoint for webhook configuration.

    Returns:
        Test response
    """
    return {"status": "ok", "message": "Webhook is configured correctly"}

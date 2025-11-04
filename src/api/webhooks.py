"""Webhook handlers for Evolution API."""
from fastapi import APIRouter, Request, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from src.database.session import get_db
from src.database.models import User
from src.utils.logger import logger
from src.utils.helpers import normalize_phone_number
from src.integrations.evolution_api import evolution_client

router = APIRouter()


async def process_incoming_message(
    phone_number: str,
    message_text: str,
    user_name: str,
    db: Session
):
    """
    Process incoming WhatsApp message in background.

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
        if not user:
            user = User(
                phone_number=normalized_phone,
                name=user_name
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"New user created: {normalized_phone}")

        # Import here to avoid circular imports
        from src.agent.langchain_agent import process_message_with_agent

        # Process message with LangChain agent
        response = await process_message_with_agent(
            user_id=user.id,
            phone_number=normalized_phone,
            message=message_text,
            db=db
        )

        # Send response via Evolution API
        evolution_client.send_text_message(
            phone_number=phone_number,
            message=response
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
        except:
            pass


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

"""Evolution API client for WhatsApp integration."""
import requests
from typing import Optional, Dict, Any
import json

from src.config.settings import settings
from src.utils.logger import logger


class EvolutionAPIClient:
    """Client for Evolution API."""

    def __init__(self):
        self.base_url = settings.EVOLUTION_API_URL.rstrip('/')
        self.api_key = settings.EVOLUTION_API_KEY
        self.instance_name = settings.EVOLUTION_INSTANCE_NAME
        self.headers = {
            "Content-Type": "application/json",
            "apikey": self.api_key
        }

    def send_text_message(
        self,
        phone_number: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Send a text message via WhatsApp.

        Args:
            phone_number: Recipient phone number (with country code)
            message: Message text

        Returns:
            API response
        """
        url = f"{self.base_url}/message/sendText/{self.instance_name}"

        payload = {
            "number": phone_number,
            "text": message
        }

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            logger.info(f"Message sent to {phone_number}")
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending message to {phone_number}: {e}")
            raise

    def send_media_message(
        self,
        phone_number: str,
        media_url: str,
        caption: Optional[str] = None,
        media_type: str = "image"
    ) -> Dict[str, Any]:
        """
        Send a media message (image, video, etc.).

        Args:
            phone_number: Recipient phone number
            media_url: URL of the media file
            caption: Optional caption
            media_type: Type of media (image, video, document)

        Returns:
            API response
        """
        url = f"{self.base_url}/message/sendMedia/{self.instance_name}"

        payload = {
            "number": phone_number,
            "mediatype": media_type,
            "media": media_url
        }

        if caption:
            payload["caption"] = caption

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            logger.info(f"Media message sent to {phone_number}")
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending media to {phone_number}: {e}")
            raise

    def get_instance_status(self) -> Dict[str, Any]:
        """
        Get instance connection status.

        Returns:
            Instance status
        """
        url = f"{self.base_url}/instance/connectionState/{self.instance_name}"

        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting instance status: {e}")
            raise

    def create_instance(self, qrcode: bool = True) -> Dict[str, Any]:
        """
        Create a new Evolution API instance.

        Args:
            qrcode: Whether to generate QR code

        Returns:
            Instance creation response
        """
        url = f"{self.base_url}/instance/create"

        payload = {
            "instanceName": self.instance_name,
            "qrcode": qrcode,
            "integration": "WHATSAPP-BAILEYS"
        }

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            logger.info(f"Instance {self.instance_name} created")
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating instance: {e}")
            raise

    def set_webhook(self, webhook_url: str) -> Dict[str, Any]:
        """
        Configure webhook for receiving messages.

        Args:
            webhook_url: URL to receive webhooks

        Returns:
            Webhook configuration response
        """
        url = f"{self.base_url}/webhook/set/{self.instance_name}"

        payload = {
            "url": webhook_url,
            "webhook_by_events": False,
            "webhook_base64": False,
            "events": [
                "MESSAGES_UPSERT",
                "MESSAGES_UPDATE",
                "SEND_MESSAGE",
                "CONNECTION_UPDATE"
            ]
        }

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            logger.info(f"Webhook configured for {self.instance_name}")
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Error setting webhook: {e}")
            raise


# Global client instance
evolution_client = EvolutionAPIClient()

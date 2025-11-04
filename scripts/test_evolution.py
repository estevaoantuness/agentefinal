"""Script to test Evolution API connection."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.integrations.evolution_api import evolution_client
from src.utils.logger import logger


def test_instance_status():
    """Test Evolution API instance status."""
    print("\n🔍 Testing Evolution API connection...")
    print(f"API URL: {evolution_client.base_url}")
    print(f"Instance: {evolution_client.instance_name}")

    try:
        status = evolution_client.get_instance_status()
        print("\n✅ Connection successful!")
        print(f"Status: {status}")
        return True
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        logger.error(f"Evolution API test failed: {e}")
        return False


def test_send_message(phone_number: str):
    """
    Test sending a message.

    Args:
        phone_number: Phone number to send test message
    """
    print(f"\n📱 Sending test message to {phone_number}...")

    try:
        response = evolution_client.send_text_message(
            phone_number=phone_number,
            message="🤖 Teste do Agente Pangeia!\n\nSe você recebeu esta mensagem, a integração está funcionando!"
        )
        print("\n✅ Message sent successfully!")
        print(f"Response: {response}")
        return True
    except Exception as e:
        print(f"\n❌ Failed to send message: {e}")
        logger.error(f"Send message test failed: {e}")
        return False


def main():
    """Run Evolution API tests."""
    print("=" * 60)
    print("Evolution API Test Script")
    print("=" * 60)

    # Test connection
    if not test_instance_status():
        print("\n⚠️  Please check your Evolution API configuration in .env")
        sys.exit(1)

    # Ask if user wants to send test message
    send_test = input("\nDo you want to send a test message? (y/n): ").lower()

    if send_test == 'y':
        phone = input("Enter phone number (with country code, e.g., 5511999999999): ")
        test_send_message(phone)

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

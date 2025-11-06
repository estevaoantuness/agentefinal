"""Test script para testar OpenAI localmente sem WhatsApp"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/Users/estevaoantunes/agente_pangeia_final/.env')

# Add project to path
sys.path.insert(0, '/Users/estevaoantunes/agente_pangeia_final')

from src.ai.openai_client import OpenAIClient
from src.ai.system_prompt import SYSTEM_MESSAGES

def test_bot():
    """Test bot conversation locally"""
    
    print("=" * 70)
    print("🤖 PANGEIA BOT - LOCAL TEST")
    print("=" * 70)
    print()
    
    # Initialize client
    try:
        client = OpenAIClient()
        print("✅ OpenAI Client initialized successfully")
        print(f"   Model: {client.model}")
        print(f"   Temperature: {client.temperature}")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # Test cases
    test_scenarios = [
        {
            "name": "Greeting",
            "user_id": "user_001",
            "user_name": "Estevão",
            "message": "oi",
            "context": []
        },
        {
            "name": "View Tasks",
            "user_id": "user_001",
            "user_name": "Estevão",
            "message": "minhas tarefas",
            "context": [{"role": "user", "content": "oi"}]
        },
        {
            "name": "Create Task",
            "user_id": "user_001",
            "user_name": "Estevão",
            "message": "cria uma tarefa: fazer relatório",
            "context": []
        },
        {
            "name": "Mark Done",
            "user_id": "user_001",
            "user_name": "Estevão",
            "message": "feito 1",
            "context": [{"role": "user", "content": "minhas tarefas"}]
        },
        {
            "name": "In Progress",
            "user_id": "user_002",
            "user_name": "Luna",
            "message": "vou começar a fazer a tarefa 3",
            "context": []
        },
        {
            "name": "View Progress",
            "user_id": "user_001",
            "user_name": "Estevão",
            "message": "como estou indo? qual é meu progresso?",
            "context": []
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'━' * 70}")
        print(f"TEST {i}: {scenario['name']}")
        print(f"{'━' * 70}")
        print(f"User: {scenario['user_name']} (ID: {scenario['user_id']})")
        print(f"Message: \"{scenario['message']}\"")
        print()
        
        try:
            # Build messages
            messages = scenario['context'] + [
                {"role": "user", "content": scenario['message']}
            ]
            
            # Call OpenAI
            result = client.chat_completion(
                messages=messages,
                user_id=scenario['user_id'],
                user_name=scenario['user_name']
            )
            
            # Show result
            print(f"✅ Response received")
            print(f"   Finish Reason: {result['finish_reason']}")
            print(f"   Tokens Used: {result['usage']['total_tokens']}")
            print()
            print("📝 Bot Response:")
            print("─" * 70)
            print(result['content'])
            print("─" * 70)
            
            # Check for function calls
            if result['function_call']:
                print()
                print(f"🔧 Function Call Detected:")
                print(f"   Name: {result['function_call']['name']}")
                print(f"   Args: {result['function_call']['arguments']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'=' * 70}")
    print("✅ ALL TESTS COMPLETED")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    test_bot()

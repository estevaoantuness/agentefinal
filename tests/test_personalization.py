"""Tests for user personalization - system_prompt.py and conversation_manager.py."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from src.ai.system_prompt import get_system_prompt
from src.ai.conversation_manager import ConversationManager


class TestSystemPromptPersonalization:
    """Test suite for system_prompt personalization."""

    def test_default_prompt_without_user_name(self):
        """Test that default prompt is returned without user name."""
        prompt = get_system_prompt()
        assert prompt is not None
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "Você é Pangeia" in prompt

    def test_prompt_with_none_user_name(self):
        """Test that default prompt is returned for None user name."""
        prompt = get_system_prompt(user_name=None)
        assert prompt is not None
        assert "Você é Pangeia" in prompt

    def test_prompt_with_empty_string_user_name(self):
        """Test that default prompt is returned for empty string."""
        prompt = get_system_prompt(user_name="")
        assert prompt is not None
        assert "Você é Pangeia" in prompt

    def test_prompt_with_whitespace_only_user_name(self):
        """Test that default prompt is returned for whitespace-only name."""
        prompt = get_system_prompt(user_name="   ")
        assert prompt is not None
        assert "Você é Pangeia" in prompt

    def test_prompt_with_estevao_name(self):
        """Test personalized prompt with Estevao name."""
        prompt = get_system_prompt(user_name="Estevão")
        assert "Estevão" in prompt
        assert "Ajudar Estevão" in prompt

    def test_prompt_with_simple_name(self):
        """Test personalized prompt with simple name."""
        prompt = get_system_prompt(user_name="João")
        assert "João" in prompt
        assert "Ajudar João" in prompt

    def test_prompt_mentions_user_context(self):
        """Test that personalized prompt mentions user in context."""
        prompt = get_system_prompt(user_name="Maria")
        assert "Maria" in prompt
        assert "conversando" in prompt or "QUEM VOCÊ ESTÁ CONVERSANDO" in prompt

    def test_prompt_includes_all_features(self):
        """Test that personalized prompt includes all system features."""
        prompt = get_system_prompt(user_name="Test User")
        # Should include all the important sections
        assert "CONTEXTO DO SISTEMA" in prompt or "view_tasks" in prompt
        assert "TOM DE VOZ" in prompt or "Natural e amigável" in prompt

    def test_prompt_different_for_different_names(self):
        """Test that prompts differ for different user names."""
        prompt_estevao = get_system_prompt(user_name="Estevão")
        prompt_joao = get_system_prompt(user_name="João")

        # Should be different
        assert prompt_estevao != prompt_joao
        # Should each contain their own name
        assert "Estevão" in prompt_estevao
        assert "João" in prompt_joao

    def test_prompt_with_special_characters_in_name(self):
        """Test prompt with special characters in name."""
        names = ["José", "François", "Müller", "O'Brien"]
        for name in names:
            prompt = get_system_prompt(user_name=name)
            assert name in prompt
            assert "Pangeia" in prompt

    def test_prompt_with_long_name(self):
        """Test prompt with very long name."""
        long_name = "João Da Silva Santos Oliveira Costa"
        prompt = get_system_prompt(user_name=long_name)
        assert long_name in prompt
        assert "Pangeia" in prompt

    def test_prompt_length_reasonable(self):
        """Test that prompt length is reasonable."""
        prompt = get_system_prompt(user_name="Test")
        # Prompt should be substantial but not excessively long
        assert len(prompt) > 500  # Minimum reasonable size
        assert len(prompt) < 10000  # Not excessively long

    def test_prompt_with_numeric_name(self):
        """Test prompt with numeric characters in name."""
        prompt = get_system_prompt(user_name="Agent007")
        assert "Agent007" in prompt

    def test_prompt_with_emoji_in_name(self):
        """Test prompt with emoji in name."""
        prompt = get_system_prompt(user_name="João 🚀")
        assert "João" in prompt
        # Should not crash even with emoji


class TestConversationManagerPersonalization:
    """Test suite for ConversationManager with user personalization."""

    def setup_method(self):
        """Setup for each test."""
        self.manager = ConversationManager()

    def test_get_conversation_without_user_name(self):
        """Test creating conversation without user name."""
        messages = self.manager.get_or_create_conversation("user_1")
        assert messages is not None
        assert isinstance(messages, list)
        assert len(messages) > 0
        # Should have system prompt as first message
        assert messages[0]['role'] == 'system'

    def test_get_conversation_with_user_name(self):
        """Test creating conversation with user name."""
        messages = self.manager.get_or_create_conversation("user_1", user_name="Estevão")
        assert messages is not None
        assert len(messages) > 0
        # System prompt should contain user name
        assert "Estevão" in messages[0]['content']

    def test_user_name_in_system_prompt(self):
        """Test that user name is included in system prompt."""
        messages = self.manager.get_or_create_conversation("user_2", user_name="João")
        system_prompt = messages[0]['content']
        assert "João" in system_prompt

    def test_different_users_different_prompts(self):
        """Test that different users get personalized prompts."""
        messages_estevao = self.manager.get_or_create_conversation("user_estevao", user_name="Estevão")
        messages_joao = self.manager.get_or_create_conversation("user_joao", user_name="João")

        prompt_estevao = messages_estevao[0]['content']
        prompt_joao = messages_joao[0]['content']

        # Should be different
        assert prompt_estevao != prompt_joao
        assert "Estevão" in prompt_estevao
        assert "João" in prompt_joao

    def test_conversation_persists_across_calls(self):
        """Test that conversation history persists."""
        user_id = "user_3"
        messages1 = self.manager.get_or_create_conversation(user_id, user_name="Test")
        initial_count = len(messages1)

        # Add a message
        self.manager.add_message(user_id, "user", "Olá")

        # Get conversation again
        messages2 = self.manager.get_or_create_conversation(user_id, user_name="Test")

        # Should have one more message
        assert len(messages2) == initial_count + 1

    def test_add_message_with_user_context(self):
        """Test adding messages after user context is set."""
        user_id = "user_4"
        self.manager.get_or_create_conversation(user_id, user_name="Maria")

        # Add multiple messages
        self.manager.add_message(user_id, "user", "minhas tarefas")
        self.manager.add_message(user_id, "assistant", "Aqui estão suas tarefas, Maria!")

        messages = self.manager.get_or_create_conversation(user_id)
        assert len(messages) >= 3  # system + 2 messages

    def test_conversation_timeout_with_personalization(self):
        """Test that expired conversations are recreated with personalization."""
        user_id = "user_5"
        manager = ConversationManager(timeout_minutes=0)  # Immediate timeout

        # Create conversation
        messages1 = manager.get_or_create_conversation(user_id, user_name="Estevão")
        msg1_content = messages1[0]['content']

        # Simulate time passing (conversation expires)
        import time
        time.sleep(0.1)

        # Get conversation again - should be recreated
        messages2 = manager.get_or_create_conversation(user_id, user_name="Estevão")

        # Should have same personalization
        assert "Estevão" in messages2[0]['content']

    def test_multiple_users_isolation(self):
        """Test that different users' conversations are isolated."""
        # Create conversations for two users
        self.manager.get_or_create_conversation("user_a", user_name="Alice")
        self.manager.get_or_create_conversation("user_b", user_name="Bob")

        # Add messages to each
        self.manager.add_message("user_a", "user", "Mensagem de Alice")
        self.manager.add_message("user_b", "user", "Mensagem de Bob")

        # Get conversations
        conv_a = self.manager.get_or_create_conversation("user_a")
        conv_b = self.manager.get_or_create_conversation("user_b")

        # Should have different messages
        assert "Alice" in conv_a[0]['content']
        assert "Bob" in conv_b[0]['content']

    def test_conversation_maintains_history_limit(self):
        """Test that conversation respects message limit."""
        user_id = "user_6"
        manager = ConversationManager(max_messages=5)

        self.manager.get_or_create_conversation(user_id, user_name="Test")

        # Add more messages than limit
        for i in range(10):
            self.manager.add_message(user_id, "user", f"Message {i}")

        messages = self.manager.get_or_create_conversation(user_id)

        # Should keep system prompt + max_messages
        assert len(messages) <= 6  # system + 5 messages

    def test_function_result_preserves_personalization(self):
        """Test that function results don't affect personalization."""
        user_id = "user_7"
        self.manager.get_or_create_conversation(user_id, user_name="Estevão")
        self.manager.add_message(user_id, "user", "minhas tarefas")

        # Add function result
        self.manager.add_function_result(user_id, "view_tasks", '{"success": true}')

        messages = self.manager.get_or_create_conversation(user_id)

        # Should still have personalization
        assert "Estevão" in messages[0]['content']

    # ========== ESTEVAO-SPECIFIC TESTS ==========
    def test_estevao_personalization_flow(self):
        """Test complete flow for Estevao user."""
        # Simulate Estevao starting conversation
        messages = self.manager.get_or_create_conversation("estevao_phone", user_name="Estevão")

        # System prompt should greet Estevao
        assert "Estevão" in messages[0]['content']

        # Add message from user
        self.manager.add_message("estevao_phone", "user", "oi")

        # Add response that uses his name
        self.manager.add_message("estevao_phone", "assistant", "Olá Estevão! Como posso ajudar?")

        messages = self.manager.get_or_create_conversation("estevao_phone")

        # Should have 3 messages: system, user message, assistant response
        assert len(messages) >= 3
        assert "Estevão" in messages[0]['content']

    def test_estevao_task_workflow(self):
        """Test complete task workflow for Estevao."""
        user_id = "estevao_task_flow"
        self.manager.get_or_create_conversation(user_id, user_name="Estevão")

        # Step 1: List tasks
        self.manager.add_message(user_id, "user", "minhas tarefas")
        self.manager.add_message(user_id, "assistant", "Aqui estão suas tarefas, Estevão!")

        # Step 2: Mark as done
        self.manager.add_message(user_id, "user", "feito 1")
        self.manager.add_function_result(user_id, "mark_done", '{"success": true}')
        self.manager.add_message(user_id, "assistant", "Parabéns, Estevão! Tarefa marcada como concluída!")

        messages = self.manager.get_or_create_conversation(user_id)

        # Should have preserved conversation and personalization
        assert "Estevão" in messages[0]['content']
        assert len(messages) >= 5  # system + messages + function result


class TestPersonalizationEdgeCases:
    """Test edge cases in personalization."""

    def test_none_type_not_personalized(self):
        """Test that None type doesn't break personalization."""
        prompt = get_system_prompt(user_name=None)
        assert prompt is not None
        assert isinstance(prompt, str)

    def test_integer_type_not_personalized(self):
        """Test that integer type doesn't cause issues."""
        try:
            prompt = get_system_prompt(user_name=123)
            # Should either not personalize or handle gracefully
            assert "Pangeia" in prompt
        except (TypeError, AttributeError):
            # It's acceptable to raise error for wrong type
            pass

    def test_boolean_type_not_personalized(self):
        """Test that boolean type doesn't cause issues."""
        try:
            prompt = get_system_prompt(user_name=True)
            assert "Pangeia" in prompt
        except (TypeError, AttributeError):
            pass

    def test_list_type_not_personalized(self):
        """Test that list type doesn't cause issues."""
        try:
            prompt = get_system_prompt(user_name=["Name"])
            assert "Pangeia" in prompt
        except (TypeError, AttributeError):
            pass

    def test_very_long_user_name(self):
        """Test with extremely long user name."""
        long_name = "A" * 1000
        prompt = get_system_prompt(user_name=long_name)
        assert long_name in prompt

    def test_user_name_with_script_content(self):
        """Test that script content in name is safe."""
        prompt = get_system_prompt(user_name="<script>alert('xss')</script>")
        # Should not execute or cause issues
        assert "Pangeia" in prompt

    def test_user_name_with_sql_injection(self):
        """Test that SQL injection attempt in name is safe."""
        prompt = get_system_prompt(user_name="'; DROP TABLE users; --")
        # Should not cause issues
        assert "Pangeia" in prompt

    def test_conversation_with_problematic_user_id(self):
        """Test conversation manager with problematic user IDs."""
        manager = ConversationManager()

        test_ids = [
            "user:123",
            "user@example.com",
            "user/path",
            "user\\path",
            "user-123-456",
        ]

        for user_id in test_ids:
            messages = manager.get_or_create_conversation(user_id, user_name="Test")
            assert messages is not None
            assert len(messages) > 0


class TestPersonalizationConcurrency:
    """Test personalization under concurrent access."""

    def test_multiple_users_concurrent_context(self):
        """Test that multiple users can have concurrent conversations."""
        manager = ConversationManager()

        # Simulate multiple users
        users = [
            ("user_1", "Alice"),
            ("user_2", "Bob"),
            ("user_3", "Charlie"),
            ("user_4", "Diana"),
            ("user_5", "Estevão"),
        ]

        # Create conversations for all
        for user_id, name in users:
            manager.get_or_create_conversation(user_id, user_name=name)
            manager.add_message(user_id, "user", "Olá")

        # Verify each has personalized conversation
        for user_id, name in users:
            messages = manager.get_or_create_conversation(user_id)
            assert name in messages[0]['content']

    def test_add_messages_concurrently(self):
        """Test adding messages for multiple users concurrently."""
        manager = ConversationManager()

        # Setup conversations
        manager.get_or_create_conversation("user_a", user_name="Alice")
        manager.get_or_create_conversation("user_b", user_name="Bob")

        # Add messages interleaved
        manager.add_message("user_a", "user", "Message 1")
        manager.add_message("user_b", "user", "Message 1")
        manager.add_message("user_a", "assistant", "Response 1")
        manager.add_message("user_b", "assistant", "Response 1")

        # Verify isolation
        conv_a = manager.get_or_create_conversation("user_a")
        conv_b = manager.get_or_create_conversation("user_b")

        assert "Alice" in conv_a[0]['content']
        assert "Bob" in conv_b[0]['content']

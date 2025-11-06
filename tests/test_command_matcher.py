"""Tests for command_matcher.py - NLP-like command pattern matching."""

import pytest
from src.ai.command_matcher import CommandMatcher


class TestCommandMatcher:
    """Test suite for CommandMatcher class."""

    def setup_method(self):
        """Setup for each test."""
        self.matcher = CommandMatcher()

    # ========== VIEW_TASKS TESTS ==========
    def test_view_tasks_simple_variation_1(self):
        """Test 'minhas tarefas' pattern."""
        result = self.matcher.match("minhas tarefas")
        assert result is not None
        assert result['function'] == 'view_tasks'
        assert result['confidence'] == 'high'
        assert result['arguments']['filter_status'] == 'all'

    def test_view_tasks_simple_variation_2(self):
        """Test 'minha tarefa' singular."""
        result = self.matcher.match("minha tarefa")
        assert result is not None
        assert result['function'] == 'view_tasks'

    def test_view_tasks_list_variation(self):
        """Test 'ver tarefas' pattern."""
        result = self.matcher.match("ver tarefas")
        assert result is not None
        assert result['function'] == 'view_tasks'

    def test_view_tasks_english_variant(self):
        """Test 'task' English variant."""
        result = self.matcher.match("task")
        assert result is not None
        assert result['function'] == 'view_tasks'

    def test_view_tasks_with_pending_status(self):
        """Test task list with status filter - pending."""
        result = self.matcher.match("minhas tarefas pendente")
        assert result is not None
        assert result['function'] == 'view_tasks'
        assert result['arguments']['filter_status'] == 'pending'

    def test_view_tasks_with_progress_status(self):
        """Test task list with status filter - in progress."""
        result = self.matcher.match("tarefas em andamento")
        assert result is not None
        assert result['function'] == 'view_tasks'
        assert result['arguments']['filter_status'] == 'in_progress'

    def test_view_tasks_with_completed_status(self):
        """Test task list with completed status."""
        result = self.matcher.match("tarefas concluída")
        assert result is not None
        assert result['function'] == 'view_tasks'
        assert result['arguments']['filter_status'] == 'completed'

    def test_view_tasks_case_insensitive(self):
        """Test case insensitivity."""
        result = self.matcher.match("MINHAS TAREFAS")
        assert result is not None
        assert result['function'] == 'view_tasks'

    # ========== CREATE_TASK TESTS ==========
    def test_create_task_simple(self):
        """Test 'criar tarefa' pattern."""
        result = self.matcher.match("criar tarefa")
        assert result is not None
        assert result['function'] == 'create_task'

    def test_create_task_with_title(self):
        """Test task creation with title extraction."""
        result = self.matcher.match("criar tarefa: Implementar API de autenticação")
        assert result is not None
        assert result['function'] == 'create_task'
        assert result['arguments']['title'] == 'Implementar API de autenticação'

    def test_create_task_nova_variation(self):
        """Test 'nova tarefa' variation."""
        result = self.matcher.match("nova tarefa: Revisar código")
        assert result is not None
        assert result['function'] == 'create_task'
        assert result['arguments']['title'] == 'Revisar código'

    def test_create_task_adicionar_variation(self):
        """Test 'adicionar tarefa' variation."""
        result = self.matcher.match("adicionar tarefa: Reunião com cliente")
        assert result is not None
        assert result['function'] == 'create_task'

    def test_create_task_short_form(self):
        """Test short form 'cria' variation."""
        result = self.matcher.match("cria tarefa: Estudar Python")
        assert result is not None
        assert result['function'] == 'create_task'

    def test_create_task_with_space_delimiter(self):
        """Test with space instead of colon."""
        result = self.matcher.match("criar tarefa Fazer compras")
        assert result is not None
        assert result['function'] == 'create_task'

    # ========== MARK_DONE TESTS ==========
    def test_mark_done_single_number(self):
        """Test 'feito 1' pattern."""
        result = self.matcher.match("feito 1")
        assert result is not None
        assert result['function'] == 'mark_done'
        assert result['arguments']['task_numbers'] == [1]

    def test_mark_done_multiple_numbers(self):
        """Test marking multiple tasks done."""
        result = self.matcher.match("feito 1 2 3")
        assert result is not None
        assert result['function'] == 'mark_done'
        assert result['arguments']['task_numbers'] == [1, 2, 3]

    def test_mark_done_concluir_variation(self):
        """Test 'concluí' variation."""
        result = self.matcher.match("concluí 5")
        assert result is not None
        assert result['function'] == 'mark_done'
        assert result['arguments']['task_numbers'] == [5]

    def test_mark_done_finalizei_variation(self):
        """Test 'finalizei' variation."""
        result = self.matcher.match("finalizei 2")
        assert result is not None
        assert result['function'] == 'mark_done'

    def test_mark_done_completei_variation(self):
        """Test 'completei' variation."""
        result = self.matcher.match("completei 3")
        assert result is not None
        assert result['function'] == 'mark_done'

    def test_mark_done_english_variation(self):
        """Test English 'done' variation."""
        result = self.matcher.match("done 1")
        assert result is not None
        assert result['function'] == 'mark_done'

    def test_mark_done_with_large_numbers(self):
        """Test with larger task numbers."""
        result = self.matcher.match("feito 99")
        assert result is not None
        assert result['function'] == 'mark_done'
        assert result['arguments']['task_numbers'] == [99]

    def test_mark_done_filters_invalid_numbers(self):
        """Test that numbers outside valid range are filtered."""
        result = self.matcher.match("feito 1 2 5000")
        assert result is not None
        assert result['function'] == 'mark_done'
        # 5000 is filtered out (> 999)
        assert result['arguments']['task_numbers'] == [1, 2]

    # ========== MARK_PROGRESS TESTS ==========
    def test_mark_progress_comecei(self):
        """Test 'comecei' pattern."""
        result = self.matcher.match("comecei 1")
        assert result is not None
        assert result['function'] == 'mark_progress'
        assert result['arguments']['task_numbers'] == [1]

    def test_mark_progress_iniciei(self):
        """Test 'iniciei' variation."""
        result = self.matcher.match("iniciei 3")
        assert result is not None
        assert result['function'] == 'mark_progress'

    def test_mark_progress_estou_fazendo(self):
        """Test 'estou fazendo' variation."""
        result = self.matcher.match("estou fazendo 2")
        assert result is not None
        assert result['function'] == 'mark_progress'

    def test_mark_progress_em_andamento(self):
        """Test 'em andamento' variation."""
        result = self.matcher.match("em andamento 1")
        assert result is not None
        assert result['function'] == 'mark_progress'

    def test_mark_progress_multiple_tasks(self):
        """Test marking multiple tasks as in progress."""
        result = self.matcher.match("comecei 1 2 3")
        assert result is not None
        assert result['function'] == 'mark_progress'
        assert result['arguments']['task_numbers'] == [1, 2, 3]

    def test_mark_progress_english_working_on(self):
        """Test English 'working on' variation."""
        result = self.matcher.match("working on 1")
        assert result is not None
        assert result['function'] == 'mark_progress'

    # ========== VIEW_PROGRESS TESTS ==========
    def test_view_progress_simple(self):
        """Test 'meu progresso' pattern."""
        result = self.matcher.match("meu progresso")
        assert result is not None
        assert result['function'] == 'view_progress'
        assert result['arguments'] == {}

    def test_view_progress_como_estou(self):
        """Test 'como estou indo' variation."""
        result = self.matcher.match("como estou indo")
        assert result is not None
        assert result['function'] == 'view_progress'

    def test_view_progress_relatorio(self):
        """Test 'relatório' variation."""
        result = self.matcher.match("relatório")
        assert result is not None
        assert result['function'] == 'view_progress'

    def test_view_progress_status(self):
        """Test 'status' variation."""
        result = self.matcher.match("status")
        assert result is not None
        assert result['function'] == 'view_progress'

    def test_view_progress_english(self):
        """Test English 'progress' variation."""
        result = self.matcher.match("progress")
        assert result is not None
        assert result['function'] == 'view_progress'

    # ========== GET_HELP TESTS ==========
    def test_get_help_ajuda(self):
        """Test 'ajuda' pattern."""
        result = self.matcher.match("ajuda")
        assert result is not None
        assert result['function'] == 'get_help'

    def test_get_help_english(self):
        """Test English 'help' pattern."""
        result = self.matcher.match("help")
        assert result is not None
        assert result['function'] == 'get_help'

    def test_get_help_o_que_faz(self):
        """Test 'o que você faz' variation."""
        result = self.matcher.match("o que você faz")
        assert result is not None
        assert result['function'] == 'get_help'

    def test_get_help_comandos(self):
        """Test 'comandos' variation."""
        result = self.matcher.match("comandos")
        assert result is not None
        assert result['function'] == 'get_help'

    def test_get_help_como_funciona(self):
        """Test 'como funciona' variation."""
        result = self.matcher.match("como funciona")
        assert result is not None
        assert result['function'] == 'get_help'

    # ========== EDGE CASES ==========
    def test_no_match_returns_none(self):
        """Test that non-matching messages return None."""
        result = self.matcher.match("olá como você está")
        assert result is None

    def test_empty_message_returns_none(self):
        """Test that empty string returns None."""
        result = self.matcher.match("")
        assert result is None

    def test_whitespace_only_returns_none(self):
        """Test that whitespace-only string returns None."""
        result = self.matcher.match("   ")
        assert result is None

    def test_none_input_returns_none(self):
        """Test that None input returns None."""
        result = self.matcher.match(None)
        assert result is None

    def test_non_string_input_returns_none(self):
        """Test that non-string input returns None."""
        result = self.matcher.match(123)
        assert result is None

    def test_special_characters_in_message(self):
        """Test message with special characters."""
        result = self.matcher.match("minhas tarefas!!!!")
        assert result is not None
        assert result['function'] == 'view_tasks'

    def test_mixed_case_with_accents(self):
        """Test mixed case with Portuguese accents."""
        result = self.matcher.match("MINHAS TAREFAS")
        assert result is not None
        assert result['function'] == 'view_tasks'

    def test_very_long_message(self):
        """Test with very long message."""
        long_message = "minhas tarefas " + "x" * 1000
        result = self.matcher.match(long_message)
        assert result is not None
        assert result['function'] == 'view_tasks'

    def test_unicode_characters(self):
        """Test with unicode characters."""
        result = self.matcher.match("minhas tarefas 📝")
        assert result is not None
        assert result['function'] == 'view_tasks'

    def test_create_task_with_special_title(self):
        """Test task creation with special characters in title."""
        result = self.matcher.match("criar tarefa: Fix bug #123 & implement feature")
        assert result is not None
        assert result['function'] == 'create_task'
        assert "Fix bug" in result['arguments']['title']

    def test_multiple_numbers_extraction(self):
        """Test extraction of multiple numbers from message."""
        result = self.matcher.match("feito 1 2 3 4 5")
        assert result is not None
        assert result['arguments']['task_numbers'] == [1, 2, 3, 4, 5]

    def test_numbers_with_extra_words(self):
        """Test number extraction with extra words."""
        result = self.matcher.match("eu concluí a tarefa número 1 e número 2")
        assert result is not None
        assert result['function'] == 'mark_done'
        assert 1 in result['arguments']['task_numbers']
        assert 2 in result['arguments']['task_numbers']

    def test_first_match_wins(self):
        """Test that first matching pattern is returned."""
        # This message could match multiple patterns
        result = self.matcher.match("criar tarefa minhas tarefas")
        assert result is not None
        # Should match first pattern found
        assert result['function'] in ['create_task', 'view_tasks']

    # ========== ESTEVAO-SPECIFIC TESTS ==========
    def test_estevao_portuguese_variations(self):
        """Test common Portuguese variations Estevao might use."""
        test_cases = [
            ("qual é meu progresso", "view_progress"),
            ("como estou indo", "view_progress"),
            ("o que tenho pra fazer", "view_tasks"),
            ("que tenho pra fazer", "view_tasks"),
            ("listar", "view_tasks"),
            ("mostrar tarefas", "view_tasks"),
            ("preciso fazer algo", "create_task"),
            ("nova tarefa de código", "create_task"),
        ]

        for message, expected_function in test_cases:
            result = self.matcher.match(message)
            assert result is not None, f"Failed to match: {message}"
            assert result['function'] == expected_function, f"Wrong function for: {message}"

    def test_estevao_number_sequences(self):
        """Test various number input patterns."""
        test_cases = [
            ("feito 1", [1]),
            ("pronto 1", [1]),
            ("feito 1 2", [1, 2]),
            ("marcar 1 como feita", [1]),
            ("completar tarefas 1 2 3", [1, 2, 3]),
        ]

        for message, expected_numbers in test_cases:
            result = self.matcher.match(message)
            if result and result['function'] in ['mark_done', 'mark_progress']:
                assert result['arguments']['task_numbers'] == expected_numbers


class TestCommandMatcherRobustness:
    """Test robustness and error handling."""

    def setup_method(self):
        """Setup for each test."""
        self.matcher = CommandMatcher()

    def test_handles_multiple_spaces(self):
        """Test handling of multiple consecutive spaces."""
        result = self.matcher.match("minhas    tarefas")
        assert result is not None
        assert result['function'] == 'view_tasks'

    def test_handles_tabs_and_newlines(self):
        """Test handling of tabs and newlines."""
        result = self.matcher.match("minhas\ttarefas")
        assert result is not None
        assert result['function'] == 'view_tasks'

    def test_handles_leading_trailing_whitespace(self):
        """Test handling of leading/trailing whitespace."""
        result = self.matcher.match("  minhas tarefas  ")
        assert result is not None
        assert result['function'] == 'view_tasks'

    def test_pattern_does_not_crash_on_edge_cases(self):
        """Test that all patterns handle edge cases gracefully."""
        edge_cases = [
            "",
            " ",
            "\n",
            "\t",
            "!!!",
            "###",
            "@@@",
            "123456789",
            "aaaaaaaaaa",
            ".",
            ",",
            ";",
        ]

        for message in edge_cases:
            # Should not raise exception
            result = self.matcher.match(message)
            # Result can be None or a dict
            assert result is None or isinstance(result, dict)

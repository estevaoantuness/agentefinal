"""Tests for webhooks.py functions - response cleaning and function call parsing."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from src.api.webhooks import clean_response_text, parse_text_function_call


class TestCleanResponseText:
    """Test suite for clean_response_text function."""

    def test_empty_string(self):
        """Test cleaning empty string."""
        result = clean_response_text("")
        assert result == ""

    def test_none_input(self):
        """Test cleaning None input."""
        result = clean_response_text(None)
        assert result == ""

    def test_plain_text_unchanged(self):
        """Test that plain text is unchanged."""
        text = "Olá, como posso ajudar?"
        result = clean_response_text(text)
        assert result == text

    # ========== XML-STYLE FUNCTION TAGS ==========
    def test_remove_xml_style_function_tag(self):
        """Test removal of XML-style function tag."""
        text = "Vou listar suas tarefas. <function=view_tasks></function>"
        result = clean_response_text(text)
        assert result == "Vou listar suas tarefas."

    def test_remove_xml_style_with_content(self):
        """Test removal of XML-style tag with content inside."""
        text = "Executando tarefa <function=view_tasks>{\"filter_status\": \"all\"}</function>"
        result = clean_response_text(text)
        assert result == "Executando tarefa"

    def test_remove_multiple_xml_tags(self):
        """Test removal of multiple XML-style tags."""
        text = "Primeiro <function=mark_done></function> segundo <function=view_tasks></function>"
        result = clean_response_text(text)
        assert result == "Primeiro  segundo"

    def test_xml_tag_multiline(self):
        """Test removal of multiline XML tags."""
        text = """Vou executar a tarefa
        <function=view_tasks>
            {"filter_status": "pending"}
        </function>
        Feito!"""
        result = clean_response_text(text)
        assert "function" not in result
        assert "Vou executar" in result

    # ========== ARROW-STYLE FUNCTION CALLS ==========
    def test_remove_arrow_style_function_call(self):
        """Test removal of arrow-style function call."""
        text = "Listando tarefas =view_tasks>{\"filter_status\": \"all\"}"
        result = clean_response_text(text)
        assert result == "Listando tarefas"

    def test_remove_arrow_style_simple(self):
        """Test removal of simple arrow-style call."""
        text = "Pronto =mark_done>{\"task_numbers\": [1]}"
        result = clean_response_text(text)
        assert result == "Pronto"

    def test_remove_multiple_arrow_calls(self):
        """Test removal of multiple arrow-style calls."""
        text = "Primeiro =func1>{} segundo =func2>{}"
        result = clean_response_text(text)
        assert "=" not in result
        assert "{" not in result

    def test_arrow_style_with_nested_json(self):
        """Test arrow style with nested JSON."""
        text = "Tarefa =create_task>{\"title\": \"Test\", \"nested\": {\"key\": \"value\"}}"
        result = clean_response_text(text)
        # Should clean the arrow-style call
        assert "=create_task" not in result
        assert "Tarefa" in result

    # ========== ANGLE-BRACKET FUNCTION MARKERS ==========
    def test_remove_angle_bracket_function_marker(self):
        """Test removal of angle bracket function markers."""
        text = "Vou fazer <view_tasks> Feito!"
        result = clean_response_text(text)
        assert result == "Vou fazer  Feito!"
        assert "<view_tasks>" not in result

    def test_remove_multiple_angle_brackets(self):
        """Test removal of multiple angle bracket markers."""
        text = "Executando <mark_done> <create_task> <view_progress>"
        result = clean_response_text(text)
        assert "<" not in result
        assert ">" not in result
        assert "Executando" in result

    def test_angle_brackets_with_underscores(self):
        """Test angle brackets with underscores."""
        text = "Task <mark_progress> complete"
        result = clean_response_text(text)
        assert "<mark_progress>" not in result
        assert "Task  complete" == result

    # ========== MIXED FORMATS ==========
    def test_remove_mixed_function_call_formats(self):
        """Test removal when multiple formats are present."""
        text = """Vou fazer as seguintes operações:
        1. Listar <view_tasks>
        2. Marcar feito =mark_done>{"task_numbers": [1]}
        3. Ver progresso <function=view_progress></function>
        Pronto!"""
        result = clean_response_text(text)
        assert "function" not in result
        assert "view_tasks" not in result
        assert "mark_done" not in result
        assert "view_progress" not in result
        assert "Pronto!" in result

    # ========== WHITESPACE HANDLING ==========
    def test_clean_extra_whitespace(self):
        """Test that extra whitespace is trimmed."""
        text = "   Olá   mundo   "
        result = clean_response_text(text)
        assert result == "Olá   mundo"

    def test_multiple_spaces_between_words_preserved(self):
        """Test that multiple spaces between words are preserved."""
        text = "Olá  mundo"
        result = clean_response_text(text)
        assert "Olá  mundo" == result

    def test_removes_newlines_at_edges(self):
        """Test removal of leading/trailing newlines."""
        text = "\n\nOlá\n\n"
        result = clean_response_text(text)
        assert result == "Olá"

    # ========== SPECIAL CHARACTERS ==========
    def test_preserves_emojis(self):
        """Test that emojis are preserved."""
        text = "✅ Tarefa concluída <mark_done>!"
        result = clean_response_text(text)
        assert "✅" in result
        assert "<mark_done>" not in result

    def test_preserves_special_punctuation(self):
        """Test that special punctuation is preserved."""
        text = "Parabéns!!! Você finalizou a tarefa <view_progress>."
        result = clean_response_text(text)
        assert "Parabéns!!!" in result
        assert "Você finalizou" in result

    # ========== REAL-WORLD SCENARIOS ==========
    def test_groq_response_scenario_1(self):
        """Test real Groq response with function call display bug."""
        text = "=view_tasks>{\"filter_status\": \"all\"}"
        result = clean_response_text(text)
        assert result == ""

    def test_groq_response_scenario_2(self):
        """Test Groq response with explanation and function call."""
        text = """Vou listar suas tarefas agora =view_tasks>{"filter_status": "all"}"""
        result = clean_response_text(text)
        assert result == "Vou listar suas tarefas agora"

    def test_groq_response_scenario_3(self):
        """Test Groq response with XML function call."""
        text = """Deixe-me marcar essa tarefa como concluída para você.
        <function=mark_done>{"task_numbers": [1, 2]}</function>
        Feito!"""
        result = clean_response_text(text)
        assert "mark_done" not in result
        assert "Deixe-me marcar" in result
        assert "Feito!" in result

    def test_estevao_natural_text_with_function_leakage(self):
        """Test real Estevao scenario with function call leakage."""
        text = "Oi Estevão! Vou ver suas tarefas <view_tasks>"
        result = clean_response_text(text)
        assert result == "Oi Estevão! Vou ver suas tarefas"


class TestParseTextFunctionCall:
    """Test suite for parse_text_function_call function."""

    def test_parse_arrow_format_simple(self):
        """Test parsing simple arrow format."""
        text = "=view_tasks>{\"filter_status\": \"all\"}"
        result = parse_text_function_call(text)
        assert result is not None
        assert result['name'] == 'view_tasks'
        assert result['arguments'] == "{\"filter_status\": \"all\"}"

    def test_parse_arrow_format_in_sentence(self):
        """Test parsing arrow format within a sentence."""
        text = "Vou listar tarefas =view_tasks>{\"filter_status\": \"pending\"}"
        result = parse_text_function_call(text)
        assert result is not None
        assert result['name'] == 'view_tasks'
        assert "pending" in result['arguments']

    def test_parse_arrow_format_create_task(self):
        """Test parsing create_task arrow format."""
        text = "=create_task>{\"title\": \"Nova tarefa\", \"priority\": \"high\"}"
        result = parse_text_function_call(text)
        assert result is not None
        assert result['name'] == 'create_task'
        assert "Nova tarefa" in result['arguments']

    def test_parse_arrow_format_mark_done(self):
        """Test parsing mark_done arrow format."""
        text = "=mark_done>{\"task_numbers\": [1, 2, 3]}"
        result = parse_text_function_call(text)
        assert result is not None
        assert result['name'] == 'mark_done'
        assert "[1, 2, 3]" in result['arguments']

    # ========== XML FORMAT PARSING ==========
    def test_parse_xml_format_simple(self):
        """Test parsing simple XML format."""
        text = "<function=view_tasks>{\"filter_status\": \"all\"}</function>"
        result = parse_text_function_call(text)
        assert result is not None
        assert result['name'] == 'view_tasks'
        assert result['arguments'] == "{\"filter_status\": \"all\"}"

    def test_parse_xml_format_in_sentence(self):
        """Test parsing XML format within sentence."""
        text = "Deixe-me fazer isso <function=mark_done>{\"task_numbers\": [1]}</function>"
        result = parse_text_function_call(text)
        assert result is not None
        assert result['name'] == 'mark_done'
        assert "[1]" in result['arguments']

    def test_parse_xml_format_multiline(self):
        """Test parsing XML format with newlines."""
        text = """<function=view_progress>
        {"format": "detailed"}
        </function>"""
        result = parse_text_function_call(text)
        assert result is not None
        assert result['name'] == 'view_progress'

    def test_parse_xml_complex_json(self):
        """Test parsing XML with complex JSON."""
        text = '<function=create_task>{"title": "Test", "nested": {"key": "value"}}</function>'
        result = parse_text_function_call(text)
        assert result is not None
        assert result['name'] == 'create_task'
        assert "nested" in result['arguments']

    # ========== EDGE CASES ==========
    def test_parse_empty_string(self):
        """Test parsing empty string."""
        result = parse_text_function_call("")
        assert result is None

    def test_parse_none(self):
        """Test parsing None."""
        result = parse_text_function_call(None)
        assert result is None

    def test_parse_no_function_call(self):
        """Test parsing text without function call."""
        text = "Olá, como posso ajudar você?"
        result = parse_text_function_call(text)
        assert result is None

    def test_parse_malformed_arrow_format(self):
        """Test parsing malformed arrow format."""
        text = "=view_tasks> missing braces"
        result = parse_text_function_call(text)
        # Should not match due to missing JSON braces
        assert result is None

    def test_parse_incomplete_xml_tag(self):
        """Test parsing incomplete XML tag."""
        text = "<function=view_tasks>{json}</function"
        result = parse_text_function_call(text)
        # Should not match due to incomplete closing tag
        assert result is None

    def test_parse_only_arrow_no_json(self):
        """Test arrow format without JSON."""
        text = "=view_tasks>"
        result = parse_text_function_call(text)
        assert result is None

    # ========== MULTIPLE FUNCTION CALLS ==========
    def test_parse_first_of_multiple_calls(self):
        """Test that first function call is parsed when multiple exist."""
        text = "=view_tasks>{} and =mark_done>{}"
        result = parse_text_function_call(text)
        assert result is not None
        # Should find the first one
        assert result['name'] == 'view_tasks'

    def test_parse_with_surrounding_text(self):
        """Test parsing with lots of surrounding text."""
        text = """Olá! Vou executar sua solicitação.
        Deixe-me fazer isso para você agora.
        =view_tasks>{"filter_status": "pending"}
        Aqui estão suas tarefas!"""
        result = parse_text_function_call(text)
        assert result is not None
        assert result['name'] == 'view_tasks'

    # ========== REAL-WORLD SCENARIOS ==========
    def test_groq_llama_response_parsing(self):
        """Test parsing typical Groq LLaMA response format."""
        text = "Vou listar suas tarefas =view_tasks>{\"filter_status\": \"all\"}"
        result = parse_text_function_call(text)
        assert result is not None
        assert result['name'] == 'view_tasks'
        # Verify we can parse the JSON
        args = json.loads(result['arguments'])
        assert args['filter_status'] == 'all'

    def test_groq_xml_response_parsing(self):
        """Test parsing typical Groq XML response format."""
        text = "Deixe-me marcar como feito <function=mark_done>{\"task_numbers\": [1]}</function> Pronto!"
        result = parse_text_function_call(text)
        assert result is not None
        assert result['name'] == 'mark_done'
        args = json.loads(result['arguments'])
        assert args['task_numbers'] == [1]

    def test_estevao_scenario_function_parsing(self):
        """Test Estevao-specific scenario."""
        text = "Vou criar uma nova tarefa para você =create_task>{\"title\": \"Estudar Python\", \"priority\": \"high\"}"
        result = parse_text_function_call(text)
        assert result is not None
        assert result['name'] == 'create_task'
        args = json.loads(result['arguments'])
        assert args['title'] == 'Estudar Python'
        assert args['priority'] == 'high'

    # ========== WHITESPACE HANDLING ==========
    def test_parse_with_extra_whitespace_in_braces(self):
        """Test parsing with whitespace in JSON."""
        text = "=view_tasks>{ \"filter_status\" : \"all\" }"
        result = parse_text_function_call(text)
        assert result is not None
        # The whitespace in JSON should be preserved
        assert "filter_status" in result['arguments']

    def test_parse_with_newlines_in_json(self):
        """Test parsing with newlines in JSON."""
        text = """=view_tasks>{
            "filter_status": "all"
        }"""
        result = parse_text_function_call(text)
        assert result is not None
        assert result['name'] == 'view_tasks'


class TestFunctionCallParsingIntegration:
    """Integration tests for function call parsing workflow."""

    def test_clean_and_parse_workflow(self):
        """Test the workflow of cleaning and parsing."""
        # Simulate a Groq response
        groq_response = "Vou executar sua tarefa =view_tasks>{\"filter_status\": \"pending\"}"

        # First parse to extract function call
        parsed = parse_text_function_call(groq_response)
        assert parsed is not None

        # Then clean for display
        cleaned = clean_response_text(groq_response)
        assert cleaned == "Vou executar sua tarefa"

    def test_multiple_formats_cleanup(self):
        """Test cleaning response with multiple function formats."""
        response = """Vou fazer o seguinte:
        1. Ver tarefas <view_tasks>
        2. Criar nova =create_task>{"title": "Nova"}
        3. Progresso <function=view_progress></function>
        """
        cleaned = clean_response_text(response)

        # All function markers should be gone
        assert "<" not in cleaned
        assert "=" not in cleaned
        assert "function" not in cleaned

        # But content should remain
        assert "Ver tarefas" in cleaned
        assert "Criar nova" in cleaned

    def test_extract_then_clean_workflow(self):
        """Test extracting function call then cleaning for display."""
        text = "Deixe-me criar isso para você =create_task>{\"title\": \"Implementar login\"}"

        # Extract function
        func = parse_text_function_call(text)
        assert func is not None
        assert func['name'] == 'create_task'

        # Clean for display
        display_text = clean_response_text(text)
        assert display_text == "Deixe-me criar isso para você"

        # User never sees the function syntax
        assert "=" not in display_text
        assert "create_task" not in display_text

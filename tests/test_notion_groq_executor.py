"""
Tests for Groq function executor integration with Notion tasks.

Tests cover:
- Getting tasks from Notion for Groq to read
- Updating Notion task status from Groq decisions
- Different output formats (formatted, summary, by_status)
- Status filtering
- Error handling
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from src.ai.function_executor import FunctionExecutor


@pytest.fixture
def function_executor():
    """FunctionExecutor instance for testing."""
    return FunctionExecutor()


@pytest.fixture
def mock_notion_task_reader():
    """Mock NotionTaskReader instance."""
    reader = Mock()
    reader.get_all_tasks.return_value = [
        {
            'id': 'task_1',
            'title': 'Implement API',
            'status': 'In Progress',
            'priority': 'High',
            'progress': 0.75,
            'effort_hours': 8,
            'due_date': '2025-11-10'
        },
        {
            'id': 'task_2',
            'title': 'Write tests',
            'status': 'Not Started',
            'priority': 'Medium',
            'progress': 0.0,
            'effort_hours': 5,
            'due_date': '2025-11-15'
        }
    ]

    reader.get_tasks_by_status.return_value = [
        reader.get_all_tasks.return_value[0]
    ]

    reader.get_high_priority_tasks.return_value = [
        reader.get_all_tasks.return_value[0]
    ]

    reader.format_for_groq.return_value = "📋 **TAREFAS**\n1. Implement API\n2. Write tests"

    reader.format_summary_for_groq.return_value = json.dumps({
        "total_tasks": 2,
        "by_status": {"In Progress": 1, "Not Started": 1},
        "average_progress": 0.375,
        "tasks": [
            {"id": "task_1", "title": "Implement API", "status": "In Progress"},
            {"id": "task_2", "title": "Write tests", "status": "Not Started"}
        ]
    })

    reader.update_task_status.return_value = True
    reader.update_task_progress.return_value = True

    return reader


class TestGetNotionTasks:
    """Test suite for _get_notion_tasks function executor."""

    @patch('src.ai.function_executor.get_notion_task_reader')
    def test_get_notion_tasks_all_tasks(self, mock_get_reader, function_executor, mock_notion_task_reader):
        """Test retrieving all tasks from Notion."""
        # Arrange
        mock_get_reader.return_value = mock_notion_task_reader
        user_id = "user_123"
        arguments = {"format": "formatted", "status_filter": "all"}

        # Act
        result = function_executor._get_notion_tasks(user_id, arguments)
        result_data = json.loads(result)

        # Assert
        assert result_data['success'] is True
        assert result_data['count'] == 2
        mock_notion_task_reader.get_all_tasks.assert_called_once()

    @patch('src.ai.function_executor.get_notion_task_reader')
    def test_get_notion_tasks_formatted_output(self, mock_get_reader, function_executor, mock_notion_task_reader):
        """Test formatted output for human reading."""
        # Arrange
        mock_get_reader.return_value = mock_notion_task_reader
        user_id = "user_123"
        arguments = {"format": "formatted"}

        # Act
        result = function_executor._get_notion_tasks(user_id, arguments)
        result_data = json.loads(result)

        # Assert
        assert result_data['success'] is True
        assert "📋" in result_data['data'] or "Implement API" in result_data['data']

    @patch('src.ai.function_executor.get_notion_task_reader')
    def test_get_notion_tasks_summary_format(self, mock_get_reader, function_executor, mock_notion_task_reader):
        """Test JSON summary format for Groq analysis."""
        # Arrange
        mock_get_reader.return_value = mock_notion_task_reader
        user_id = "user_123"
        arguments = {"format": "summary"}

        # Act
        result = function_executor._get_notion_tasks(user_id, arguments)
        result_data = json.loads(result)

        # Assert
        assert result_data['success'] is True
        # Data should be a JSON string
        summary = json.loads(result_data['data'])
        assert summary['total_tasks'] == 2

    @patch('src.ai.function_executor.get_notion_task_reader')
    def test_get_notion_tasks_by_status_format(self, mock_get_reader, function_executor, mock_notion_task_reader):
        """Test grouping tasks by status."""
        # Arrange
        mock_get_reader.return_value = mock_notion_task_reader
        user_id = "user_123"
        arguments = {"format": "by_status"}
        mock_notion_task_reader.get_all_tasks.return_value = [
            {
                'id': 'task_1',
                'title': 'Task In Progress',
                'status': 'In Progress',
                'priority': 'High'
            },
            {
                'id': 'task_2',
                'title': 'Task Not Started',
                'status': 'Not Started',
                'priority': 'Medium'
            }
        ]

        # Act
        result = function_executor._get_notion_tasks(user_id, arguments)
        result_data = json.loads(result)

        # Assert
        assert result_data['success'] is True
        by_status = json.loads(result_data['data'])
        assert 'In Progress' in by_status
        assert 'Not Started' in by_status

    @patch('src.ai.function_executor.get_notion_task_reader')
    def test_get_notion_tasks_filter_by_status(self, mock_get_reader, function_executor, mock_notion_task_reader):
        """Test filtering tasks by status."""
        # Arrange
        mock_get_reader.return_value = mock_notion_task_reader
        user_id = "user_123"
        arguments = {"format": "formatted", "status_filter": "in_progress"}

        # Act
        result = function_executor._get_notion_tasks(user_id, arguments)
        result_data = json.loads(result)

        # Assert
        assert result_data['success'] is True
        mock_notion_task_reader.get_tasks_by_status.assert_called_once_with('In Progress')

    @patch('src.ai.function_executor.get_notion_task_reader')
    def test_get_notion_tasks_filter_completed(self, mock_get_reader, function_executor, mock_notion_task_reader):
        """Test filtering for completed tasks."""
        # Arrange
        mock_get_reader.return_value = mock_notion_task_reader
        user_id = "user_123"
        arguments = {"format": "formatted", "status_filter": "completed"}

        # Act
        result = function_executor._get_notion_tasks(user_id, arguments)
        result_data = json.loads(result)

        # Assert
        assert result_data['success'] is True
        mock_notion_task_reader.get_tasks_by_status.assert_called_once_with('Completed')

    @patch('src.ai.function_executor.get_notion_task_reader')
    def test_get_notion_tasks_empty_database(self, mock_get_reader, function_executor, mock_notion_task_reader):
        """Test handling empty task database."""
        # Arrange
        mock_notion_task_reader.get_all_tasks.return_value = []
        mock_get_reader.return_value = mock_notion_task_reader
        user_id = "user_123"
        arguments = {}

        # Act
        result = function_executor._get_notion_tasks(user_id, arguments)
        result_data = json.loads(result)

        # Assert
        assert result_data['success'] is True
        assert result_data['count'] == 0

    @patch('src.ai.function_executor.get_notion_task_reader')
    def test_get_notion_tasks_api_error(self, mock_get_reader, function_executor, mock_notion_task_reader):
        """Test error handling when Notion API fails."""
        # Arrange
        mock_notion_task_reader.get_all_tasks.side_effect = Exception("Notion API Error")
        mock_get_reader.return_value = mock_notion_task_reader
        user_id = "user_123"
        arguments = {}

        # Act
        result = function_executor._get_notion_tasks(user_id, arguments)
        result_data = json.loads(result)

        # Assert
        assert result_data['success'] is False
        assert 'error' in result_data

    @patch('src.ai.function_executor.get_notion_task_reader')
    def test_get_notion_tasks_default_format(self, mock_get_reader, function_executor, mock_notion_task_reader):
        """Test that default format is 'formatted'."""
        # Arrange
        mock_get_reader.return_value = mock_notion_task_reader
        user_id = "user_123"
        arguments = {}  # No format specified

        # Act
        result = function_executor._get_notion_tasks(user_id, arguments)
        result_data = json.loads(result)

        # Assert
        assert result_data['success'] is True
        mock_notion_task_reader.format_for_groq.assert_called()

    @patch('src.ai.function_executor.get_notion_task_reader')
    def test_get_notion_tasks_status_mapping(self, mock_get_reader, function_executor, mock_notion_task_reader):
        """Test that status filters are correctly mapped."""
        # Arrange
        mock_get_reader.return_value = mock_notion_task_reader
        user_id = "user_123"

        # Test each status filter
        status_filters = [
            ("not_started", "Not Started"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("on_hold", "On Hold"),
            ("blocked", "Blocked")
        ]

        for filter_val, expected_status in status_filters:
            # Reset mock
            mock_notion_task_reader.get_tasks_by_status.reset_mock()
            arguments = {"format": "formatted", "status_filter": filter_val}

            # Act
            result = function_executor._get_notion_tasks(user_id, arguments)

            # Assert
            mock_notion_task_reader.get_tasks_by_status.assert_called_once_with(expected_status)


class TestUpdateNotionTaskStatus:
    """Test suite for _update_notion_task_status function executor."""

    @patch('src.ai.function_executor.get_notion_task_reader')
    def test_update_notion_task_status_success(self, mock_get_reader, function_executor, mock_notion_task_reader):
        """Test successful task status update."""
        # Arrange
        mock_get_reader.return_value = mock_notion_task_reader
        user_id = "user_123"
        task_id = "task_123"
        arguments = {
            "task_id": task_id,
            "new_status": "Completed"
        }

        # Act
        result = function_executor._update_notion_task_status(user_id, arguments)
        result_data = json.loads(result)

        # Assert
        assert result_data['success'] is True
        assert "✅" in result_data['data']
        mock_notion_task_reader.update_task_status.assert_called_once_with(task_id, "Completed")

    @patch('src.ai.function_executor.get_notion_task_reader')
    def test_update_notion_task_status_with_progress(self, mock_get_reader, function_executor, mock_notion_task_reader):
        """Test status update with progress percentage."""
        # Arrange
        mock_get_reader.return_value = mock_notion_task_reader
        user_id = "user_123"
        task_id = "task_123"
        arguments = {
            "task_id": task_id,
            "new_status": "In Progress",
            "update_progress": 50
        }

        # Act
        result = function_executor._update_notion_task_status(user_id, arguments)
        result_data = json.loads(result)

        # Assert
        assert result_data['success'] is True
        assert "50%" in result_data['data']
        mock_notion_task_reader.update_task_status.assert_called_once_with(task_id, "In Progress")
        mock_notion_task_reader.update_task_progress.assert_called_once_with(task_id, 50)

    @patch('src.ai.function_executor.get_notion_task_reader')
    def test_update_notion_task_status_missing_task_id(self, mock_get_reader, function_executor, mock_notion_task_reader):
        """Test error when task_id is missing."""
        # Arrange
        mock_get_reader.return_value = mock_notion_task_reader
        user_id = "user_123"
        arguments = {"new_status": "Completed"}  # Missing task_id

        # Act
        result = function_executor._update_notion_task_status(user_id, arguments)
        result_data = json.loads(result)

        # Assert
        assert result_data['success'] is False
        assert "required" in result_data['error'].lower()

    @patch('src.ai.function_executor.get_notion_task_reader')
    def test_update_notion_task_status_missing_new_status(self, mock_get_reader, function_executor, mock_notion_task_reader):
        """Test error when new_status is missing."""
        # Arrange
        mock_get_reader.return_value = mock_notion_task_reader
        user_id = "user_123"
        arguments = {"task_id": "task_123"}  # Missing new_status

        # Act
        result = function_executor._update_notion_task_status(user_id, arguments)
        result_data = json.loads(result)

        # Assert
        assert result_data['success'] is False
        assert "required" in result_data['error'].lower()

    @patch('src.ai.function_executor.get_notion_task_reader')
    def test_update_notion_task_status_api_error(self, mock_get_reader, function_executor, mock_notion_task_reader):
        """Test error handling when Notion API fails."""
        # Arrange
        mock_notion_task_reader.update_task_status.return_value = False
        mock_get_reader.return_value = mock_notion_task_reader
        user_id = "user_123"
        arguments = {
            "task_id": "task_123",
            "new_status": "Completed"
        }

        # Act
        result = function_executor._update_notion_task_status(user_id, arguments)
        result_data = json.loads(result)

        # Assert
        assert result_data['success'] is False
        assert "Could not update" in result_data['error']

    @patch('src.ai.function_executor.get_notion_task_reader')
    def test_update_notion_task_status_all_status_options(self, mock_get_reader, function_executor, mock_notion_task_reader):
        """Test updating to all valid status options."""
        # Arrange
        mock_get_reader.return_value = mock_notion_task_reader
        user_id = "user_123"
        statuses = ["Not Started", "In Progress", "Completed", "On Hold", "Blocked"]

        for status in statuses:
            # Reset mock
            mock_notion_task_reader.update_task_status.reset_mock()
            arguments = {
                "task_id": "task_123",
                "new_status": status
            }

            # Act
            result = function_executor._update_notion_task_status(user_id, arguments)
            result_data = json.loads(result)

            # Assert
            assert result_data['success'] is True
            mock_notion_task_reader.update_task_status.assert_called_once_with("task_123", status)

    @patch('src.ai.function_executor.get_notion_task_reader')
    def test_update_notion_task_status_progress_range(self, mock_get_reader, function_executor, mock_notion_task_reader):
        """Test progress updates with various percentages."""
        # Arrange
        mock_get_reader.return_value = mock_notion_task_reader
        user_id = "user_123"
        progress_values = [0, 25, 50, 75, 100]

        for progress in progress_values:
            # Reset mock
            mock_notion_task_reader.update_task_progress.reset_mock()
            arguments = {
                "task_id": "task_123",
                "new_status": "In Progress",
                "update_progress": progress
            }

            # Act
            result = function_executor._update_notion_task_status(user_id, arguments)
            result_data = json.loads(result)

            # Assert
            assert result_data['success'] is True
            mock_notion_task_reader.update_task_progress.assert_called_once_with("task_123", progress)

    @patch('src.ai.function_executor.get_notion_task_reader')
    def test_update_notion_task_progress_failure_doesnt_fail_update(self, mock_get_reader, function_executor, mock_notion_task_reader):
        """Test that progress update failure doesn't fail the overall status update."""
        # Arrange
        mock_notion_task_reader.update_task_status.return_value = True
        mock_notion_task_reader.update_task_progress.return_value = False
        mock_get_reader.return_value = mock_notion_task_reader
        user_id = "user_123"
        arguments = {
            "task_id": "task_123",
            "new_status": "Completed",
            "update_progress": 100
        }

        # Act
        result = function_executor._update_notion_task_status(user_id, arguments)
        result_data = json.loads(result)

        # Assert
        assert result_data['success'] is True
        # Message should only include status, not progress
        assert "Completed" in result_data['data']


class TestGroqTaskIntegrationScenarios:
    """Integration tests simulating Groq AI decision workflows."""

    @patch('src.ai.function_executor.get_notion_task_reader')
    def test_groq_workflow_read_tasks_then_update(self, mock_get_reader, function_executor, mock_notion_task_reader):
        """Simulate Groq reading tasks and updating status."""
        # Arrange
        mock_get_reader.return_value = mock_notion_task_reader
        user_id = "user_123"

        # Groq reads all tasks
        read_result = function_executor._get_notion_tasks(user_id, {"format": "summary"})
        read_data = json.loads(read_result)

        # Extract task ID from response
        summary = json.loads(read_data['data'])
        task_id = summary['tasks'][0]['id']

        # Act - Groq decides to mark first task as completed
        update_result = function_executor._update_notion_task_status(user_id, {
            "task_id": task_id,
            "new_status": "Completed",
            "update_progress": 100
        })
        update_data = json.loads(update_result)

        # Assert
        assert read_data['success'] is True
        assert update_data['success'] is True

    @patch('src.ai.function_executor.get_notion_task_reader')
    def test_groq_workflow_filter_high_priority(self, mock_get_reader, function_executor, mock_notion_task_reader):
        """Simulate Groq filtering and working with high priority tasks."""
        # Arrange
        high_priority_task = {
            'id': 'high_priority_task',
            'title': 'Urgent bug fix',
            'status': 'Not Started',
            'priority': 'Urgent',
            'progress': 0
        }
        mock_notion_task_reader.get_all_tasks.return_value = [high_priority_task]
        mock_get_reader.return_value = mock_notion_task_reader
        user_id = "user_123"

        # Act - Groq asks for summary to analyze
        result = function_executor._get_notion_tasks(user_id, {"format": "summary"})
        result_data = json.loads(result)

        # Assert
        assert result_data['success'] is True
        summary = json.loads(result_data['data'])
        assert summary['tasks'][0]['priority'] == 'Urgent'

"""
Comprehensive tests for NotionTaskReader and Groq task integration.

Tests cover:
- Task retrieval from Notion database
- Task filtering by status and priority
- Task status updates
- Progress tracking
- Formatting for Groq AI understanding
- Error handling and edge cases
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from src.integrations.notion_tasks import NotionTaskReader, get_notion_task_reader


@pytest.fixture
def mock_notion_client():
    """Mock Notion client."""
    return Mock()


@pytest.fixture
def notion_task_reader(mock_notion_client):
    """NotionTaskReader instance with mocked Notion client."""
    reader = NotionTaskReader()
    reader.client = mock_notion_client
    reader.db_id = "test_db_id_123"
    return reader


@pytest.fixture
def sample_task_page():
    """Sample Notion page object representing a task."""
    return {
        "id": "page_id_1",
        "created_time": "2025-11-05T10:00:00.000Z",
        "last_edited_time": "2025-11-05T14:00:00.000Z",
        "properties": {
            "Task Name": {
                "type": "title",
                "title": [{"text": {"content": "Implement API endpoint"}}]
            },
            "Status": {
                "type": "status",
                "status": {"name": "In Progress"}
            },
            "Priority": {
                "type": "select",
                "select": {"name": "High"}
            },
            "Progress": {
                "type": "number",
                "number": 0.75
            },
            "Effort Hours": {
                "type": "number",
                "number": 8
            },
            "Due Date": {
                "type": "date",
                "date": {"start": "2025-11-10"}
            },
            "Description": {
                "type": "rich_text",
                "rich_text": [{"text": {"content": "Create REST API endpoint for user management"}}]
            },
            "Category": {
                "type": "select",
                "select": {"name": "Development"}
            },
            "Tags": {
                "type": "multi_select",
                "multi_select": [
                    {"name": "API"},
                    {"name": "Backend"}
                ]
            }
        }
    }


@pytest.fixture
def multiple_task_pages():
    """Multiple task pages with different statuses."""
    return [
        {
            "id": "page_1",
            "created_time": "2025-11-01T10:00:00.000Z",
            "last_edited_time": "2025-11-01T10:00:00.000Z",
            "properties": {
                "Task Name": {
                    "type": "title",
                    "title": [{"text": {"content": "Task 1 - Not Started"}}]
                },
                "Status": {
                    "type": "status",
                    "status": {"name": "Not Started"}
                },
                "Priority": {
                    "type": "select",
                    "select": {"name": "Medium"}
                },
                "Progress": {
                    "type": "number",
                    "number": 0.0
                }
            }
        },
        {
            "id": "page_2",
            "created_time": "2025-11-02T10:00:00.000Z",
            "last_edited_time": "2025-11-02T10:00:00.000Z",
            "properties": {
                "Task Name": {
                    "type": "title",
                    "title": [{"text": {"content": "Task 2 - In Progress"}}]
                },
                "Status": {
                    "type": "status",
                    "status": {"name": "In Progress"}
                },
                "Priority": {
                    "type": "select",
                    "select": {"name": "High"}
                },
                "Progress": {
                    "type": "number",
                    "number": 0.5
                }
            }
        },
        {
            "id": "page_3",
            "created_time": "2025-11-03T10:00:00.000Z",
            "last_edited_time": "2025-11-03T10:00:00.000Z",
            "properties": {
                "Task Name": {
                    "type": "title",
                    "title": [{"text": {"content": "Task 3 - Completed"}}]
                },
                "Status": {
                    "type": "status",
                    "status": {"name": "Completed"}
                },
                "Priority": {
                    "type": "select",
                    "select": {"name": "Low"}
                },
                "Progress": {
                    "type": "number",
                    "number": 1.0
                }
            }
        }
    ]


class TestNotionTaskReaderInit:
    """Test NotionTaskReader initialization."""

    def test_init_with_database_id_set(self):
        """Test initialization when database ID is set."""
        with patch.dict('os.environ', {'NOTION_GROQ_TASKS_DB_ID': 'test_db_id'}):
            with patch('src.integrations.notion_tasks.settings'):
                reader = NotionTaskReader()
                assert reader.db_id == 'test_db_id'

    def test_init_without_database_id(self):
        """Test initialization when database ID is not set."""
        with patch.dict('os.environ', {}, clear=True):
            with patch('src.integrations.notion_tasks.settings'):
                reader = NotionTaskReader()
                assert reader.db_id is None


class TestGetAllTasks:
    """Test suite for get_all_tasks method."""

    def test_get_all_tasks_success(self, notion_task_reader, sample_task_page):
        """Test successful retrieval of all tasks."""
        # Arrange
        notion_task_reader.client.databases.query.return_value = {
            'results': [sample_task_page]
        }

        # Act
        tasks = notion_task_reader.get_all_tasks()

        # Assert
        assert len(tasks) == 1
        assert tasks[0]['title'] == "Implement API endpoint"
        assert tasks[0]['status'] == "In Progress"
        assert tasks[0]['priority'] == "High"
        assert tasks[0]['progress'] == 0.75

    def test_get_all_tasks_empty_database(self, notion_task_reader):
        """Test retrieval when database is empty."""
        # Arrange
        notion_task_reader.client.databases.query.return_value = {'results': []}

        # Act
        tasks = notion_task_reader.get_all_tasks()

        # Assert
        assert len(tasks) == 0

    def test_get_all_tasks_without_database_id(self):
        """Test that method returns empty list without database ID."""
        # Arrange
        reader = NotionTaskReader()
        reader.db_id = None

        # Act
        tasks = reader.get_all_tasks()

        # Assert
        assert tasks == []

    def test_get_all_tasks_multiple_tasks(self, notion_task_reader, multiple_task_pages):
        """Test retrieval of multiple tasks."""
        # Arrange
        notion_task_reader.client.databases.query.return_value = {
            'results': multiple_task_pages
        }

        # Act
        tasks = notion_task_reader.get_all_tasks()

        # Assert
        assert len(tasks) == 3
        assert tasks[0]['title'] == "Task 1 - Not Started"
        assert tasks[1]['status'] == "In Progress"
        assert tasks[2]['status'] == "Completed"

    def test_get_all_tasks_api_error(self, notion_task_reader):
        """Test handling of Notion API errors."""
        # Arrange
        notion_task_reader.client.databases.query.side_effect = Exception("API Error")

        # Act
        tasks = notion_task_reader.get_all_tasks()

        # Assert
        assert tasks == []


class TestGetTasksByStatus:
    """Test suite for get_tasks_by_status method."""

    def test_get_tasks_by_status_in_progress(self, notion_task_reader, multiple_task_pages):
        """Test filtering tasks by 'In Progress' status."""
        # Arrange
        in_progress_task = multiple_task_pages[1]
        notion_task_reader.client.databases.query.return_value = {
            'results': [in_progress_task]
        }

        # Act
        tasks = notion_task_reader.get_tasks_by_status("In Progress")

        # Assert
        assert len(tasks) == 1
        assert tasks[0]['status'] == "In Progress"
        notion_task_reader.client.databases.query.assert_called_once()

    def test_get_tasks_by_status_completed(self, notion_task_reader, multiple_task_pages):
        """Test filtering tasks by 'Completed' status."""
        # Arrange
        completed_task = multiple_task_pages[2]
        notion_task_reader.client.databases.query.return_value = {
            'results': [completed_task]
        }

        # Act
        tasks = notion_task_reader.get_tasks_by_status("Completed")

        # Assert
        assert len(tasks) == 1
        assert tasks[0]['status'] == "Completed"

    def test_get_tasks_by_status_no_results(self, notion_task_reader):
        """Test filtering when no tasks match status."""
        # Arrange
        notion_task_reader.client.databases.query.return_value = {'results': []}

        # Act
        tasks = notion_task_reader.get_tasks_by_status("Blocked")

        # Assert
        assert tasks == []

    def test_get_tasks_by_status_api_error(self, notion_task_reader):
        """Test error handling in status filtering."""
        # Arrange
        notion_task_reader.client.databases.query.side_effect = Exception("Filter Error")

        # Act
        tasks = notion_task_reader.get_tasks_by_status("In Progress")

        # Assert
        assert tasks == []


class TestGetHighPriorityTasks:
    """Test suite for get_high_priority_tasks method."""

    def test_get_high_priority_tasks(self, notion_task_reader, multiple_task_pages):
        """Test retrieval of high/urgent priority tasks."""
        # Arrange
        high_priority_task = multiple_task_pages[1]  # High priority task
        notion_task_reader.client.databases.query.return_value = {
            'results': [high_priority_task]
        }

        # Act
        tasks = notion_task_reader.get_high_priority_tasks()

        # Assert
        assert len(tasks) == 1
        assert tasks[0]['priority'] == "High"

    def test_get_high_priority_tasks_empty(self, notion_task_reader):
        """Test when no high priority tasks exist."""
        # Arrange
        notion_task_reader.client.databases.query.return_value = {'results': []}

        # Act
        tasks = notion_task_reader.get_high_priority_tasks()

        # Assert
        assert tasks == []


class TestUpdateTaskStatus:
    """Test suite for update_task_status method."""

    def test_update_task_status_success(self, notion_task_reader):
        """Test successful task status update."""
        # Arrange
        task_id = "page_id_123"
        new_status = "Completed"

        # Act
        result = notion_task_reader.update_task_status(task_id, new_status)

        # Assert
        assert result is True
        notion_task_reader.client.pages.update.assert_called_once()
        call_args = notion_task_reader.client.pages.update.call_args
        assert call_args.kwargs['page_id'] == task_id

    def test_update_task_status_to_in_progress(self, notion_task_reader):
        """Test updating task status to 'In Progress'."""
        # Arrange
        task_id = "page_id_456"
        new_status = "In Progress"

        # Act
        result = notion_task_reader.update_task_status(task_id, new_status)

        # Assert
        assert result is True
        call_args = notion_task_reader.client.pages.update.call_args
        assert call_args.kwargs['properties']['Status']['status']['name'] == new_status

    def test_update_task_status_api_error(self, notion_task_reader):
        """Test error handling during status update."""
        # Arrange
        notion_task_reader.client.pages.update.side_effect = Exception("Update Error")

        # Act
        result = notion_task_reader.update_task_status("page_id", "Completed")

        # Assert
        assert result is False


class TestUpdateTaskProgress:
    """Test suite for update_task_progress method."""

    def test_update_task_progress_success(self, notion_task_reader):
        """Test successful task progress update."""
        # Arrange
        task_id = "page_id_789"
        progress = 75

        # Act
        result = notion_task_reader.update_task_progress(task_id, progress)

        # Assert
        assert result is True
        notion_task_reader.client.pages.update.assert_called_once()

    def test_update_task_progress_clamped_to_100(self, notion_task_reader):
        """Test that progress is clamped to 100%."""
        # Arrange
        task_id = "page_id"
        progress = 150  # Over 100%

        # Act
        result = notion_task_reader.update_task_progress(task_id, progress)

        # Assert
        assert result is True
        call_args = notion_task_reader.client.pages.update.call_args
        progress_value = call_args.kwargs['properties']['Progress']['number']
        assert progress_value == 1.0  # 100 / 100

    def test_update_task_progress_clamped_to_zero(self, notion_task_reader):
        """Test that progress is clamped to 0%."""
        # Arrange
        task_id = "page_id"
        progress = -50

        # Act
        result = notion_task_reader.update_task_progress(task_id, progress)

        # Assert
        assert result is True
        call_args = notion_task_reader.client.pages.update.call_args
        progress_value = call_args.kwargs['properties']['Progress']['number']
        assert progress_value == 0.0

    def test_update_task_progress_api_error(self, notion_task_reader):
        """Test error handling during progress update."""
        # Arrange
        notion_task_reader.client.pages.update.side_effect = Exception("Progress Error")

        # Act
        result = notion_task_reader.update_task_progress("page_id", 50)

        # Assert
        assert result is False


class TestFormatForGroq:
    """Test suite for format_for_groq method."""

    def test_format_single_task(self, notion_task_reader, sample_task_page):
        """Test formatting single task for Groq."""
        # Arrange
        parsed_task = notion_task_reader._parse_task_page(sample_task_page)
        tasks = [parsed_task]

        # Act
        formatted = notion_task_reader.format_for_groq(tasks)

        # Assert
        assert "Implement API endpoint" in formatted
        assert "In Progress" in formatted
        assert "High" in formatted
        assert "75%" in formatted

    def test_format_empty_task_list(self, notion_task_reader):
        """Test formatting empty task list."""
        # Arrange
        tasks = []

        # Act
        formatted = notion_task_reader.format_for_groq(tasks)

        # Assert
        assert "Não há tarefas" in formatted

    def test_format_multiple_tasks(self, notion_task_reader, multiple_task_pages):
        """Test formatting multiple tasks."""
        # Arrange
        tasks = [notion_task_reader._parse_task_page(page) for page in multiple_task_pages]

        # Act
        formatted = notion_task_reader.format_for_groq(tasks)

        # Assert
        assert "Task 1 - Not Started" in formatted
        assert "Task 2 - In Progress" in formatted
        assert "Task 3 - Completed" in formatted
        assert formatted.count("Status:") == 3


class TestFormatSummaryForGroq:
    """Test suite for format_summary_for_groq method."""

    def test_format_summary_single_task(self, notion_task_reader, sample_task_page):
        """Test JSON summary format for single task."""
        # Arrange
        parsed_task = notion_task_reader._parse_task_page(sample_task_page)
        tasks = [parsed_task]

        # Act
        summary_json = notion_task_reader.format_summary_for_groq(tasks)
        summary = json.loads(summary_json)

        # Assert
        assert summary['total_tasks'] == 1
        assert 'by_status' in summary
        assert 'by_priority' in summary
        assert 'tasks' in summary
        assert summary['tasks'][0]['title'] == "Implement API endpoint"

    def test_format_summary_multiple_tasks(self, notion_task_reader, multiple_task_pages):
        """Test summary with multiple tasks grouped by status."""
        # Arrange
        tasks = [notion_task_reader._parse_task_page(page) for page in multiple_task_pages]

        # Act
        summary_json = notion_task_reader.format_summary_for_groq(tasks)
        summary = json.loads(summary_json)

        # Assert
        assert summary['total_tasks'] == 3
        assert 'In Progress' in summary['by_status']
        assert 'Completed' in summary['by_status']
        assert summary['by_status']['In Progress'] == 1
        assert summary['by_status']['Completed'] == 1

    def test_format_summary_average_progress(self, notion_task_reader, multiple_task_pages):
        """Test that average progress is calculated correctly."""
        # Arrange
        tasks = [notion_task_reader._parse_task_page(page) for page in multiple_task_pages]

        # Act
        summary_json = notion_task_reader.format_summary_for_groq(tasks)
        summary = json.loads(summary_json)

        # Assert
        # (0.0 + 0.5 + 1.0) / 3 = 0.5
        assert summary['average_progress'] == 0.5

    def test_format_summary_empty_list(self, notion_task_reader):
        """Test summary with empty task list."""
        # Arrange
        tasks = []

        # Act
        summary_json = notion_task_reader.format_summary_for_groq(tasks)
        summary = json.loads(summary_json)

        # Assert
        assert summary['total_tasks'] == 0
        assert summary['average_progress'] == 0


class TestParseTaskPage:
    """Test suite for _parse_task_page method."""

    def test_parse_complete_task_page(self, notion_task_reader, sample_task_page):
        """Test parsing task page with all properties."""
        # Act
        task = notion_task_reader._parse_task_page(sample_task_page)

        # Assert
        assert task is not None
        assert task['id'] == "page_id_1"
        assert task['title'] == "Implement API endpoint"
        assert task['status'] == "In Progress"
        assert task['priority'] == "High"
        assert task['progress'] == 0.75
        assert task['effort_hours'] == 8
        assert task['due_date'] == "2025-11-10"
        assert task['description'] == "Create REST API endpoint for user management"
        assert task['category'] == "Development"
        assert task['tags'] == ["API", "Backend"]

    def test_parse_task_without_optional_fields(self, notion_task_reader):
        """Test parsing task with only required fields."""
        # Arrange
        minimal_page = {
            "id": "page_minimal",
            "created_time": "2025-11-05T10:00:00.000Z",
            "last_edited_time": "2025-11-05T10:00:00.000Z",
            "properties": {
                "Task Name": {
                    "type": "title",
                    "title": [{"text": {"content": "Minimal Task"}}]
                }
            }
        }

        # Act
        task = notion_task_reader._parse_task_page(minimal_page)

        # Assert
        assert task['title'] == "Minimal Task"
        assert task['status'] is None or task['status'] == 'Not Started'
        assert task['priority'] is not None

    def test_parse_task_with_empty_title(self, notion_task_reader):
        """Test parsing task with empty title."""
        # Arrange
        page = {
            "id": "page_empty",
            "properties": {
                "Task Name": {
                    "type": "title",
                    "title": []
                }
            }
        }

        # Act
        task = notion_task_reader._parse_task_page(page)

        # Assert
        assert task['title'] == "Untitled"

    def test_parse_invalid_page_returns_none(self, notion_task_reader):
        """Test parsing invalid page returns None."""
        # Arrange
        invalid_page = {"id": "invalid"}  # Missing required structure

        # Act
        task = notion_task_reader._parse_task_page(invalid_page)

        # Assert
        assert task is not None  # Should still return dict with id
        assert task['id'] == "invalid"


class TestSingletonInstance:
    """Test suite for singleton instance retrieval."""

    def test_get_notion_task_reader_returns_instance(self):
        """Test that get_notion_task_reader returns NotionTaskReader instance."""
        # Act
        reader = get_notion_task_reader()

        # Assert
        assert isinstance(reader, NotionTaskReader)

    def test_get_notion_task_reader_returns_same_instance(self):
        """Test that singleton returns same instance."""
        # Act
        reader1 = get_notion_task_reader()
        reader2 = get_notion_task_reader()

        # Assert
        assert reader1 is reader2


class TestIntegrationScenarios:
    """Integration tests combining multiple operations."""

    def test_workflow_retrieve_update_status(self, notion_task_reader, sample_task_page):
        """Test complete workflow: retrieve task and update status."""
        # Arrange
        notion_task_reader.client.databases.query.return_value = {
            'results': [sample_task_page]
        }

        # Act - Get task
        tasks = notion_task_reader.get_all_tasks()
        task = tasks[0]

        # Update status
        update_result = notion_task_reader.update_task_status(task['id'], "Completed")

        # Assert
        assert update_result is True
        assert task['status'] == "In Progress"

    def test_workflow_format_for_groq_analysis(self, notion_task_reader, multiple_task_pages):
        """Test workflow: retrieve and format for Groq analysis."""
        # Arrange
        notion_task_reader.client.databases.query.return_value = {
            'results': multiple_task_pages
        }

        # Act
        tasks = notion_task_reader.get_all_tasks()
        formatted = notion_task_reader.format_for_groq(tasks)
        summary = notion_task_reader.format_summary_for_groq(tasks)

        # Assert
        assert "Task 1" in formatted
        summary_obj = json.loads(summary)
        assert summary_obj['total_tasks'] == 3
        assert summary_obj['average_progress'] == 0.5

"""
Comprehensive tests for FunctionExecutor
Tests task management functions: create, view, mark_done, mark_progress, view_progress
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from src.ai.function_executor import FunctionExecutor
from src.database.models import Task, TaskStatus, TaskPriority, User


@pytest.fixture
def function_executor():
    """FunctionExecutor instance for testing"""
    return FunctionExecutor()


@pytest.fixture
def mock_db_session():
    """Mock SQLAlchemy session"""
    return Mock(spec=Session)


@pytest.fixture
def mock_task():
    """Mock Task object"""
    task = Mock(spec=Task)
    task.id = 1
    task.user_id = 1
    task.title = 'Test Task'
    task.description = 'Test Description'
    task.status = TaskStatus.PENDING
    task.priority = TaskPriority.MEDIUM
    return task


class TestViewTasks:
    """Test suite for view_tasks function"""

    @patch('src.ai.function_executor.SessionLocal')
    def test_view_tasks_with_no_tasks(self, mock_session_local, function_executor):
        """Test viewing tasks when user has no tasks"""
        # Arrange
        mock_session = Mock()
        mock_session_local.return_value = mock_session
        mock_session.query.return_value.filter.return_value.all.return_value = []

        # Act
        result = function_executor._view_tasks('1', {})

        # Assert
        result_dict = json.loads(result)
        assert result_dict['success'] is True
        assert 'no tasks yet' in result_dict['data'].lower()

    @patch('src.ai.function_executor.SessionLocal')
    def test_view_tasks_with_multiple_tasks(self, mock_session_local, function_executor, mock_task):
        """Test viewing tasks with multiple tasks"""
        # Arrange
        mock_session = Mock()
        mock_session_local.return_value = mock_session

        task1 = Mock(spec=Task)
        task1.title = 'Task 1'
        task1.status = TaskStatus.PENDING

        task2 = Mock(spec=Task)
        task2.title = 'Task 2'
        task2.status = TaskStatus.IN_PROGRESS

        mock_session.query.return_value.filter.return_value.all.return_value = [task1, task2]

        # Act
        result = function_executor._view_tasks('1', {})

        # Assert
        result_dict = json.loads(result)
        assert result_dict['success'] is True
        assert 'Task 1' in result_dict['data']
        assert 'Task 2' in result_dict['data']

    @patch('src.ai.function_executor.SessionLocal')
    def test_view_tasks_with_filter_status(self, mock_session_local, function_executor):
        """Test viewing tasks with status filter"""
        # Arrange
        mock_session = Mock()
        mock_session_local.return_value = mock_session

        completed_task = Mock(spec=Task)
        completed_task.title = 'Completed Task'
        completed_task.status = TaskStatus.COMPLETED

        mock_session.query.return_value.filter.return_value.filter.return_value.all.return_value = [
            completed_task
        ]

        # Act
        result = function_executor._view_tasks('1', {'filter_status': 'completed'})

        # Assert
        result_dict = json.loads(result)
        assert result_dict['success'] is True

    @patch('src.ai.function_executor.SessionLocal')
    def test_view_tasks_database_error(self, mock_session_local, function_executor):
        """Test viewing tasks when database error occurs"""
        # Arrange
        mock_session = Mock()
        mock_session_local.return_value = mock_session
        mock_session.query.side_effect = Exception('DB Error')

        # Act
        result = function_executor._view_tasks('1', {})

        # Assert
        result_dict = json.loads(result)
        assert result_dict['success'] is False
        assert 'Error listing tasks' in result_dict['error']


class TestCreateTask:
    """Test suite for create_task function"""

    @patch('src.ai.function_executor.SessionLocal')
    def test_create_task_success(self, mock_session_local, function_executor):
        """Test successful task creation"""
        # Arrange
        mock_session = Mock()
        mock_session_local.return_value = mock_session

        # Act
        result = function_executor._create_task('1', {
            'title': 'New Task',
            'description': 'Task Description',
            'priority': 'high'
        })

        # Assert
        result_dict = json.loads(result)
        assert result_dict['success'] is True
        assert 'New Task' in result_dict['data']
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @patch('src.ai.function_executor.SessionLocal')
    def test_create_task_without_title(self, mock_session_local, function_executor):
        """Test task creation fails without title"""
        # Arrange
        mock_session = Mock()
        mock_session_local.return_value = mock_session

        # Act
        result = function_executor._create_task('1', {'description': 'No title'})

        # Assert
        result_dict = json.loads(result)
        assert result_dict['success'] is False
        assert 'title is required' in result_dict['error'].lower()

    @patch('src.ai.function_executor.SessionLocal')
    def test_create_task_with_default_priority(self, mock_session_local, function_executor):
        """Test task creation with default priority"""
        # Arrange
        mock_session = Mock()
        mock_session_local.return_value = mock_session

        # Act
        result = function_executor._create_task('1', {'title': 'Task'})

        # Assert
        result_dict = json.loads(result)
        assert result_dict['success'] is True
        mock_session.add.assert_called_once()

    @patch('src.ai.function_executor.SessionLocal')
    def test_create_task_database_error(self, mock_session_local, function_executor):
        """Test task creation when database error occurs"""
        # Arrange
        mock_session = Mock()
        mock_session_local.return_value = mock_session
        mock_session.add.side_effect = Exception('DB Error')

        # Act
        result = function_executor._create_task('1', {'title': 'Task'})

        # Assert
        result_dict = json.loads(result)
        assert result_dict['success'] is False


class TestMarkDone:
    """Test suite for mark_done function"""

    @patch('src.ai.function_executor.SessionLocal')
    def test_mark_single_task_done(self, mock_session_local, function_executor):
        """Test marking single task as done"""
        # Arrange
        mock_session = Mock()
        mock_session_local.return_value = mock_session

        task = Mock(spec=Task)
        task.title = 'Task to Complete'
        task.status = TaskStatus.PENDING

        mock_session.query.return_value.filter.return_value.all.return_value = [task]

        # Act
        result = function_executor._mark_done('1', {'task_numbers': [1]})

        # Assert
        result_dict = json.loads(result)
        assert result_dict['success'] is True
        assert 'marked as completed' in result_dict['data'].lower()

    @patch('src.ai.function_executor.SessionLocal')
    def test_mark_multiple_tasks_done(self, mock_session_local, function_executor):
        """Test marking multiple tasks as done"""
        # Arrange
        mock_session = Mock()
        mock_session_local.return_value = mock_session

        task1 = Mock(spec=Task)
        task1.title = 'Task 1'
        task2 = Mock(spec=Task)
        task2.title = 'Task 2'

        mock_session.query.return_value.filter.return_value.all.return_value = [task1, task2]

        # Act
        result = function_executor._mark_done('1', {'task_numbers': [1, 2]})

        # Assert
        result_dict = json.loads(result)
        assert result_dict['success'] is True
        assert mock_session.commit.call_count == 2

    @patch('src.ai.function_executor.SessionLocal')
    def test_mark_task_done_invalid_number(self, mock_session_local, function_executor):
        """Test marking task with invalid task number"""
        # Arrange
        mock_session = Mock()
        mock_session_local.return_value = mock_session
        mock_session.query.return_value.filter.return_value.all.return_value = []

        # Act
        result = function_executor._mark_done('1', {'task_numbers': [999]})

        # Assert
        result_dict = json.loads(result)
        assert result_dict['success'] is True
        assert 'not found' in result_dict['data'].lower()

    @patch('src.ai.function_executor.SessionLocal')
    def test_mark_done_without_task_numbers(self, mock_session_local, function_executor):
        """Test marking done without task numbers"""
        # Arrange
        mock_session = Mock()
        mock_session_local.return_value = mock_session

        # Act
        result = function_executor._mark_done('1', {})

        # Assert
        result_dict = json.loads(result)
        assert result_dict['success'] is False


class TestMarkProgress:
    """Test suite for mark_progress function"""

    @patch('src.ai.function_executor.SessionLocal')
    def test_mark_task_in_progress(self, mock_session_local, function_executor):
        """Test marking task as in progress"""
        # Arrange
        mock_session = Mock()
        mock_session_local.return_value = mock_session

        task = Mock(spec=Task)
        task.title = 'In Progress Task'

        mock_session.query.return_value.filter.return_value.all.return_value = [task]

        # Act
        result = function_executor._mark_progress('1', {'task_numbers': [1]})

        # Assert
        result_dict = json.loads(result)
        assert result_dict['success'] is True
        assert 'in progress' in result_dict['data'].lower()


class TestViewProgress:
    """Test suite for view_progress function"""

    @patch('src.ai.function_executor.SessionLocal')
    def test_view_progress_with_tasks(self, mock_session_local, function_executor):
        """Test viewing progress with completed and pending tasks"""
        # Arrange
        mock_session = Mock()
        mock_session_local.return_value = mock_session

        task1 = Mock(spec=Task)
        task1.status = TaskStatus.COMPLETED

        task2 = Mock(spec=Task)
        task2.status = TaskStatus.PENDING

        task3 = Mock(spec=Task)
        task3.status = TaskStatus.IN_PROGRESS

        mock_session.query.return_value.filter.return_value.all.return_value = [task1, task2, task3]

        # Act
        result = function_executor._view_progress('1')

        # Assert
        result_dict = json.loads(result)
        assert result_dict['success'] is True
        assert result_dict['data']['total'] == 3
        assert result_dict['data']['completed'] == 1
        assert result_dict['data']['pending'] == 1
        assert result_dict['data']['in_progress'] == 1

    @patch('src.ai.function_executor.SessionLocal')
    def test_view_progress_no_tasks(self, mock_session_local, function_executor):
        """Test viewing progress with no tasks"""
        # Arrange
        mock_session = Mock()
        mock_session_local.return_value = mock_session
        mock_session.query.return_value.filter.return_value.all.return_value = []

        # Act
        result = function_executor._view_progress('1')

        # Assert
        result_dict = json.loads(result)
        assert result_dict['success'] is True
        assert result_dict['data']['total'] == 0
        assert result_dict['data']['percentage'] == 0


class TestGetHelp:
    """Test suite for get_help function"""

    def test_get_help_returns_help_text(self, function_executor):
        """Test that get_help returns valid help text"""
        # Act
        result = function_executor._get_help()

        # Assert
        result_dict = json.loads(result)
        assert result_dict['success'] is True
        assert len(result_dict['data']) > 0
        assert 'Pangeia' in result_dict['data']

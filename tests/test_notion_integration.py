"""
Comprehensive tests for Notion integration (NotionUserManager)
Tests user profile sync, onboarding tracking, and data retrieval
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.integrations.notion_users import NotionUserManager
from src.database.models import User


@pytest.fixture
def mock_notion_client():
    """Mock Notion API client"""
    return Mock()


@pytest.fixture
def notion_manager(mock_notion_client):
    """NotionUserManager instance with mocked Notion client"""
    with patch('src.integrations.notion_users.Client', return_value=mock_notion_client):
        with patch.dict('os.environ', {
            'NOTION_USERS_DATABASE_ID': 'test-db-id'
        }):
            manager = NotionUserManager()
            manager.client = mock_notion_client
            return manager


@pytest.fixture
def mock_user():
    """Mock User object for testing"""
    user = Mock(spec=User)
    user.id = 1
    user.phone_number = '+5511987654321'
    user.name = 'Estevao Antunes'
    user.created_at = datetime.utcnow()
    return user


@pytest.fixture
def mock_notion_page():
    """Mock Notion page response"""
    return {
        'id': 'page-id-123',
        'properties': {
            'Phone': {
                'phone_number': '+5511987654321'
            },
            'Name': {
                'title': [{'text': {'content': 'Estevao Antunes'}}]
            },
            'Onboarding_Stage': {
                'select': {'name': 'not_started'}
            }
        }
    }


class TestNotionUserManager:
    """Test suite for NotionUserManager"""

    def test_init_with_database_id_configured(self, mock_notion_client):
        """Test initialization when NOTION_USERS_DATABASE_ID is set"""
        with patch('src.integrations.notion_users.Client', return_value=mock_notion_client):
            with patch.dict('os.environ', {'NOTION_USERS_DATABASE_ID': 'test-db-id'}):
                manager = NotionUserManager()
                assert manager.users_db_id == 'test-db-id'

    def test_init_without_database_id(self, mock_notion_client):
        """Test initialization when NOTION_USERS_DATABASE_ID is not set"""
        with patch('src.integrations.notion_users.Client', return_value=mock_notion_client):
            with patch.dict('os.environ', {}, clear=True):
                manager = NotionUserManager()
                assert manager.users_db_id is None

    def test_get_user_by_phone_success(self, notion_manager, mock_notion_page):
        """Test successful user lookup by phone number"""
        # Arrange
        phone_number = '+5511987654321'
        notion_manager.client.databases.query.return_value = {
            'results': [mock_notion_page]
        }

        # Act
        result = notion_manager.get_user_by_phone(phone_number)

        # Assert
        assert result is not None
        assert result['id'] == 'page-id-123'
        notion_manager.client.databases.query.assert_called_once()

    def test_get_user_by_phone_not_found(self, notion_manager):
        """Test user lookup when user does not exist"""
        # Arrange
        phone_number = '+5511987654321'
        notion_manager.client.databases.query.return_value = {'results': []}

        # Act
        result = notion_manager.get_user_by_phone(phone_number)

        # Assert
        assert result is None

    def test_get_user_by_phone_api_error(self, notion_manager):
        """Test user lookup when Notion API fails"""
        # Arrange
        phone_number = '+5511987654321'
        notion_manager.client.databases.query.side_effect = Exception('API Error')

        # Act
        result = notion_manager.get_user_by_phone(phone_number)

        # Assert
        assert result is None

    def test_mark_onboarding_complete_success(self, notion_manager, mock_notion_page):
        """Test successful marking of onboarding as complete"""
        # Arrange
        phone_number = '+5511987654321'
        notion_manager.client.databases.query.return_value = {
            'results': [mock_notion_page]
        }

        # Act
        result = notion_manager.mark_onboarding_complete(phone_number)

        # Assert
        assert result is True
        notion_manager.client.pages.update.assert_called_once()

        # Verify correct properties were updated
        call_args = notion_manager.client.pages.update.call_args
        properties = call_args.kwargs['properties']
        assert properties['Onboarding_Stage']['select']['name'] == 'completed'
        assert 'Last_Profile_Update' in properties

    def test_mark_onboarding_complete_user_not_found(self, notion_manager):
        """Test marking onboarding when user does not exist"""
        # Arrange
        phone_number = '+5511987654321'
        notion_manager.client.databases.query.return_value = {'results': []}

        # Act
        result = notion_manager.mark_onboarding_complete(phone_number)

        # Assert
        assert result is False
        notion_manager.client.pages.update.assert_not_called()

    def test_mark_onboarding_complete_api_error(self, notion_manager, mock_notion_page):
        """Test marking onboarding when Notion API fails"""
        # Arrange
        phone_number = '+5511987654321'
        notion_manager.client.databases.query.return_value = {
            'results': [mock_notion_page]
        }
        notion_manager.client.pages.update.side_effect = Exception('API Error')

        # Act
        result = notion_manager.mark_onboarding_complete(phone_number)

        # Assert
        assert result is False

    def test_get_onboarding_status_completed(self, notion_manager):
        """Test getting onboarding status when completed"""
        # Arrange
        phone_number = '+5511987654321'
        completed_page = {
            'id': 'page-id',
            'properties': {
                'Onboarding_Stage': {
                    'select': {'name': 'completed'}
                }
            }
        }
        notion_manager.client.databases.query.return_value = {
            'results': [completed_page]
        }

        # Act
        result = notion_manager.get_onboarding_status(phone_number)

        # Assert
        assert result is True

    def test_get_onboarding_status_not_completed(self, notion_manager):
        """Test getting onboarding status when not completed"""
        # Arrange
        phone_number = '+5511987654321'
        not_started_page = {
            'id': 'page-id',
            'properties': {
                'Onboarding_Stage': {
                    'select': {'name': 'not_started'}
                }
            }
        }
        notion_manager.client.databases.query.return_value = {
            'results': [not_started_page]
        }

        # Act
        result = notion_manager.get_onboarding_status(phone_number)

        # Assert
        assert result is False

    def test_get_onboarding_status_user_not_found(self, notion_manager):
        """Test getting onboarding status when user does not exist"""
        # Arrange
        phone_number = '+5511987654321'
        notion_manager.client.databases.query.return_value = {'results': []}

        # Act
        result = notion_manager.get_onboarding_status(phone_number)

        # Assert
        assert result is False

    def test_sync_user_to_notion_new_user(self, notion_manager, mock_user):
        """Test syncing new user to Notion"""
        # Arrange
        notion_manager.client.databases.query.return_value = {'results': []}
        notion_manager.client.pages.create.return_value = {'id': 'new-page-id'}

        # Act
        result = notion_manager.sync_user_to_notion(mock_user)

        # Assert
        assert result == 'new-page-id'
        notion_manager.client.pages.create.assert_called_once()

        # Verify correct properties were set
        call_args = notion_manager.client.pages.create.call_args
        properties = call_args.kwargs['properties']
        assert properties['Phone']['phone_number'] == '+5511987654321'
        assert properties['Name']['title'][0]['text']['content'] == 'Estevao Antunes'

    def test_sync_user_to_notion_existing_user(self, notion_manager, mock_user, mock_notion_page):
        """Test syncing existing user to Notion (update)"""
        # Arrange
        notion_manager.client.databases.query.return_value = {
            'results': [mock_notion_page]
        }

        # Act
        result = notion_manager.sync_user_to_notion(mock_user)

        # Assert
        assert result == 'page-id-123'
        notion_manager.client.pages.update.assert_called_once()
        notion_manager.client.pages.create.assert_not_called()

    def test_sync_user_to_notion_api_error(self, notion_manager, mock_user):
        """Test syncing user when Notion API fails"""
        # Arrange
        notion_manager.client.databases.query.side_effect = Exception('API Error')

        # Act
        result = notion_manager.sync_user_to_notion(mock_user)

        # Assert
        assert result is None

    def test_update_user_notion_field_success(self, notion_manager, mock_notion_page):
        """Test updating a specific user field in Notion"""
        # Arrange
        phone_number = '+5511987654321'
        field_name = 'Status'
        field_value = 'active'
        notion_manager.client.databases.query.return_value = {
            'results': [mock_notion_page]
        }

        # Act
        result = notion_manager.update_user_notion_field(
            phone_number, field_name, field_value
        )

        # Assert
        assert result is True
        notion_manager.client.pages.update.assert_called_once()

    def test_update_user_notion_field_user_not_found(self, notion_manager):
        """Test updating field when user does not exist"""
        # Arrange
        phone_number = '+5511987654321'
        notion_manager.client.databases.query.return_value = {'results': []}

        # Act
        result = notion_manager.update_user_notion_field(
            phone_number, 'Status', 'active'
        )

        # Assert
        assert result is False

    def test_no_database_id_configured(self, mock_notion_client):
        """Test that methods handle missing database ID gracefully"""
        with patch('src.integrations.notion_users.Client', return_value=mock_notion_client):
            with patch.dict('os.environ', {}, clear=True):
                manager = NotionUserManager()

                # All methods should return None/False when DB ID not set
                assert manager.get_user_by_phone('+1234567890') is None
                assert manager.get_onboarding_status('+1234567890') is False
                assert manager.mark_onboarding_complete('+1234567890') is False
                assert manager.update_user_notion_field('+1234567890', 'field', 'value') is False

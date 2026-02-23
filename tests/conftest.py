
import pytest
from unittest.mock import MagicMock
import sys
import os

# Ensure modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def mock_app_context():
    """
    Creates a fully mocked app context for testing skills.
    """
    mock_context = {
        'speech': MagicMock(),
        'brain': MagicMock(),
        'files': MagicMock(),
        'system': MagicMock(),
        'config': MagicMock(),
        'analytics': MagicMock(),
        'weather': MagicMock(),
        'fuzzy': MagicMock(),
        'music': MagicMock(),
        'news': MagicMock(),
        'calculator': MagicMock(),
        'email_manager': MagicMock(),
        'contacts': MagicMock(),
        'shortcuts': MagicMock(),
        'ghost': MagicMock(),
        'cursor': MagicMock(),
        'visuals': MagicMock(),
        'assassin': MagicMock(),
        'dead_drop': MagicMock(),
        'clipboard': MagicMock(),
        'focus': MagicMock(),
        'command_processor': MagicMock(),
        'calendar': MagicMock(),
        'reminders': MagicMock(),
        'mimic': MagicMock(),
        'translator': MagicMock(),
        'alarm_manager': MagicMock()
    }
    
    # Configure common return values to avoid AttributeError
    mock_context['command_processor'].manual_online_status = True
    
    return mock_context

@pytest.fixture
def mock_speech(mock_app_context):
    return mock_app_context['speech']

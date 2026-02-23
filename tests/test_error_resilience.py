
import pytest
from unittest.mock import MagicMock, patch
import requests
import json
import webbrowser

from modules.skills import (
    WeatherSkill, NewsSkill, InternetSkill, 
    FileSkill, AppControlSkill, MusicSkill, CalculatorSkill
)

# --- PHASE 1: NETWORK SKILLS ---

def test_weather_connection_error(mock_app_context, mock_speech):
    skill = WeatherSkill(mock_app_context)
    mock_app_context['weather'].get_weather.side_effect = requests.exceptions.ConnectionError("Offline")
    
    skill.handle("weather in london")
    
    mock_speech.speak.assert_called_with("I cannot connect to the weather service. Please check your internet connection.")

def test_weather_json_error(mock_app_context, mock_speech):
    skill = WeatherSkill(mock_app_context)
    mock_app_context['weather'].get_weather.side_effect = json.JSONDecodeError("Bad JSON", "", 0)
    
    skill.handle("weather")
    
    mock_speech.speak.assert_called_with("I received invalid data from the weather provider.")

def test_internet_browser_error(mock_app_context, mock_speech):
    skill = InternetSkill(mock_app_context)
    # Mocking webbrowser.open to raise Error
    with patch('webbrowser.open', side_effect=webbrowser.Error("Browser crash")):
        skill.handle("google python")
        mock_speech.speak.assert_called_with("I couldn't open the web browser.")

# --- PHASE 2: SYSTEM SKILLS ---

def test_file_permission_error(mock_app_context, mock_speech):
    skill = FileSkill(mock_app_context)
    mock_app_context['files'].delete_file.side_effect = PermissionError("Access denied")
    
    skill.handle("delete file secret.txt")
    
    mock_speech.speak.assert_called_with("I sort of don't have permission to delete that.")

def test_file_not_found_error(mock_app_context, mock_speech):
    skill = FileSkill(mock_app_context)
    mock_app_context['files'].delete_file.side_effect = FileNotFoundError("Missing")
    
    skill.handle("delete file ghost.txt")
    
    msg = mock_speech.speak.call_args[0][0]
    assert "I couldn't find a file named ghost.txt" in msg

def test_app_control_failure(mock_app_context, mock_speech):
    skill = AppControlSkill(mock_app_context)
    # Mock subprocess.run to return failure code
    mock_fail = MagicMock()
    mock_fail.returncode = 1
    mock_fail.stderr = "App not found"

    with patch('subprocess.run', return_value=mock_fail):
        # Should try fuzzy, fail, then speak error
        # Assuming fuzzy matcher returns None for this test if not mocked
        mock_app_context['fuzzy'].match_app_name.return_value = None
        
        skill.handle("open NonExistentApp")
        
        msg = mock_speech.speak.call_args[0][0]
        assert "I couldn't find an app named nonexistentapp" in msg

# --- PHASE 3: UTILITY SKILLS ---

def test_calculator_zero_division(mock_app_context, mock_speech):
    skill = CalculatorSkill(mock_app_context)
    # Mock parser to raise ZeroDivisionError (or let actual logic run if we were testing module, but here we test skill handling)
    mock_app_context['calculator'].parse_and_calculate.side_effect = ZeroDivisionError("Div by 0")
    
    skill.handle("calculate 10 divided by 0")
    
    mock_speech.speak.assert_called_with("I cannot divide by zero.")

def test_music_generic_error(mock_app_context, mock_speech):
    skill = MusicSkill(mock_app_context)
    mock_app_context['music'].play.side_effect = Exception("Spotify crashed")
    
    skill.handle("resume music")
    
    mock_speech.speak.assert_called_with("I'm having trouble controlling the music player.")

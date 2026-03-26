"""
tests/test_smartthings.py
──────────────────────────
Unit tests for SmartThingsManager and SmartThingsSkill.
Uses unittest.mock to avoid real HTTP calls.
Run with: python -m pytest tests/test_smartthings.py -v
"""

import pytest
from unittest.mock import MagicMock, patch
from modules.smartthings import (
    SmartThingsManager,
    SmartThingsAuthError,
    SmartThingsDeviceError,
    SmartThingsAPIError,
    SmartThingsError,
)
from modules.skills.smartthings_skill import SmartThingsSkill

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_manager():
    manager = MagicMock(spec=SmartThingsManager)
    manager.turn_on.return_value = {"results": [{"id": "main", "status": "ACCEPTED"}]}
    manager.turn_off.return_value = {"results": [{"id": "main", "status": "ACCEPTED"}]}
    manager.set_temperature.return_value = {"results": [{"id": "main", "status": "ACCEPTED"}]}
    manager.set_mode.return_value = {"results": [{"id": "main", "status": "ACCEPTED"}]}
    manager.get_status.return_value = {
        "switch": "on",
        "temperature": 27.0,
        "coolingSetpoint": 22.0,
        "airConditionerMode": "cool",
    }
    return manager

@pytest.fixture
def skill(mock_manager):
    return SmartThingsSkill(manager=mock_manager)

# ── SmartThingsSkill.matches() ────────────────────────────────────────────────

class TestSkillMatching:
    @pytest.mark.parametrize("phrase", [
        "turn on the ac",
        "turn on the air conditioner",
        "switch on AC",
        "ac on",
        "it's hot",
        "make it cooler",
        "its getting warm",
    ])
    def test_ac_on_matches(self, skill, phrase):
        assert skill.matches(phrase), f"Should match AC_ON for: '{phrase}'"

    @pytest.mark.parametrize("phrase", [
        "turn off the ac",
        "switch off ac",
        "ac off",
        "it's freezing",
        "it's too cold",
    ])
    def test_ac_off_matches(self, skill, phrase):
        assert skill.matches(phrase), f"Should match AC_OFF for: '{phrase}'"

    @pytest.mark.parametrize("phrase", [
        "set ac to 22 degrees",
        "set the temperature to 24",
        "make it 20 celsius",
        "22 degrees please",
    ])
    def test_set_temp_matches(self, skill, phrase):
        assert skill.matches(phrase), f"Should match SET_TEMP for: '{phrase}'"

    @pytest.mark.parametrize("phrase", [
        "set ac to cool mode",
        "switch to heat mode",
        "change to auto",
        "set ac to dry",
    ])
    def test_set_mode_matches(self, skill, phrase):
        assert skill.matches(phrase), f"Should match SET_MODE for: '{phrase}'"

    @pytest.mark.parametrize("phrase", [
        "what time is it",
        "play some music",
        "set a timer for 10 minutes",
        "hello jarvis",
    ])
    def test_non_ac_does_not_match(self, skill, phrase):
        assert not skill.matches(phrase), f"Should NOT match for: '{phrase}'"

# ── SmartThingsSkill.execute() ────────────────────────────────────────────────

class TestSkillExecution:
    def test_execute_ac_on(self, skill, mock_manager):
        result = skill.execute("turn on the ac")
        mock_manager.turn_on.assert_called_once()
        assert "on" in result.lower()

    def test_execute_ac_off(self, skill, mock_manager):
        result = skill.execute("turn off the ac")
        mock_manager.turn_off.assert_called_once()
        assert "off" in result.lower()

    def test_execute_set_temp(self, skill, mock_manager):
        result = skill.execute("set ac to 22 degrees")
        mock_manager.set_temperature.assert_called_once_with(22.0)
        assert "22" in result

    def test_execute_set_mode_cool(self, skill, mock_manager):
        result = skill.execute("set ac to cool mode")
        mock_manager.set_mode.assert_called_once_with("cool")
        assert "cool" in result.lower()

    def test_execute_status(self, skill, mock_manager):
        result = skill.execute("ac status")
        mock_manager.get_status.assert_called_once()
        assert "on" in result.lower()
        assert "27" in result or "22" in result

    def test_api_error_returns_graceful_message(self, skill, mock_manager):
        mock_manager.turn_on.side_effect = SmartThingsError("Connection failed")
        result = skill.execute("turn on the ac")
        assert "problem" in result.lower() or "failed" in result.lower()

# ── SmartThingsManager HTTP error mapping ─────────────────────────────────────

class TestManagerErrorMapping:
    @patch("modules.smartthings.requests.post")
    def test_401_raises_auth_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        manager = SmartThingsManager(pat="fake", device_id="fake-device")
        with pytest.raises(SmartThingsAuthError):
            manager.turn_on()

    @patch("modules.smartthings.requests.post")
    def test_404_raises_device_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_post.return_value = mock_response
        manager = SmartThingsManager(pat="fake", device_id="fake-device")
        with pytest.raises(SmartThingsDeviceError):
            manager.turn_on()

    @patch("modules.smartthings.requests.post")
    def test_temperature_out_of_range_raises_value_error(self, mock_post):
        manager = SmartThingsManager(pat="fake", device_id="fake-device")
        with pytest.raises(ValueError):
            manager.set_temperature(5)   # Below TEMP_MIN_C
        with pytest.raises(ValueError):
            manager.set_temperature(50)  # Above TEMP_MAX_C

    @patch("modules.smartthings.requests.post")
    def test_invalid_mode_raises_value_error(self, mock_post):
        manager = SmartThingsManager(pat="fake", device_id="fake-device")
        with pytest.raises(ValueError):
            manager.set_mode("turbo_nuclear_blast")

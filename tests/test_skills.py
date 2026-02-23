import sys
import os
import unittest
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config
from modules.skills import (
    SystemSkill, TimeSkill, AppControlSkill, WeatherSkill,
    MusicSkill, NewsSkill, CalculatorSkill, CommunicationSkill,
    InternetSkill, FileSkill, FocusSkill, ResearchSkill,
    AutomationSkill, ShortcutsSkill, InteractionSkill
)

class TestSkills(unittest.TestCase):
    def setUp(self):
        # Mock Context
        self.mock_context = {
            'speech': MagicMock(),
            'brain': MagicMock(),
            'files': MagicMock(),
            'system': MagicMock(),
            'config': config,
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
            'command_processor': MagicMock()
        }
        
        # Mock Speech methods
        self.mock_context['speech'].speak = MagicMock()
        self.mock_context['speech'].tts = MagicMock()

    def test_interaction_skill(self):
        skill = InteractionSkill(self.mock_context)
        self.assertTrue(skill.can_handle("thanks"))
        self.assertTrue(skill.can_handle("exit"))
        self.assertTrue(skill.handle("thanks"))
        self.assertEqual(skill.handle("exit"), "EXIT")

    def test_system_skill(self):
        skill = SystemSkill(self.mock_context)
        self.assertTrue(skill.can_handle("set volume to 50"))
        self.assertTrue(skill.can_handle("voice feedback verbose"))
        self.assertTrue(skill.handle("voice feedback verbose"))

    def test_time_skill(self):
        skill = TimeSkill(self.mock_context)
        self.assertTrue(skill.can_handle("what time is it"))
        self.assertTrue(skill.handle("what time is it"))

    def test_app_control_skill(self):
        skill = AppControlSkill(self.mock_context)
        # Mock config.MAC_APPS or just rely on generic "open"
        self.assertTrue(skill.can_handle("open safari"))
        # We don't run handle because it tries to launch apps, but we can check logic path
        # skill.handle("open safari") would fail if 'open' not mocked in os.system
        
    def test_weather_skill(self):
        skill = WeatherSkill(self.mock_context)
        self.assertTrue(skill.can_handle("what is the weather"))
        self.assertTrue(skill.handle("what is the weather"))

    def test_music_skill(self):
        skill = MusicSkill(self.mock_context)
        self.assertTrue(skill.can_handle("play music"))
        self.assertTrue(skill.can_handle("next song"))
        # handle calls app_context['music'].play_soothing() for "play music"
        self.assertTrue(skill.handle("play music"))
        self.mock_context['music'].play_soothing.assert_called()

    def test_calculator_skill(self):
        skill = CalculatorSkill(self.mock_context)
        self.assertTrue(skill.can_handle("calculate 5 plus 5"))
        self.assertTrue(skill.can_handle("how much is 100 dollars in euros"))
        self.mock_context['calculator'].calculate.return_value = "10"
        self.assertTrue(skill.handle("calculate 5 plus 5"))

    def test_internet_skill(self):
        skill = InternetSkill(self.mock_context)
        self.assertTrue(skill.can_handle("quickly search on google about jarvis"))
        self.assertTrue(skill.can_handle("toggle internet"))
        self.assertFalse(skill.can_handle("could u please make a quick search on \"jarvis ai\""))
        # handle opens browser, so we mock webbrowser
        import webbrowser
        webbrowser.open = MagicMock()
        self.assertTrue(skill.handle("quickly search on google about jarvis"))

    def test_automation_skill_summarize_intent(self):
        skill = AutomationSkill(self.mock_context)
        self.mock_context['brain'].ask.return_value = "short summary"

        self.assertTrue(skill.can_handle("summarize it"))
        self.assertTrue(skill.can_handle("Please summarize this: Jarvis is an AI assistant."))
        self.assertTrue(skill.handle("Please summarize this: Jarvis is an AI assistant that helps with commands."))
        self.mock_context['brain'].ask.assert_called()

if __name__ == '__main__':
    unittest.main()

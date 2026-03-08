import datetime
import unittest
from unittest.mock import MagicMock, patch

from modules.alarm_manager import AlarmManager


class TestAlarmManager(unittest.TestCase):
    def test_parse_spoken_time_tomorrow_morning(self):
        manager = AlarmManager()
        now = datetime.datetime.now()
        parsed = manager._parse_smart_time("six thirty tomorrow morning")

        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.hour, 6)
        self.assertEqual(parsed.minute, 30)
        self.assertEqual(parsed.date(), (now + datetime.timedelta(days=1)).date())
        self.assertGreater(parsed, now)

    def test_parse_wake_me_up_phrase_tomorrow_morning(self):
        manager = AlarmManager()
        now = datetime.datetime.now()
        parsed = manager._parse_smart_time("wake me up at six thirty tomorrow morning")

        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.hour, 6)
        self.assertEqual(parsed.minute, 30)
        self.assertEqual(parsed.date(), (now + datetime.timedelta(days=1)).date())
        self.assertGreater(parsed, now)

    def test_parse_relative_time_still_works(self):
        manager = AlarmManager()
        now = datetime.datetime.now()
        parsed = manager._parse_smart_time("in 20 minutes")

        self.assertIsNotNone(parsed)
        delta = parsed - now
        self.assertGreaterEqual(delta, datetime.timedelta(minutes=19))
        self.assertLessEqual(delta, datetime.timedelta(minutes=21))

    def test_parse_simple_am_time_still_works(self):
        manager = AlarmManager()
        parsed = manager._parse_smart_time("7 am")

        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.hour, 7)
        self.assertEqual(parsed.minute, 0)

    def test_set_alarm_with_spoken_time_runs_shortcut(self):
        manager = AlarmManager()
        ok = MagicMock(returncode=0, stderr="")

        with patch("subprocess.run", return_value=ok) as run_mock:
            success, message = manager.set_alarm("wake me up at six thirty tomorrow morning")

        self.assertTrue(success)
        self.assertIn("Alarm set for", message)
        run_mock.assert_called_once()
        call_args = run_mock.call_args[0][0]
        self.assertEqual(call_args[:4], ["shortcuts", "run", "Set Alarm", "-i"])


if __name__ == "__main__":
    unittest.main()

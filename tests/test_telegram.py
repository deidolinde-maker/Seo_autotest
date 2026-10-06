import os
import unittest
from unittest.mock import patch

from taskdev_3188.telegram import format_report_message, send_report


class TelegramTests(unittest.TestCase):
    def test_ok_message_ignores_skipped_as_failure(self):
        message = format_report_message(
            {"counters": {"ok": 322, "changed": 0, "errors": 0, "unavailable": 0, "skipped": 12}},
            "https://jenkins.example/job/1/",
            "17",
        )
        self.assertNotIn("TASKDEV-3188", message)
        self.assertIn("Всё в норме", message)
        self.assertIn("⏭ Пропущено redirect URL: <b>12</b>", message)
        self.assertIn("Jenkins build #17", message)

    def test_disabled_telegram_does_not_fail(self):
        with patch.dict(os.environ, {"TELEGRAM_ENABLED": "false"}, clear=False):
            self.assertTrue(send_report({"counters": {}}, ""))


if __name__ == "__main__":
    unittest.main()

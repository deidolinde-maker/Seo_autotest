import unittest

from taskdev_3188.models import PageSnapshot
from taskdev_3188.validator import validate_page


class RedirectSkipTests(unittest.TestCase):
    def test_baseline_redirect_is_skipped(self):
        baseline = PageSnapshot("https://example.test", fetch_status="failed", http_status=308, error="redirect")
        current = PageSnapshot("https://example.test", fetch_status="failed", http_status=308, error="redirect")
        result = validate_page(current, baseline, "101")
        self.assertEqual(result.status, "пропущено")
        self.assertEqual(result.fetch_error, "baseline_redirect")

    def test_successful_baseline_is_not_skipped(self):
        baseline = PageSnapshot("https://example.test", title="Old", description="D", h1=["H1"])
        current = PageSnapshot("https://example.test", title="New", description="D", h1=["H1"])
        result = validate_page(current, baseline, "101")
        self.assertEqual(result.status, "изменена")


if __name__ == "__main__":
    unittest.main()

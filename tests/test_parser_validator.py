import unittest

from taskdev_3188.models import PageSnapshot
from taskdev_3188.parser import parse_html
from taskdev_3188.validator import site_for_url, validate_page


class ParserValidatorTests(unittest.TestCase):
    def test_parser_reads_exact_values_and_h2_order(self):
        snapshot = parse_html(
            "https://example.test/page",
            """
            <html><head><title>Title</title>
            <meta name='description' content='Description'></head>
            <body><h1>H1</h1><h2>First</h2><h2>Second</h2></body></html>
            """,
        )
        self.assertEqual(snapshot.title, "Title")
        self.assertEqual(snapshot.description, "Description")
        self.assertEqual(snapshot.h1, ["H1"])
        self.assertEqual(snapshot.h2, ["First", "Second"])

    def test_changed_text_is_reported(self):
        baseline = PageSnapshot("/page", title="Old", description="D", h1=["H1"], h2=["A"])
        current = PageSnapshot("/page", title="New", description="D", h1=["H1"], h2=["A"])
        result = validate_page(current, baseline, "101")
        self.assertEqual(result.status, "изменена")
        self.assertEqual(result.changes["meta title"], {"was": "Old", "became": "New"})

    def test_missing_h1_is_repeated_error(self):
        baseline = PageSnapshot("/page", title="T", description="D", h1=["Old"], h2=[])
        current = PageSnapshot("/page", title="T", description="D", h1=[], h2=[])
        result = validate_page(current, baseline, "101")
        self.assertEqual(result.status, "ошибка")
        self.assertEqual(result.errors[0]["element"], "H1")

    def test_failed_fetch_does_not_become_seo_error(self):
        current = PageSnapshot("/page", fetch_status="failed", error="404")
        result = validate_page(current, None, "101")
        self.assertEqual(result.status, "не удалось проверить")
        self.assertFalse(result.errors)

    def test_site_is_detected_from_url(self):
        self.assertEqual(site_for_url("https://101internet.ru/moskva"), "101")
        self.assertEqual(site_for_url("https://www.moskvaonline.ru/rates"), "mol")
        self.assertEqual(site_for_url("https://piter-online.net/rates"), "pol")


if __name__ == "__main__":
    unittest.main()

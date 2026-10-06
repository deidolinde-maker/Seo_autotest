import json
import shutil
import tempfile
import unittest
from pathlib import Path

from taskdev_3188.collector import Collector
from taskdev_3188.models import PageSnapshot
from taskdev_3188.storage import load_snapshot, read_urls, save_snapshot


class FakeResponse:
    def __init__(self, status_code=200, text="", url="https://example.test/page"):
        self.status_code = status_code
        self.text = text
        self.url = url


class FakeSession:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.response


class CollectorStorageTests(unittest.TestCase):
    def test_redirect_is_not_followed(self):
        session = FakeSession(FakeResponse(301))
        result = Collector(session=session).collect_one("https://example.test/page")
        self.assertEqual(result.fetch_status, "failed")
        self.assertEqual(result.error, "redirect")
        self.assertFalse(session.calls[0][1]["allow_redirects"])

    def test_snapshot_round_trip_and_deduplicated_urls(self):
        directory = tempfile.mkdtemp(prefix="test-storage-", dir=Path.cwd())
        try:
            root = Path(directory)
            urls = root / "urls.txt"
            urls.write_text("# comment\nhttps://a.test\nhttps://a.test\n\nhttps://b.test\n", encoding="utf-8")
            self.assertEqual(read_urls(urls), ["https://a.test", "https://b.test"])

            target = root / "state" / "snapshot.json"
            save_snapshot(target, [PageSnapshot("https://a.test", title="T")], "now")
            loaded = load_snapshot(target)
            self.assertEqual(loaded["https://a.test"].title, "T")
            json.loads(target.read_text(encoding="utf-8"))
        finally:
            shutil.rmtree(directory, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()

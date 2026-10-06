import json
import tempfile
import unittest
from pathlib import Path

from taskdev_3188.allure_report import write_allure_results
from taskdev_3188.models import ValidationResult


class AllureReportTests(unittest.TestCase):
    def test_writes_one_result_per_url(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            results = [
                ValidationResult("https://a.test", "ОК"),
                ValidationResult("https://b.test", "изменена", changes={"H1": {"was": "A", "became": "B"}}),
            ]
            write_allure_results(results, directory)
            files = list(Path(directory).glob("*-result.json"))
            self.assertEqual(len(files), 2)
            statuses = {json.loads(path.read_text(encoding="utf-8"))["status"] for path in files}
            self.assertEqual(statuses, {"passed", "failed"})


if __name__ == "__main__":
    unittest.main()

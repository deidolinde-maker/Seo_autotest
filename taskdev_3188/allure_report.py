from __future__ import annotations

import json
import shutil
import time
import uuid
from pathlib import Path
from typing import Iterable

from .models import ValidationResult


def _allure_status(result: ValidationResult) -> str:
    if result.status == "пропущено":
        return "skipped"
    return "passed" if result.status == "ОК" else "failed"


def write_allure_results(results: Iterable[ValidationResult], output_dir: str | Path) -> None:
    """Write Allure 2 result files without requiring an Allure Python plugin."""
    target = Path(output_dir)
    if target.exists():
        for item in target.iterdir():
            if item.is_file() and item.name.endswith("-result.json"):
                item.unlink()
    target.mkdir(parents=True, exist_ok=True)
    now = int(time.time() * 1000)
    for result in results:
        result_uuid = str(uuid.uuid4())
        payload = {
            "uuid": result_uuid,
            "historyId": result.url,
            "fullName": f"TASKDEV-3188 :: {result.url}",
            "name": result.url,
            "status": _allure_status(result),
            "stage": "finished",
            "start": now,
            "stop": now,
            "statusDetails": {
                "message": json.dumps({
                    "status": result.status,
                    "changes": result.changes,
                    "errors": result.errors,
                    "fetch_error": result.fetch_error,
                }, ensure_ascii=False),
            },
            "labels": [
                {"name": "suite", "value": "TASKDEV-3188"},
                {"name": "feature", "value": "SEO validation"},
            ],
            "parameters": [{"name": "url", "value": result.url}],
        }
        (target / f"{result_uuid}-result.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

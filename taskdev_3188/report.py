from __future__ import annotations

from typing import Iterable

from .models import ValidationResult
from .storage import write_json_atomic


def build_report(results: Iterable[ValidationResult], generated_at: str) -> dict:
    items = list(results)
    counters = {
        "changed": sum(item.status == "изменена" for item in items),
        "errors": sum(item.status == "ошибка" for item in items),
        "unavailable": sum(item.status == "не удалось проверить" for item in items),
        "skipped": sum(item.status == "пропущено" for item in items),
        "ok": sum(item.status == "ОК" for item in items),
    }
    return {"generated_at": generated_at, "counters": counters, "pages": [item.to_dict() for item in items]}


def save_report(path: str, results: Iterable[ValidationResult], generated_at: str) -> dict:
    report = build_report(results, generated_at)
    write_json_atomic(path, report)
    return report

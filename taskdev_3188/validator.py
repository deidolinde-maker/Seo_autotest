from __future__ import annotations

from typing import Dict, Optional
from urllib.parse import urlparse

from .models import PageSnapshot, ValidationResult


PLACEHOLDERS = {
    "101": "101internet",
    "mol": "moskvaonline",
    "pol": "piteronline",
}


def site_for_url(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    if host == "101internet.ru" or host.endswith(".101internet.ru"):
        return "101"
    if host == "www.moskvaonline.ru" or host.endswith(".moskvaonline.ru"):
        return "mol"
    if host == "piter-online.net" or host.endswith(".piter-online.net"):
        return "pol"
    raise ValueError(f"Unsupported site hostname: {host or '<empty>'}")


def _invalid_required(values, placeholder: Optional[str]):
    if len(values) != 1:
        return {"reason": "wrong_count", "count": len(values), "values": values}
    value = values[0]
    if value is None or not str(value).strip():
        return {"reason": "empty", "count": 1, "values": values}
    if placeholder is not None and value == placeholder:
        return {"reason": "placeholder", "count": 1, "values": values}
    return None


def validate_page(current: PageSnapshot, baseline: Optional[PageSnapshot], site: str) -> ValidationResult:
    if current.fetch_status != "success":
        return ValidationResult(
            url=current.url,
            status="не удалось проверить",
            fetch_error=current.error or "fetch_failed",
        )

    placeholder = PLACEHOLDERS.get(site)
    errors = []
    element_errors = {}
    for name, values in (
        ("meta title", [current.title]),
        ("meta description", [current.description]),
        ("H1", current.h1),
    ):
        error = _invalid_required(values, placeholder if name != "H1" else None)
        if error:
            item = {"element": name, **error}
            errors.append(item)
            element_errors[name] = item

    changes: Dict[str, Dict[str, object]] = {}
    if baseline is not None:
        for name, old, new in (
            ("meta title", baseline.title, current.title),
            ("meta description", baseline.description, current.description),
            ("H1", baseline.h1, current.h1),
            ("H2", baseline.h2, current.h2),
        ):
            # Ошибочное значение элемента не становится изменением.
            if name in element_errors:
                continue
            if old != new:
                changes[name] = {"was": old, "became": new}

    if errors:
        status = "ошибка"
    elif baseline is None:
        status = "ОК"
    elif changes:
        status = "изменена"
    else:
        status = "ОК"
    return ValidationResult(url=current.url, status=status, changes=changes, errors=errors)

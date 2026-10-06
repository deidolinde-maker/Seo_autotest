from __future__ import annotations

import html
import json
import os
from urllib.error import URLError
from urllib.request import Request, urlopen


def _enabled() -> bool:
    return (os.getenv("TELEGRAM_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"})


def format_report_message(report: dict, build_url: str = "") -> str:
    counters = report.get("counters", {})
    changed = int(counters.get("changed", 0))
    errors = int(counters.get("errors", 0))
    unavailable = int(counters.get("unavailable", 0))
    skipped = int(counters.get("skipped", 0))
    checked = int(counters.get("ok", 0)) + changed + errors

    if changed == 0 and errors == 0 and unavailable == 0:
        message = f"<b>TASKDEV-3188</b>\nОК\nПроверено страниц: {checked}"
    else:
        lines = ["<b>TASKDEV-3188</b>"]
        if changed:
            lines.append(f"Изменено страниц: {changed}")
        if errors:
            lines.append(f"SEO-ошибок: {errors}")
        if unavailable:
            lines.append(f"Не удалось проверить: {unavailable}")
        lines.append(f"Проверено страниц: {checked}")
        message = "\n".join(lines)

    if skipped:
        message += f"\nПропущено redirect URL: {skipped}"
    if build_url:
        message += f'\n<a href="{html.escape(build_url, quote=True)}">Открыть Jenkins build</a>'
    return message


def send_report(report: dict, build_url: str = "") -> bool:
    """Send a report through the existing Jenkins Telegram proxy contract."""
    if not _enabled():
        return True
    proxy_url = os.getenv("TELEGRAM_PROXY_URL", "").strip()
    auth_secret = os.getenv("TELEGRAM_PROXY_AUTH_SECRET", "").strip()
    proxy_creds = os.getenv("TELEGRAM_PROXY_CREDS", "").strip()
    if not proxy_url or not auth_secret or not proxy_creds:
        return False
    payload = {
        "title": "TASKDEV-3188 SEO monitor",
        "text": format_report_message(report, build_url),
        "creds": proxy_creds,
        "parse_mode": "HTML",
        "disable_notification": False,
    }
    request = Request(
        proxy_url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "X-Authentication": auth_secret},
        method="POST",
    )
    try:
        timeout = float(os.getenv("TELEGRAM_PROXY_TIMEOUT_SEC", "15"))
        with urlopen(request, timeout=timeout) as response:
            return 200 <= response.status < 400
    except (OSError, URLError):
        return False

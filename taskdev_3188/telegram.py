from __future__ import annotations

import html
import json
import os
from urllib.error import URLError
from urllib.request import Request, urlopen


def _enabled() -> bool:
    return (os.getenv("TELEGRAM_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"})


def format_report_message(report: dict, build_url: str = "", build_number: str = "") -> str:
    counters = report.get("counters", {})
    changed = int(counters.get("changed", 0))
    errors = int(counters.get("errors", 0))
    unavailable = int(counters.get("unavailable", 0))
    skipped = int(counters.get("skipped", 0))
    checked = int(counters.get("ok", 0)) + changed + errors

    has_events = changed > 0 or errors > 0 or unavailable > 0
    header = "⚠️ <b>Найдены события</b>" if has_events else "✅ <b>Проверка завершена</b>"
    lines = [
        "🔎 <b>TASKDEV-3188</b>",
        "<code>SEO monitor</code>",
        "",
        header,
        "━━━━━━━━━━━━━━━━",
    ]
    if not has_events:
        lines.append(f"✅ Всё в норме · проверено: <b>{checked}</b>")
    else:
        if changed:
            lines.append(f"📝 Изменено страниц: <b>{changed}</b>")
        if errors:
            lines.append(f"❌ SEO-ошибок: <b>{errors}</b>")
        if unavailable:
            lines.append(f"🚫 Не удалось проверить: <b>{unavailable}</b>")
        lines.append(f"📊 Проверено: <b>{checked}</b>")
    
    if skipped:
        lines.append(f"⏭ Пропущено redirect URL: <b>{skipped}</b>")
    lines.append("━━━━━━━━━━━━━━━━")
    if build_url:
        label = f"Открыть Jenkins build #{html.escape(build_number)}" if build_number else "Открыть Jenkins build"
        lines.append(f'🔗 <a href="{html.escape(build_url, quote=True)}">{label}</a>')
    return "\n".join(lines)


def send_report(report: dict, build_url: str = "", build_number: str = "") -> bool:
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
        "text": format_report_message(report, build_url, build_number),
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

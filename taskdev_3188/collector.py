from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Iterable, List
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .models import PageSnapshot
from .parser import parse_html


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class _UrllibResponse:
    def __init__(self, response):
        self.status_code = getattr(response, "status", response.getcode())
        self.url = response.geturl()
        self.text = response.read().decode(response.headers.get_content_charset() or "utf-8", errors="replace")


class _UrllibSession:
    def __init__(self):
        self.opener = build_opener(_NoRedirectHandler())

    def get(self, url, *, timeout, allow_redirects, headers):
        request = Request(url, headers=headers, method="GET")
        try:
            return _UrllibResponse(self.opener.open(request, timeout=timeout))
        except HTTPError as exc:
            if 300 <= exc.code < 400:
                return type("RedirectResponse", (), {"status_code": exc.code, "url": url, "text": ""})()
            raise


class Collector:
    """Manual snapshot builder. It never writes the approved baseline."""

    def __init__(self, session=None, timeout: float = 30.0, delay: float = 0.0):
        self.session = session or _UrllibSession()
        self.timeout = timeout
        self.delay = delay

    def collect_one(self, url: str) -> PageSnapshot:
        try:
            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=False,
                headers={"User-Agent": "TASKDEV-3188-seo-monitor/1.0"},
            )
            if 300 <= response.status_code < 400:
                return PageSnapshot(url=url, fetch_status="failed", http_status=response.status_code, error="redirect")
            if response.status_code in (404, 410):
                return PageSnapshot(url=url, fetch_status="failed", http_status=response.status_code, error="not_found")
            if response.status_code < 200 or response.status_code >= 300:
                return PageSnapshot(url=url, fetch_status="failed", http_status=response.status_code, error="http_error")
            return parse_html(url, response.text, http_status=response.status_code, final_url=getattr(response, "url", url))
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            return PageSnapshot(url=url, fetch_status="failed", error=str(exc))

    def collect(self, urls: Iterable[str]) -> List[PageSnapshot]:
        url_list = list(urls)
        results = []
        for index, url in enumerate(url_list):
            results.append(self.collect_one(url))
            if self.delay and index < len(url_list) - 1:
                time.sleep(self.delay)
        return results


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

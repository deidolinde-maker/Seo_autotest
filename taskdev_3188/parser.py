from __future__ import annotations

from html.parser import HTMLParser
from typing import List, Optional

from .models import PageSnapshot


class _SEOHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_values: List[str] = []
        self.description_values: List[str] = []
        self.h1_values: List[str] = []
        self.h2_values: List[str] = []
        self._active: Optional[str] = None
        self._buffer: List[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        attrs_dict = {str(key).lower(): value for key, value in attrs}
        tag = tag.lower()
        if tag == "meta" and str(attrs_dict.get("name") or "").lower() == "description":
            self.description_values.append(str(attrs_dict.get("content") or "").strip())
        if tag in {"title", "h1", "h2"}:
            self._active = tag
            self._buffer = []

    def handle_data(self, data: str) -> None:
        if self._active:
            self._buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag != self._active:
            return
        value = " ".join("".join(self._buffer).split())
        if tag == "title":
            self.title_values.append(value)
        elif tag == "h1":
            self.h1_values.append(value)
        elif tag == "h2":
            self.h2_values.append(value)
        self._active = None
        self._buffer = []


def parse_html(url: str, html: str, *, http_status: int = 200, final_url: str | None = None) -> PageSnapshot:
    """Parse server HTML without executing JavaScript."""
    parser = _SEOHTMLParser()
    parser.feed(html)
    title = parser.title_values[0] if len(parser.title_values) == 1 else None
    description = parser.description_values[0] if len(parser.description_values) == 1 else None
    return PageSnapshot(
        url=url,
        http_status=http_status,
        final_url=final_url or url,
        title=title,
        description=description.strip() if isinstance(description, str) else description,
        h1=parser.h1_values,
        h2=parser.h2_values,
    )

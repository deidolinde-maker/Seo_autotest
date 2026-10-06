from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PageSnapshot:
    url: str
    fetch_status: str = "success"
    http_status: Optional[int] = None
    final_url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    h1: List[Optional[str]] = field(default_factory=list)
    h2: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "fetch_status": self.fetch_status,
            "http_status": self.http_status,
            "final_url": self.final_url,
            "title": self.title,
            "description": self.description,
            "h1": self.h1,
            "h2": self.h2,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PageSnapshot":
        return cls(
            url=str(data["url"]),
            fetch_status=str(data.get("fetch_status", "success")),
            http_status=data.get("http_status"),
            final_url=data.get("final_url"),
            title=data.get("title"),
            description=data.get("description"),
            h1=list(data.get("h1") or []),
            h2=list(data.get("h2") or []),
            error=data.get("error"),
        )


@dataclass
class ValidationResult:
    url: str
    status: str
    changes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    fetch_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "status": self.status,
            "changes": self.changes,
            "errors": self.errors,
            "fetch_error": self.fetch_error,
        }

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Iterable, List

from .models import PageSnapshot


def read_urls(path: str | Path) -> List[str]:
    values: List[str] = []
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        value = raw.strip()
        if value and not value.startswith("#"):
            values.append(value)
    return list(dict.fromkeys(values))


def write_json_atomic(path: str | Path, payload) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, target)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def save_snapshot(path: str | Path, snapshots: Iterable[PageSnapshot], generated_at: str) -> None:
    pages = {item.url: item.to_dict() for item in snapshots}
    write_json_atomic(path, {"generated_at": generated_at, "pages": pages})


def load_snapshot(path: str | Path) -> Dict[str, PageSnapshot]:
    source = Path(path)
    if not source.exists():
        return {}
    data = json.loads(source.read_text(encoding="utf-8"))
    return {url: PageSnapshot.from_dict(item) for url, item in (data.get("pages") or {}).items()}

"""Персистентное состояние сессий (токены, куки).

Файл state.json хранится с правами 0600, каталог — 0700. Схема:
{
  "pulse": {"cookies": {...}, "tokens": {...}, "saved_at": <epoch>},
  "sdo":   {"wstoken": "...", "saved_at": <epoch>}
}
"""
import json
import os
import tempfile

from .config import STATE_DIR, STATE_FILE


def load() -> dict:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save(state: dict) -> None:
    os.chmod(STATE_DIR, 0o700)
    fd, tmp = tempfile.mkstemp(dir=STATE_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        os.chmod(tmp, 0o600)
        os.replace(tmp, STATE_FILE)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise

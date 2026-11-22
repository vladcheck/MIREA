"""Персистентное состояние сессий (токены, куки) и пинов черновиков.

Файл state.json хранится с правами 0600, каталог — 0700. Схема:
{
  "pulse": {"cookies": {...}, "tokens": {...}, "saved_at": <epoch>},
  "sdo":   {"wstoken": "...", "saved_at": <epoch>}
}

draft.json — пины файловых менеджеров черновиков ответов (СДО): пин, созданный
в одном процессе (например, прикрепление файла), доступен из другого (submit).
Схема: {"<cmid>": {"itemid": ..., "client_id": ..., ...}}.
"""

import json
import os
import tempfile
from pathlib import Path

from .config import STATE_DIR, STATE_FILE

DRAFT_FILE: Path = STATE_DIR / "draft.json"


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


# ----------------------------------------------------------- пины черновиков
# Пути берутся из атрибутов модуля В МОМЕНТ ВЫЗОВА — тесты могут
# замонкепатчить STATE_DIR/DRAFT_FILE.


def load_draft_pins() -> dict:
    """Пины черновиков {cmid: ctx}; битый или отсутствующий файл -> {}."""
    if not DRAFT_FILE.exists():
        return {}
    try:
        return json.loads(DRAFT_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_draft_pins(pins: dict) -> None:
    """Атомарно записать пины черновиков (каталог 0700, файл 0600)."""
    os.chmod(STATE_DIR, 0o700)
    fd, tmp = tempfile.mkstemp(dir=STATE_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(pins, f, ensure_ascii=False, indent=2)
        os.chmod(tmp, 0o600)
        os.replace(tmp, DRAFT_FILE)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise

"""Конфигурация: переменные окружения и пути.

Креды читаются из .env (см. .env.example) или окружения. Никогда не логировать.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def _get(key: str) -> str | None:
    v = os.environ.get(key)
    return v if v else None


LOGIN: str | None = _get("MIREA_LOGIN")
PASSWORD: str | None = _get("MIREA_PASSWORD")
SDO_TOKEN_OVERRIDE: str | None = _get("MIREA_SDO_TOKEN")

STATE_DIR: Path = Path(_get("MIREA_STATE_DIR") or ROOT / ".state")
STATE_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE: Path = STATE_DIR / "state.json"

BRS_FILE: Path = ROOT / "brs-semester.json"

SDO_BASE = "https://online-edu.mirea.ru"
PULSE_BASE = "https://pulse.mirea.ru"

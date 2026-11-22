"""Состояние подключения MCP к системам РТУ МИРЭА."""
import time

from fastmcp import FastMCP

from .. import state
from ..config import BRS_FILE, LOGIN, PASSWORD, STATE_FILE


def register(mcp: FastMCP) -> None:
    @mcp.tool
    def mirea_status() -> dict:
        """Проверить состояние подключения к системам РТУ МИРЭА.

        Показывает: заданы ли учётные данные, сохранены ли сессия Пульса
        и токен СДО, заполнен ли файл параметров БРС семестра, и какие шаги
        нужны для входа (обычно mirea_auth_start).
        """
        st = state.load()
        pulse = st.get("pulse") or {}
        sdo = st.get("sdo") or {}
        saved_at = pulse.get("saved_at")
        return {
            "credentials_configured": bool(LOGIN and PASSWORD),
            "pulse": {
                "session_saved": bool(pulse),
                "saved_at": saved_at,
                "fresh": bool(saved_at) and (time.time() - saved_at < 3600),
            },
            "sdo": {"token_saved": bool(sdo.get("wstoken"))},
            "brs_semester_file": BRS_FILE.exists(),
            "state_file": str(STATE_FILE),
        }

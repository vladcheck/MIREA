"""Инструменты СДО: дисциплины, баллы, предстоящие работы."""
from dataclasses import asdict

from fastmcp import FastMCP

from ..models import MireaMcpError
from ..sdo_client import SdoClient

_client: SdoClient | None = None


def _get_client() -> SdoClient:
    global _client
    if _client is None:
        _client = SdoClient()
    return _client


def register(mcp: FastMCP) -> None:
    @mcp.tool
    def mirea_disciplines() -> dict:
        """Дисциплины текущего семестра из СДО (online-edu.mirea.ru).

        Возвращает список дисциплин с баллами по работам текущего контроля,
        суммой набранных баллов и максимумом. Поле source показывает канал
        данных: "rest" (Moodle REST), "oidc" (SSO Пульса) или "browser"
        (локальная сессия Moodle).
        """
        client = _get_client()
        try:
            disciplines = client.disciplines()
            return {
                "source": client.source,
                "disciplines": [asdict(d) for d in disciplines],
            }
        except MireaMcpError as e:
            return {"error": str(e), "hint": e.hint}

    @mcp.tool
    def mirea_grades(discipline: str | None = None) -> dict:
        """Баллы по дисциплинам из СДО: работы, баллы, флаг проверено.

        Аргумент discipline — имя (или его часть) дисциплины; без него
        возвращаются баллы по всем дисциплинам. Работа считается проверенной,
        если балл за неё уже выставлен (graded=True, даже при 0 баллов).
        """
        client = _get_client()
        try:
            grades = client.grades(discipline)
            return {
                "source": client.source,
                "grades": [asdict(g) for g in grades],
            }
        except MireaMcpError as e:
            return {"error": str(e), "hint": e.hint}

    @mcp.tool
    def mirea_due_works(days: int = 14) -> dict:
        """Предстоящие работы с дедлайнами по всем дисциплинам из СДО.

        Аргумент days — горизонт в днях (по умолчанию 14). Возвращает работы,
        у которых дедлайн в пределах горизонта и которые ещё не сданы.
        """
        client = _get_client()
        try:
            works = client.due_works(days)
            return {"source": client.source, "due_works": works}
        except MireaMcpError as e:
            return {"error": str(e), "hint": e.hint}

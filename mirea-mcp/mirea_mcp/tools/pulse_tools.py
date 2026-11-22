"""Инструменты MCP для Пульса: вход, расписание, посещаемость."""
import dataclasses

from fastmcp import FastMCP

from ..models import MireaMcpError
from ..pulse_client import PulseClient


def register(mcp: FastMCP) -> None:
    client = PulseClient()

    @mcp.tool
    async def mirea_auth_start() -> dict:
        """Начать вход в системы РТУ МИРЭА (Пульс) по сохранённым учётным данным.

        Если требуется двухфакторная аутентификация, код будет отправлен на
        корпоративную почту @edu.mirea.ru — тогда подтвердите его инструментом
        mirea_auth_otp. Иначе сессия сохраняется сразу.
        """
        try:
            return await client.auth_start()
        except MireaMcpError as e:
            return {"error": str(e), "hint": e.hint}

    @mcp.tool
    async def mirea_auth_otp(code: str) -> dict:
        """Подтвердить вход кодом из письма на корпоративной почте @edu.mirea.ru.

        Вызывается после mirea_auth_start, если тот вернул otp_required=true.
        После успеха сессия Пульса сохраняется и инструменты расписания
        и посещаемости работают без повторного входа.
        """
        try:
            return await client.auth_otp(code)
        except MireaMcpError as e:
            return {"error": str(e), "hint": e.hint}

    @mcp.tool
    async def mirea_schedule(days: int = 7) -> dict:
        """Получить расписание занятий из Пульса на указанное число дней (по умолчанию 7).

        Возвращает список занятий с временем начала и конца (ISO, московский часовой
        пояс), названием дисциплины, типом (лекция/практика/лабораторная), аудиторией
        и преподавателем. Требует сохранённой сессии (см. mirea_auth_start).
        """
        try:
            lessons = await client.schedule(days=days)
            return {"lessons": [dataclasses.asdict(lesson) for lesson in lessons]}
        except MireaMcpError as e:
            return {"error": str(e), "hint": e.hint}

    @mcp.tool
    async def mirea_attendance(
        discipline: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> dict:
        """Получить посещаемость из Пульса по дисциплинам текущего семестра.

        Аргументы:
            discipline: фильтр по названию дисциплины (часть названия, без учёта регистра).
            date_from: начало периода в формате ISO (например, 2026-11-01).
            date_to: конец периода в формате ISO.

        По каждой дисциплине возвращает отметки за занятия (status: present /
        absent / excused), счётчики attended/total и сумму баллов за посещение
        (БП, обычно до 30). Требует сохранённой сессии (см. mirea_auth_start).
        """
        try:
            items = await client.attendance(discipline=discipline, date_from=date_from, date_to=date_to)
            return {"attendance": [dataclasses.asdict(item) for item in items]}
        except MireaMcpError as e:
            return {"error": str(e), "hint": e.hint}

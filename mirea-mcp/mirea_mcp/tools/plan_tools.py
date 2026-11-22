"""Инструмент mirea_plan — план-на-семестр по данным СДО и Пульса."""
from fastmcp import FastMCP

from .. import brs as brs_mod
from .. import plan as plan_mod
from ..models import MireaMcpError


def register(mcp: FastMCP) -> None:
    @mcp.tool
    async def mirea_plan(days: int = 14) -> dict:
        """Построить план-на-семестр по дисциплинам РТУ МИРЭА.

        Баллы и работы берутся из СДО (обязательны: без токена СДО план
        невозможен — начните с mirea_auth_start). Посещаемость, расписание
        и официальная сводка БРС берутся из Пульса; если сессия Пульса не
        активна, план строится по данным СДО, с пометкой. Для каждой
        дисциплины: сумма баллов (СБ) из Пульса и из СДО, заполнение
        категорий БРС (БТК/БП/БСК/БД/БТД/БДОП), цель по БРС, % проверенных
        работ, готовность к зачёту/экзамену. Рекомендации: какие занятия
        посетить, какие работы сдать, по каким дисциплинам можно не ходить.
        """
        from ..pulse_client import PulseClient
        from ..sdo_client import SdoClient

        try:
            brs = brs_mod.load_brs()
        except (OSError, ValueError) as e:
            return {"error": f"не удалось загрузить brs-semester.json: {e}",
                    "hint": "проверьте файл параметров БРС семестра"}

        pulse_note = None
        try:
            sdo = SdoClient()
            grades = sdo.grades()
        except MireaMcpError as e:
            return {"error": str(e), "hint": e.hint}

        attendances, lessons, pulse_brs = [], [], None
        try:
            pulse = PulseClient()
            attendances = await pulse.attendance()
            lessons = await pulse.schedule(days=days)
            pulse_brs = await pulse.brs_summary()
        except MireaMcpError:
            pulse_note = (
                "посещаемость и расписание недоступны: вызовите mirea_auth_start"
            )

        report = plan_mod.build_plan(
            grades, attendances, lessons, brs, days=days, pulse_brs=pulse_brs
        )

        result = {
            "days": report["days"],
            "disciplines": report["disciplines"],
            "recommendations": report["recommendations"],
            "brs": {
                "act": brs.get("act"),
                "act_date": brs.get("act_date"),
                "bmax": brs.get("bmax"),
                "zachet_min_sb": brs_mod.ZACHET_MIN_SB,
                "exam_min_sb": brs_mod.EXAM_MIN_SB,
                "graded_min_pct": brs_mod.GRADED_MIN_PCT,
                "sem_control_access_pct": brs.get("sem_control_access_pct"),
                "grade_scale": brs.get("grade_scale"),
                "bp_max": (brs.get("categories", {}).get("БП") or {}).get("max"),
            },
        }
        if pulse_note:
            result["note"] = pulse_note
        return result

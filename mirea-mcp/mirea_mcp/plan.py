"""Чистая логика плана-на-семестр (ADR-0003): без сети и без клиентов.

Вход — только доменные модели (models.py) и параметры БРС (brs.py).
Инструмент mirea_plan в tools/plan_tools.py собирает данные из СДО и Пульса
и вызывает build_plan. Сопоставление дисциплин между источниками — по
нормализованному имени: casefold, схлопывание пробелов, срез БРС-суффикса
СДО («_Зачет (часть 1/2) [I.26-27]»), затем префиксное вхождение (мин. 8).
"""
import re
from datetime import datetime, timedelta

from . import brs as brs_mod
from .models import AttendanceMark, DisciplineAttendance, DisciplineGrades, Lesson, Work

_SDO_SUFFIX = re.compile(
    r"_(Зач[её]т|Экзамен)(\s*\(часть[^)]*\))?\s*(\[[^\]]*\])?\s*$",
    re.IGNORECASE,
)
_MIN_PREFIX = 8


def _norm(name: str) -> str:
    n = " ".join(name.split()).casefold()
    return _SDO_SUFFIX.sub("", n).strip()


def _lookup(index: dict, name: str):
    """Совпадение дисциплин: точное по нормализованному имени, иначе префикс.

    Префиксный вариант требует, чтобы короткая сторона была не короче
    _MIN_PREFIX символов, — покрывает оставшиеся расхождения написания.
    """
    key = _norm(name)
    hit = index.get(key)
    if hit is not None:
        return hit
    best = None
    for k, v in index.items():
        if min(len(k), len(key)) < _MIN_PREFIX:
            continue
        if key.startswith(k) or k.startswith(key):
            if best is None or len(k) > len(best[0]):
                best = (k, v)
    return best[1] if best else None


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def plan_discipline(
    dg: DisciplineGrades,
    control: str,
    brs: dict,
    pulse_brs: dict | None = None,
) -> dict:
    """Статус одной дисциплины: СБ, % проверенных работ, цель и готовность.

    Официальный СБ берётся из сводки БРС Пульса (pulse_brs), если она есть;
    иначе — вычисляется из проверенных работ СДО. graded_pct всегда из СДО.
    """
    graded_works = [w for w in dg.works if w.graded]
    if graded_works:
        sb_sdo = sum(w.score or 0.0 for w in graded_works)
    else:
        sb_sdo = dg.sb or 0.0

    sb_pulse = pulse_brs.get("total") if pulse_brs else None
    sb = sb_pulse if sb_pulse is not None else sb_sdo

    total = len(dg.works)
    graded_pct = (len(graded_works) / total * 100.0) if total else 0.0

    target = brs_mod.EXAM_MIN_SB if control == "exam" else brs_mod.ZACHET_MIN_SB
    done = sb >= target and graded_pct >= brs_mod.GRADED_MIN_PCT
    works_remaining = sum(
        1 for w in dg.works if not w.graded or w.submitted is False
    )

    cat_max = (brs.get("categories") or {})
    category_fill = None
    sources_note = None
    if pulse_brs:
        def _fill(points_key: str, max_key: str, cat_code: str) -> dict:
            return {
                "points": pulse_brs.get(points_key),
                "max": pulse_brs.get(max_key)
                or (cat_max.get(cat_code) or {}).get("max"),
            }

        def _brs_only(cat_code: str) -> dict:
            # категории без поля в Пульсе: max — строго из brs-semester.json
            return {"points": None,
                    "max": (cat_max.get(cat_code) or {}).get("max")}

        category_fill = {
            "БТК": _fill("current_control", "current_control_max", "БТК"),
            "БСК": _fill("semester_control", "semester_control_max", "БСК"),
            "БП": _fill("attendance", "attendance_max", "БП"),
            "БД": _brs_only("БД"),
            "БТД": _brs_only("БТД"),
            "БДОП": _fill("additional", "additional_max", "БДОП"),
        }
        diff = abs((sb_pulse or 0.0) - sb_sdo)
        if diff > 1.0:
            pr_lr_sum = sum(
                w.score or 0.0
                for w in dg.works
                if w.graded
                and w.name.casefold().startswith(
                    ("практические занятия", "лабораторная", "текущий контроль")
                )
            )
            if sb_sdo > sb and pr_lr_sum > 0 and pr_lr_sum >= diff - 1.0:
                sources_note = (
                    f"сумма работ СДО ({sb_sdo}) включает ПР/ЛР, не внесённые "
                    f"преподавателем в официальный БРС; официальный СБ = {sb}"
                )
            else:
                sources_note = f"расхождение СДО/Пульс на {round(diff, 1)} баллов"

    result = {
        "name": dg.name,
        "control": control,
        "sb": sb,
        "sb_sdo": sb_sdo,
        "sb_pulse": sb_pulse,
        "target": target,
        "done": done,
        "grade": brs_mod.grade_for_sb(sb, brs),
        "graded_pct": round(graded_pct, 1),
        "works_total": total,
        "works_graded": len(graded_works),
        "works_remaining": works_remaining,
    }
    if category_fill is not None:
        result["category_fill"] = category_fill
    if sources_note:
        result["sources_note"] = sources_note
    return result


def build_plan(
    grades: list[DisciplineGrades],
    attendances: list[DisciplineAttendance],
    lessons: list[Lesson],
    brs: dict,
    days: int = 14,
    pulse_brs: list[dict] | None = None,
) -> dict:
    """Сводный план по дисциплинам и рекомендации на ближайшие `days` дней."""
    bp_max = (brs.get("categories", {}).get("БП") or {}).get("max")

    att_by_name = {_norm(a.discipline): a for a in attendances}
    brs_by_name = {}
    for row in pulse_brs or []:
        name = row.get("discipline") or row.get(
            "name") or row.get("discipline_name")
        if name:
            brs_by_name[_norm(name)] = row
    now = datetime.now()
    horizon_ts = (now + timedelta(days=days)).timestamp()

    disciplines = []
    done_names: list[str] = []
    status_by_name: dict[str, dict] = {}
    for dg in grades:
        control = getattr(dg, "control_from_name", None) or brs_mod.control_type(dg.name, brs)
        status = plan_discipline(
            dg, control, brs, _lookup(brs_by_name, dg.name))
        att = _lookup(att_by_name, dg.name)
        status["attendance"] = {
            "attended": att.attended if att else 0,
            "total": att.total if att else 0,
            "bp_points": att.bp_points if att else None,
            "bp_max": bp_max,
        }
        disciplines.append(status)
        status_by_name[_norm(dg.name)] = status
        if status["done"]:
            done_names.append(dg.name)

    attend_rec, submit_rec, skip_lessons = [], [], []
    for lesson in lessons:
        start = _parse_dt(lesson.start)
        upcoming = start is not None and now.timestamp() <= start.timestamp() <= horizon_ts
        status = _lookup(status_by_name, lesson.discipline)
        item = {
            "discipline": lesson.discipline,
            "start": lesson.start,
            "kind": lesson.kind,
            "room": lesson.room,
            "teacher": lesson.teacher,
        }
        if status is None or not status["done"]:
            if upcoming:
                attend_rec.append(item)
        else:
            skip_lessons.append(item)

    for dg in grades:
        status = status_by_name.get(_norm(dg.name))
        if status is not None and status["done"]:
            continue
        for w in dg.works:
            if w.graded and w.submitted is not False:
                continue
            due = _parse_dt(w.due)
            if due is None or due.timestamp() > horizon_ts:
                continue
            submit_rec.append(
                {
                    "discipline": dg.name,
                    "work": w.name,
                    "kind": w.kind,
                    "due": w.due,
                    "score": w.score,
                    "max": w.max,
                    "url": w.url,
                }
            )

    submit_rec.sort(key=lambda x: x["due"] or "")
    attend_rec.sort(key=lambda x: x["start"] or "")

    return {
        "days": days,
        "disciplines": disciplines,
        "recommendations": {
            "attend": attend_rec,
            "submit": submit_rec,
            "skip_ok": {"disciplines": done_names, "lessons": skip_lessons},
        },
    }


if __name__ == "__main__":
    import json

    brs = brs_mod.load_brs()
    demo_brs = dict(brs)
    demo_brs["disciplines"] = {"Математический анализ": {"control": "exam"}}

    grades = [
        DisciplineGrades(
            name="Математический анализ",
            works=[
                Work(name="КР 1", kind="КР", score=14.0, max=20.0, graded=True,
                     submitted=True, due="2026-11-10T00:00:00"),
                Work(name="ПР 3", kind="ПР", score=0.0, max=10.0, graded=True,
                     submitted=True, due="2026-11-15T00:00:00"),
                Work(name="ЛР 2", kind="ЛР", max=15.0, submitted=False,
                     due=(datetime.now() + timedelta(days=3)).isoformat()),
            ],
        )
    ]
    attendances = [
        DisciplineAttendance(
            discipline="Математический анализ",
            marks=[
                AttendanceMark(discipline="Математический анализ",
                               start="2026-11-18T09:00:00", status="present",
                               points=1.0)
            ],
            attended=8,
            total=10,
            bp_points=12.0,
        )
    ]
    lessons = [
        Lesson(start=(datetime.now() + timedelta(days=1, hours=4)).isoformat(),
               end=(datetime.now() + timedelta(days=1, hours=6)).isoformat(),
               discipline="Математический анализ", kind="лекция",
               room="А-305", teacher="Иванова И.И."),
        Lesson(start=(datetime.now() + timedelta(days=2, hours=4)).isoformat(),
               end=(datetime.now() + timedelta(days=2, hours=6)).isoformat(),
               discipline="Математический анализ", kind="практика",
               room="Б-210", teacher="Иванова И.И."),
    ]

    report = build_plan(
        grades,
        attendances,
        lessons,
        demo_brs,
        days=14,
        pulse_brs=[
            {
                "discipline": "Математический анализ",
                "discipline_id": 12345,
                "current_control": 25.0,
                "current_control_max": 45.0,
                "semester_control": 0.0,
                "semester_control_max": 40.0,
                "attendance": 14.0,
                "attendance_max": 20.0,
                "achievements": 0.0,
                "achievements_max": 5.0,
                "additional": 0.0,
                "additional_max": 10.0,
                "total": 39.0,
                "total_max": 130.0,
            }
        ],
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))

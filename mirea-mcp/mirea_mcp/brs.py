"""Параметры БРС семестра и базовая линия mirea_plan (ADR-0003).

Числа не хардкодятся в логике: brs-semester.json обновляется сверкой с
docs/normative-acts/ при выходе нового Положения о БРС.
"""
import json

from .config import BRS_FILE

ZACHET_MIN_SB = 40.0  # минимум СБ для зачёта (шкала Положения о БРС)
EXAM_MIN_SB = 60.0  # минимум СБ для экзамена («хорошо» по шкале)
GRADED_MIN_PCT = 75.0  # допуск к семестровому контролю: % проверенных работ


def load_brs() -> dict:
    with open(BRS_FILE, encoding="utf-8") as f:
        data = json.load(f)
    for key in ("bmax", "categories", "grade_scale"):
        if key not in data:
            raise ValueError(f"brs-semester.json: отсутствует ключ '{key}'")
    return data


def grade_for_sb(sb: float, brs: dict) -> str:
    for row in sorted(brs["grade_scale"], key=lambda r: -r["min"]):
        if sb >= row["min"]:
            return row["grade"]
    return brs["grade_scale"][-1]["grade"]


def control_type(discipline: str, brs: dict) -> str:
    """
    Тип итогового контроля дисциплины: 'exam' | 'zachet'
    (по умолчанию — зачёт).
    """
    info = brs.get("disciplines", {}).get(discipline) or {}
    return info.get("control", "zachet")

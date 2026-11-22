"""Общие доменные структуры — контракт между клиентами (СДО, Пульс) и
инструментами.

Канонические термины — в GLOSSARY.md репозитория. Здесь только машинные
структуры.
"""
from dataclasses import dataclass, field


class MireaMcpError(Exception):
    """Базовая ошибка MCP-сервера. Инструменты возвращают её текст агенту."""

    hint: str | None = None

    def __init__(self, message: str, hint: str | None = None):
        super().__init__(message)
        self.hint = hint


class CredentialsMissing(MireaMcpError):
    pass


class SdoAuthError(MireaMcpError):
    pass


class PulseLoginRequired(MireaMcpError):
    pass


@dataclass
class Work:
    """Работа по дисциплине (мероприятие текущего контроля)."""

    name: str
    kind: str | None = None  # КР / ПР / ЛР / ...
    score: float | None = None  # баллы; None — ещё не проверено
    max: float | None = None  # максимум за работу
    # проверено ли; 0 баллов при graded=True считается проверенным
    graded: bool = False
    due: str | None = None  # ISO-дедлайн
    submitted: bool | None = None  # сдано ли
    url: str | None = None


@dataclass
class DisciplineGrades:
    """Баллы по дисциплине из СДО."""

    name: str
    sdo_id: str | None = None
    works: list[Work] = field(default_factory=list)
    sb: float | None = None  # сумма баллов; из строки «Сумма баллов», если она есть
    total_max: float | None = None
    # БРС-категории: Текущий контроль, Посещаемость, ...
    category_scores: dict[str, float] = field(default_factory=dict)
    # "exam" (_Экзамен) / "zachet" (_Зачет) из имени, иначе None
    control_from_name: str | None = None


@dataclass
class AttendanceMark:
    """Отметка посещаемости одного занятия."""

    discipline: str
    start: str  # ISO datetime
    kind: str | None = None  # лекция / практика
    status: str = "unknown"  # present / absent / late / unknown
    points: float | None = None  # начисленные баллы за посещение (БП)


@dataclass
class DisciplineAttendance:
    discipline: str
    marks: list[AttendanceMark] = field(default_factory=list)
    attended: int = 0
    total: int = 0
    # сумма баллов за посещение (БП), если Пульс даёт
    bp_points: float | None = None
    # честная пометка, если детализация по занятиям недоступна
    note: str | None = None


@dataclass
class Lesson:
    """Занятие из расписания Пульса."""

    start: str  # ISO datetime
    end: str  # ISO datetime
    discipline: str
    kind: str | None = None
    room: str | None = None
    teacher: str | None = None

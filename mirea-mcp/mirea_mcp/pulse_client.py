"""Асинхронный клиент Пульса (pulse.mirea.ru) поверх pymirea.

Сессия хранится в state.json (см. mirea_mcp.state): cookie-джар + токены
Keycloak. Все сетевые вызовы ленивые — импорт модуля не требует кредов
и сети. OTP-челлендж Keycloak кладётся в module-level переменную между
вызовами auth_start() и auth_otp().
"""
from __future__ import annotations

import base64
import dataclasses
import logging
import secrets
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import pymirea
from pymirea import AuthChallenge, Client, Config
from pymirea.exceptions import MireaError, MireaSessionExpired
from pymirea.pulse_session import (
    SESSION_EXPIRED_MESSAGE,
    has_pulse_auth_cookie,
    pulse_session_needs_login,
)

from . import state
from .config import LOGIN, PASSWORD
from .models import (
    AttendanceMark,
    CredentialsMissing,
    DisciplineAttendance,
    Lesson,
    MireaMcpError,
    PulseLoginRequired,
)

logger = logging.getLogger(__name__)

_MSK = ZoneInfo("Europe/Moscow")

# Ключи Keycloak-токенов внутри cookie-словаря pymirea — выделяем при сохранении.
_TOKEN_KEYS = ("access_token", "refresh_token",
               "id_token", "token_type", "expires_in")

# module-level OTP-челлендж между auth_start() и auth_otp():
# {"challenge": {...AuthChallenge.asdict...}, "saved_at": epoch}
_pending_challenge: dict | None = None
_CONFIGURED = False

# Челлендж живёт ~15 минут: код из письма одноразовый, а SSO-форма протухает.
CHALLENGE_TTL_S = 15 * 60


def _persist_challenge(stash: dict) -> None:
    st = state.load()
    pulse = st.get("pulse") or {}
    pulse["pending_challenge"] = stash
    st["pulse"] = pulse
    state.save(st)


def _clear_challenge() -> None:
    st = state.load()
    pulse = st.get("pulse") or {}
    if "pending_challenge" in pulse:
        pulse.pop("pending_challenge", None)
        st["pulse"] = pulse
        state.save(st)


def _load_persisted_challenge() -> tuple[dict | None, bool]:
    """Вернуть (челлендж, истёк_ли). Просроченный (>15 минут) удаляется из state."""
    stash = (state.load().get("pulse") or {}).get("pending_challenge")
    if not stash or not stash.get("challenge"):
        return None, False
    saved_at = stash.get("saved_at") or 0
    if time.time() - float(saved_at) > CHALLENGE_TTL_S:
        _clear_challenge()
        return None, True
    return stash, False


def _ensure_pymirea_configured() -> None:
    """pymirea требует configure(Config(...)) до создания клиентов.

    SessionCrypto нам не нужен (состояние храним в открытом виде через
    mirea_mcp.state), но Config.session_keys обязателен — генерируем
    случайный ключ один раз и держим его в state.
    """
    global _CONFIGURED
    if _CONFIGURED:
        return
    st = state.load()
    key = st.get("pymirea_session_key")
    if not key:
        key = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("ascii")
        st["pymirea_session_key"] = key
        state.save(st)
    pymirea.configure(Config(session_keys=key))
    _CONFIGURED = True


def _split_session(raw: dict) -> tuple[dict, dict]:
    cookies = {k: v for k, v in raw.items() if k not in _TOKEN_KEYS}
    tokens = {k: v for k, v in raw.items() if k in _TOKEN_KEYS}
    return cookies, tokens


def _load_session() -> dict:
    pulse = state.load().get("pulse") or {}
    session: dict = {}
    session.update(pulse.get("cookies") or {})
    session.update(pulse.get("tokens") or {})
    return session


def _persist_session(session: dict) -> None:
    cookies, tokens = _split_session(session)
    st = state.load()
    st["pulse"] = {"cookies": cookies,
                   "tokens": tokens, "saved_at": time.time()}
    state.save(st)


def _iso(epoch: float | None) -> str | None:
    if epoch is None:
        return None
    return datetime.fromtimestamp(epoch, tz=_MSK).isoformat()


def _map_error(message: str | None) -> MireaMcpError:
    text = message or "Неизвестная ошибка МИРЭА"
    if SESSION_EXPIRED_MESSAGE in text or "Перелогиньтесь" in text or "Сессия" in text:
        return PulseLoginRequired(text, hint="вызовите mirea_auth_start")
    return MireaMcpError(text)


class PulseClient:
    """Клиент Пульса: вход по SSO, расписание, посещаемость."""

    async def ensure_session(self) -> dict:
        """Восстановить сессию из state и обновить просроченный токен.

        Возвращает словарь session-cookies для pymirea.Client. Если сессии
        нет или она мертва — PulseLoginRequired с подсказкой про mirea_auth_start.
        """
        _ensure_pymirea_configured()
        session = _load_session()
        if not session or not has_pulse_auth_cookie(session):
            raise PulseLoginRequired(
                "Сессия Пульса не сохранена", hint="вызовите mirea_auth_start"
            )
        if pulse_session_needs_login(session):
            raise PulseLoginRequired(
                "Сохранённая сессия Пульса недействительна", hint="вызовите mirea_auth_start"
            )
        try:
            await pymirea.ensure_fresh_token(session)
        except MireaSessionExpired:
            raise PulseLoginRequired(
                "Сессия МИРЭА истекла", hint="вызовите mirea_auth_start"
            ) from None
        except MireaError as e:
            raise _map_error(str(e)) from None
        return session

    async def auth_start(self) -> dict:
        """Начать вход в Пульс по MIREA_LOGIN/MIREA_PASSWORD.

        Если SSO требует 2FA — челлендж сохраняется и возвращается
        {"otp_required": True}; иначе сессия сразу сохраняется в state.
        """
        global _pending_challenge
        _ensure_pymirea_configured()
        if not LOGIN or not PASSWORD:
            raise CredentialsMissing(
                "Не заданы MIREA_LOGIN / MIREA_PASSWORD",
                hint="заполните mirea-mcp/.env (см. .env.example)",
            )
        auth = pymirea.MireaAuth()
        try:
            result = await auth.login(LOGIN, PASSWORD)
        finally:
            try:
                await auth.close()
            except Exception:  # noqa: BLE001 — закрытие пула не должно ломать вход
                pass
        if result.challenge is not None:
            _pending_challenge = {
                "challenge": dataclasses.asdict(result.challenge),
                "saved_at": time.time(),
            }
            _persist_challenge(_pending_challenge)
            return {
                "otp_required": True,
                "message": "код отправлен на корпоративную почту @edu.mirea.ru",
            }
        if not result.success or not result.cookies:
            raise MireaMcpError(
                result.message or "Не удалось войти в Пульс",
                hint="проверьте MIREA_LOGIN / MIREA_PASSWORD в .env",
            )
        _pending_challenge = None
        _clear_challenge()
        _persist_session(dict(result.cookies))
        return {"otp_required": False}

    async def auth_otp(self, code: str) -> dict:
        """Завершить вход кодом из письма @edu.mirea.ru (после auth_start).

        Челлендж ищется сначала в памяти процесса, затем в state (другой
        процесс или перезапуск сервера). Просроченный (>15 минут) челлендж
        отбрасывается.
        """
        global _pending_challenge
        _ensure_pymirea_configured()
        stash = _pending_challenge
        if stash is None:
            stash, expired = _load_persisted_challenge()
            if stash is not None:
                _pending_challenge = stash
        else:
            expired = False
        if stash is None:
            if expired:
                raise PulseLoginRequired(
                    "Код подтверждения истёк (прошло больше 15 минут)",
                    hint="вызовите mirea_auth_start заново",
                )
            raise PulseLoginRequired(
                "Нет активного 2FA-челленджа", hint="сначала вызовите mirea_auth_start"
            )
        challenge = AuthChallenge(**stash["challenge"])
        auth = pymirea.MireaAuth()
        try:
            result = await auth.complete_2fa(challenge, code)
        finally:
            try:
                await auth.close()
            except Exception:  # noqa: BLE001
                pass
        if result.challenge is not None:
            _pending_challenge = {
                "challenge": dataclasses.asdict(result.challenge),
                "saved_at": time.time(),
            }
            _persist_challenge(_pending_challenge)
            raise MireaMcpError(
                result.message or "Код не подошёл, требуется новый",
                hint="повторите mirea_auth_otp с новым кодом",
            )
        if not result.success or not result.cookies:
            _pending_challenge = None
            _clear_challenge()
            raise MireaMcpError(
                result.message or "Не удалось подтвердить код", hint="вызовите mirea_auth_start заново"
            )
        _pending_challenge = None
        _clear_challenge()
        _persist_session(dict(result.cookies))
        return {"success": True}

    async def schedule(self, days: int = 7) -> list[Lesson]:
        """Расписание на days дней вперёд (от сегодня, московское время)."""
        if days < 1 or days > 31:
            raise MireaMcpError("days должен быть от 1 до 31")
        session = await self.ensure_session()
        async with Client(session_cookies=session) as client:
            result = await client.grades.get_schedule(days=days)
            await client.grades.close()
        _persist_session(session)
        if not result.success:
            raise _map_error(result.message)
        lessons: list[Lesson] = []
        for item in result.lessons or []:
            lessons.append(
                Lesson(
                    start=_iso(item.start_epoch) or "",
                    end=_iso(item.end_epoch),
                    discipline=item.name,
                    kind=item.lesson_type or None,
                    room=item.room or None,
                    teacher=item.teacher or None,
                )
            )
        return lessons

    async def attendance(
        self,
        discipline: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[DisciplineAttendance]:
        """Посещаемость по дисциплинам: отметки за занятия, счётчики, баллы БП."""
        from_date = datetime.fromisoformat(
            date_from).date() if date_from else None
        to_date = datetime.fromisoformat(date_to).date() if date_to else None

        session = await self.ensure_session()
        async with Client(session_cookies=session) as client:
            grades = await client.grades.get_grades()
            if not grades.success or not grades.subjects:
                await client.grades.close()
                _persist_session(session)
                raise _map_error(grades.message)
            subjects = grades.subjects
            if discipline:
                needle = discipline.casefold()
                subjects = [s for s in subjects if needle in s.name.casefold()]
            g = client.grades
            details: list[tuple[object, object, list[tuple[float |
                                                           None, str, str | None]] | None, str | None]] = []
            for subject in subjects:
                if not subject.discipline_id:
                    continue
                detail = await g.get_attendance_detail(subject.discipline_id)
                decoded: list[tuple[float | None,
                                    str, str | None]] | None = None
                note: str | None = None
                if detail.success and detail.entries:
                    decoded = [
                        (entry.lesson_start, _ATTEND_STATUS.get(
                            entry.attend_type, "unknown"), None)
                        for entry in detail.entries
                    ]
                else:
                    # pymirea не распознала формат — читаем ответ сами.
                    decoded = await self._fetch_attendance_raw(g, subject.discipline_id)
                    if decoded is None:
                        note = detail.message or "детализация посещаемости недоступна"
                details.append((subject, detail, decoded, note))
            await client.grades.close()
        _persist_session(session)

        out: list[DisciplineAttendance] = []
        for subject, detail, decoded, note in details:
            marks: list[AttendanceMark] = []
            attended = total = 0
            if decoded:
                if detail.success and detail.summary:
                    attended = detail.summary.present
                    total = detail.summary.total_lessons
                else:
                    total = len(decoded)
                    attended = sum(1 for _, status,
                                   _ in decoded if status == "present")
                for start_epoch, status, kind in decoded:
                    start = _iso(start_epoch)
                    lesson_date = (
                        datetime.fromtimestamp(start_epoch, tz=_MSK).date()
                        if start_epoch
                        else None
                    )
                    if from_date and lesson_date and lesson_date < from_date:
                        continue
                    if to_date and lesson_date and lesson_date > to_date:
                        continue
                    marks.append(
                        AttendanceMark(
                            discipline=subject.name,
                            start=start or "",
                            kind=kind,
                            status=status,
                            points=None,
                        )
                    )
            out.append(
                DisciplineAttendance(
                    discipline=subject.name,
                    marks=marks,
                    attended=attended,
                    total=total,
                    bp_points=subject.attendance if subject.attendance else None,
                    note=note,
                )
            )
        return out

    async def _fetch_attendance_raw(self, grades, discipline_id: str):
        """Сырой вызов GetStudentDisciplineVisitingLog + наш декодер.

        Возвращает [(lesson_start_epoch, status, kind)] или None, если ответа нет.
        """
        session_cookies = grades.session_cookies
        student_id = (session_cookies.get(
            grades._student_id_cache_key) or "").strip()
        log_id = (session_cookies.get(grades._cache_key) or "").strip()
        if not student_id or not log_id:
            logs, _ = await grades._get_visiting_logs()
            student_id = (session_cookies.get(
                grades._student_id_cache_key) or "").strip()
            log_id = (session_cookies.get(grades._cache_key)
                      or "").strip() or (logs[0] if logs else "")
        if not student_id or not log_id:
            return None
        req = grades._encode_student_discipline_visiting_log_request(
            student_id=student_id, discipline_id=discipline_id, visiting_log_id=log_id
        )
        payload, err = await grades._grpc_unary(grades.ATTENDANCE_DISCIPLINE_INFO_URL, req)
        if err or not payload:
            return None
        entries = _decode_attendance_detail(payload)
        if not entries:
            unwrapped = grades._unwrap_field_1(payload)
            if unwrapped:
                entries = _decode_attendance_detail(unwrapped)
        return entries or None

    async def brs_summary(self) -> list[dict]:
        """Сводка БРС по дисциплинам текущего семестра из Пульса.

        По каждой дисциплине: баллы и максимумы по категориям
        (текущий контроль, семестровый контроль, посещаемость, достижения,
        дополнительные) и итог. Числа — float, плюс discipline_id.
        """
        session = await self.ensure_session()
        async with Client(session_cookies=session) as client:
            result = await client.grades.get_grades()
            await client.grades.close()
        _persist_session(session)
        if not result.success or not result.subjects:
            raise _map_error(result.message)

        def num(value) -> float | None:
            if value is None:
                return None
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        summary: list[dict] = []
        for subject in result.subjects:
            summary.append(
                {
                    "discipline": subject.name,
                    "discipline_id": subject.discipline_id,
                    "current_control": num(subject.current_control),
                    "current_control_max": num(subject.current_control_max),
                    "semester_control": num(subject.semester_control),
                    "semester_control_max": num(subject.semester_control_max),
                    "attendance": num(subject.attendance),
                    "attendance_max": num(subject.attendance_max),
                    "achievements": num(subject.achievements),
                    "achievements_max": num(subject.achievements_max),
                    "additional": num(subject.additional),
                    "additional_max": num(subject.additional_max),
                    "total": num(subject.total),
                    "total_max": num(subject.total_max),
                }
            )
        return summary


_ATTEND_STATUS = {0: "unknown", 1: "absent", 2: "excused", 3: "present"}
_ATTEND_STATUS_FROM_TEXT = {
    "present": "present",
    "absent": "absent",
    "excused": "excused",
    "late": "late",
}


# ─── Декодер ответа GetStudentDisciplineVisitingLog (обход дрейфа схемы) ───
# pymirea 0.5.1 читает per-lesson отметки из top-level поля 1 (`attendancesInfo`),
# но актуальный Pulse (проверено 2026-11-22) отдаёт их в поле 4, где
# f1 = идентификатор отметки «uuid|epoch|Status», f2.f2 = занятие
# (f2/f3 — start/end epoch-секунды, f10.f2 — тип занятия). Поле 3 — справочник
# типов занятий. Ниже — минимальный protobuf-обходчик только для этого ответа.


def _pb_varint(data: bytes, pos: int) -> tuple[int, int]:
    result = 0
    shift = 0
    while True:
        byte = data[pos]
        pos += 1
        result |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return result, pos
        shift += 7


def _pb_fields(data: bytes) -> list[tuple[int, int, object]]:
    """Разобрать protobuf-сообщение в [(field, wire_type, value)]."""
    fields: list[tuple[int, int, object]] = []
    pos = 0
    while pos < len(data):
        key, pos = _pb_varint(data, pos)
        field, wt = key >> 3, key & 7
        if wt == 0:
            value, pos = _pb_varint(data, pos)
        elif wt == 1:
            value, pos = data[pos:pos + 8], pos + 8
        elif wt == 2:
            length, pos = _pb_varint(data, pos)
            value, pos = data[pos:pos + length], pos + length
        elif wt == 5:
            value, pos = data[pos:pos + 4], pos + 4
        else:
            break
        fields.append((field, wt, value))
    return fields


def _pb_text(value: object) -> str | None:
    if not isinstance(value, (bytes, bytearray)):
        return None
    try:
        text = bytes(value).decode("utf-8")
    except UnicodeDecodeError:
        return None
    return text if text and all(ch.isprintable() for ch in text) else None


def _attendance_status_from_id(attend_id: str | None) -> str:
    if not attend_id:
        return "unknown"
    tail = attend_id.rsplit("|", 1)[-1].strip().casefold()
    return _ATTEND_STATUS_FROM_TEXT.get(tail, "unknown")


def _decode_attendance_detail(payload: bytes) -> list[tuple[float | None, str, str | None]]:
    """Декодировать per-lesson отметки из актуального формата Pulse.

    Возвращает [(lesson_start_epoch, status, kind)].
    """
    entries: list[tuple[float | None, str, str | None]] = []
    for field, wt, value in _pb_fields(payload):
        if field != 4 or wt != 2:
            continue
        attend_id: str | None = None
        start: float | None = None
        kind: str | None = None
        for f2, w2, v2 in _pb_fields(value):
            if f2 == 1 and w2 == 2 and attend_id is None:
                for f3, w3, v3 in _pb_fields(v2):
                    if f3 == 1 and w3 == 2:
                        attend_id = _pb_text(v3)
                        if attend_id:
                            break
                if attend_id is None:
                    attend_id = _pb_text(v2)
            elif f2 == 2 and w2 == 2:
                # v2 — обёртка записи: f1 — дубликат id, f2 — занятие, f3 — пусто
                for f3, w3, v3 in _pb_fields(v2):
                    if f3 != 2 or w3 != 2:
                        continue
                    # v3 — сообщение занятия:
                    # f2 msg{f1 varint = start epoch}, f3 msg{f1 varint = end},
                    # f10 msg{f1 uuid типа, f2 str = тип занятия}
                    for f4, w4, v4 in _pb_fields(v3):
                        if f4 == 2 and w4 == 2 and start is None:
                            for f5, w5, v5 in _pb_fields(v4):
                                if f5 == 1 and w5 == 0:
                                    start = float(v5)
                                    break
                        elif f4 == 10 and w4 == 2 and kind is None:
                            for f5, w5, v5 in _pb_fields(v4):
                                if f5 == 2 and w5 == 2:
                                    kind = _pb_text(v5)
        entries.append((start, _attendance_status_from_id(attend_id), kind))
    return entries

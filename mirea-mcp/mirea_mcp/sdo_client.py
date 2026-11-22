"""Клиент СДО РТУ МИРЭА (Moodle, online-edu.mirea.ru).

Железное правило: пароль в Moodle НИКОГДА не отправляется (локальная auth
отключена вузом; несколько invalidlogin = блокировка аккаунта).

Режимы работы (пер-инстанс, лениво определяется при первом вызове, порядок проб):

1. REST — только когда задан config.SDO_TOKEN_OVERRIDE (MIREA_SDO_TOKEN):
   чистый wstoken, без пароля где-либо. Ручной резерв на случай, если вуз
   когда-нибудь включит мобильный сервис.
2. Восстановление сохранённой сессии: state["sdo"]["cookies"] → jar,
   валидация GET /my/ (200, без редиректа на вход).
3. OIDC — проезд по сессии Keycloak (sso.mirea.ru): куки из state["pulse"]["cookies"]
   подсаживаются в jar, GET /auth/oidc/ проходит SSO-редиректы без OTP. Локальный
   логин/пароль Keycloak здесь НЕ реализуется — требуется предварительный вход
   в Пульс (mirea_auth_start → mirea_auth_otp).

Успешная oidc-сессия (MoodleSession + sesskey) сохраняется в
state["sdo"]["cookies"] и переиспользуется при следующих запусках.

Подключение ленивое: импорт модуля не требует кредов и сети.
"""
from __future__ import annotations

import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urljoin
from zoneinfo import ZoneInfo

import httpx
from bs4 import BeautifulSoup

from . import state
from .config import SDO_BASE, SDO_TOKEN_OVERRIDE
from .models import (
    AssignTarget,
    Attachment,
    DisciplineGrades,
    MireaMcpError,
    SdoAuthError,
    Work,
)

_TIMEOUT = 30
_MSK = ZoneInfo("Europe/Moscow")
# Коды ошибок Moodle REST, после которых имеет смысл
# переключаться на OIDC-режим
_REST_FATAL_CODES = {
    "accessexception",
    "invalidtoken",
    "servicerequireslogin",
    "usernotfullysetup"
}
_RANGE_CELL = re.compile(
    r"^\s*(?P<score>-|[-\d.,\s]+)\s*/\s*(?P<max>[-\d.,\s]+)\s*$")
_WS = re.compile(r"\s+")


class SdoClient:
    """Клиент СДО. Дисциплины, баллы и дедлайны текущего семестра."""

    def __init__(self, timeout: float = _TIMEOUT) -> None:
        self._http = httpx.Client(
            base_url=SDO_BASE,
            timeout=timeout,
            follow_redirects=False,
            headers={"User-Agent": "mirea-mcp/0.1 (+sdo)"},
        )
        self._mode: str | None = None  # "rest" | "oidc"
        self._wstoken: str | None = None
        self._sesskey: str | None = None
        self._userid: int | None = None
        # course_id -> assign-страницы
        self._assign_cache: dict[str, list[dict]] = {}
        # cmid -> параметры filemanager черновика
        self._draft_ctx_cache: dict[int, dict] = {}

    # ------------------------------------------------------------------ общее

    @property
    def source(self) -> str:
        """Канал данных текущей сессии: "rest" или "oidc"."""
        self._ensure_mode()
        assert self._mode is not None
        return self._mode

    def _ensure_mode(self) -> None:
        if self._mode is not None:
            return
        if self._try_rest():
            self._mode = "rest"
            return
        if self._restore_session():
            return
        try:
            if self._try_oidc():
                self._mode = "oidc"
                self._save_session("oidc")
                return
        except SdoAuthError:
            raise  # SSO требует входа в Пульс — подсказка уже в ошибке
        raise SdoAuthError(
            "Не удалось войти в СДО: нет ни REST-токена (MIREA_SDO_TOKEN), "
            "ни сохранённой сессии, ни SSO-сессии Пульса.",
            hint=self._SSO_HINT,
        )

    # ------------------------------------------------------ куки сессии (state)

    @staticmethod
    def _iter_cookie_dicts(cookies) -> list[dict]:
        """Нормализация: список dict'ов или dict name->value/dict."""
        if isinstance(cookies, dict):
            cookies = [
                {"name": k, **v} if isinstance(v,
                                               dict) else {"name": k, "value": v}
                for k, v in cookies.items()
            ]
        return [c for c in (cookies or []) if isinstance(c, dict) and c.get("name")]

    def _seed_cookies(self, cookies, *, mirea_only: bool = True) -> int:
        n = 0
        for c in self._iter_cookie_dicts(cookies):
            domain = (c.get("domain") or "").lstrip(".")
            if not domain and mirea_only:
                # Куки из state["pulse"] хранятся как {name: value} без домена.
                # Доменные куки SSO (KEYCLOAK_*, AUTH_SESSION_ID) должны доезжать
                # до sso.mirea.ru в цепочке редиректов /auth/oidc/ — поэтому
                # бездоменным ставим общий parent-domain.
                domain = "mirea.ru"
            if mirea_only and domain and not domain.endswith("mirea.ru"):
                continue
            value = c.get("value", "")
            value = "" if value is None else str(value)
            self._http.cookies.set(
                str(c["name"]), value,
                domain=("." + domain) if domain else "",
                path=c.get("path") or "/",
            )
            n += 1
        return n

    def _save_session(self, mode: str) -> None:
        jar = [
            {"name": c.name, "value": c.value,
                "domain": c.domain or "", "path": c.path or "/"}
            for c in self._http.cookies.jar
        ]
        st = state.load()
        sdo = st.setdefault("sdo", {})
        sdo["cookies"] = jar
        sdo["mode"] = mode
        sdo["saved_at"] = time.time()
        state.save(st)

    def _restore_session(self) -> bool:
        """Восстановить ранее сохранённую Moodle-сессию из state, если она жива."""
        sdo = state.load().get("sdo") or {}
        jar = sdo.get("cookies") or []
        if not jar:
            return False
        self._seed_cookies(jar, mirea_only=False)
        mode = sdo.get("mode")
        if mode != "oidc":
            # legacy-режим "browser" (локальная форма с паролем) удалён — пере-auth через OIDC
            return False
        if self._session_valid():
            self._mode = mode
            self._extract_sesskey()
            return True
        return False

    def _session_valid(self) -> bool:
        """Дешёвая проверка: /my/ отдаёт 200 и не уводит на страницу входа."""
        try:
            resp = self._http.get("/my/", follow_redirects=True)
        except httpx.HTTPError:
            return False
        final = str(resp.url)
        return resp.status_code == 200 and "login" not in final and "sso.mirea.ru" not in final

    def _extract_sesskey(self, html: str | None = None) -> bool:
        if html is None:
            try:
                html = self._http.get("/my/").text
            except httpx.HTTPError:
                return False
        soup = BeautifulSoup(html, "html.parser")
        inp = soup.find("input", {"name": "sesskey"})
        m = re.search(r'"sesskey"\s*:\s*"([a-zA-Z0-9]+)"', html)
        self._sesskey = (inp.get("value") if inp else None) or (
            m.group(1) if m else None)
        return self._sesskey is not None

    # ------------------------------------------------------------------ REST

    def _get_token(self) -> str | None:
        """wstoken только из MIREA_SDO_TOKEN или сохранённого state.

        Пароль в Moodle НИКОГДА не отправляется: обмен логин/пароль на токен
        (login/token.php) удалён — локальная auth отключена вузом, а каждый
        invalidlogin приближает блокировку аккаунта.
        """
        if SDO_TOKEN_OVERRIDE:
            return SDO_TOKEN_OVERRIDE.strip()
        return (state.load().get("sdo") or {}).get("wstoken") or None

    def _rest(self, function: str, fatal_ok: bool = False, **params) -> dict | list | None:
        """Вызов REST-функции Moodle. Возвращает None при фатальной ошибке режима."""
        token = self._get_token()
        if not token:
            return None
        query = {
            "wstoken": token,
            "moodlewsrestformat": "json",
            "wsfunction": function,
            **params,
        }
        resp = self._http.get("/webservice/rest/server.php", params=query)
        try:
            data = resp.json()
        except ValueError as exc:
            raise SdoAuthError(
                f"СДО вернул не-JSON для {function} (HTTP {resp.status_code}).") from exc
        if isinstance(data, dict) and data.get("exception"):
            code = str(data.get("errorcode", ""))
            message = data.get("message") or code or "unknown error"
            if code in _REST_FATAL_CODES or code in {"invalidlogin"}:
                if fatal_ok:
                    return None
                raise SdoAuthError(
                    f"REST {function} отклонён: {message}",
                    hint="Токен не подходит; передайте актуальный через MIREA_SDO_TOKEN.",
                )
            raise SdoAuthError(f"REST {function}: {message}")
        return data

    def _try_rest(self) -> bool:
        try:
            info = self._rest("core_webservice_get_site_info", fatal_ok=True)
        except SdoAuthError:
            return False
        if not isinstance(info, dict) or not info.get("userid"):
            return False
        self._userid = int(info["userid"])
        return True

    # ------------------------------------------------------------------ OIDC (SSO-ride)

    _SSO_HINT = (
        "Сначала выполните вход в Пульс: mirea_auth_start → mirea_auth_otp "
        "(код на корпоративной почте), затем повторите вызов"
    )

    def _try_oidc(self) -> bool:
        """Войти в СДО через Moodle OIDC, проехав по сессии Keycloak из Пульса.

        Кидает SdoAuthError с подсказкой про mirea_auth_start/mirea_auth_otp,
        если SSO перенаправил на форму логина Keycloak.
        """
        st = state.load()
        pulse_cookies = (st.get("pulse") or {}).get("cookies") or []
        # только *.mirea.ru (включая sso.mirea.ru)
        self._seed_cookies(pulse_cookies)
        try:
            resp = self._http.get("/auth/oidc/", follow_redirects=False)
            resp = self._drain_redirects(resp)
            # Keycloak response_mode=form_post: вместо финального редиректа
            # отдаёт авто-сабмитящуюся HTML-форму с code/state — сабмитим её сами.
            form = self._parse_form_post(resp)
            if form is not None:
                action, fields = form
                resp = self._drain_redirects(self._http.post(
                    action, data=fields, follow_redirects=False))
        except httpx.HTTPError as exc:
            raise SdoAuthError(
                f"Сетевая ошибка при обращении к SSO: {exc}", hint=self._SSO_HINT) from exc
        final = str(resp.url)
        if "sso.mirea.ru" in final:
            # Keycloak не признал сессию и показал форму логина — свой OTP-флоу не реализуем
            raise SdoAuthError(
                "SSO (sso.mirea.ru) требует входа: сохранённая сессия Пульса отсутствует или истекла.",
                hint=self._SSO_HINT,
            )
        if resp.status_code >= 400 or "login/index.php" in final:
            return False
        if not any(c.name == "MoodleSession" for c in self._http.cookies.jar):
            return False
        return self._extract_sesskey(resp.text)

    def _drain_redirects(self, resp: httpx.Response, limit: int = 8) -> httpx.Response:
        """Пройти цепочку редиректов вручную (GET по Location)."""
        from urllib.parse import urljoin

        current = resp
        for _ in range(limit):
            if current.status_code not in (301, 302, 303, 307, 308):
                break
            loc = current.headers.get("location")
            if not loc:
                break
            current = self._http.get(
                urljoin(str(current.url), loc), follow_redirects=False)
        return current

    @staticmethod
    def _parse_form_post(resp: httpx.Response) -> tuple[str, dict[str, str]] | None:
        """Распарсить авто-сабмитящуюся form_post-страницу Keycloak (code/state).

        Возвращает (action, fields) либо None, если это не такая форма.
        """
        m = re.search(
            r"<form[^>]*?action=[\"']([^\"']+)[\"'][^>]*>(.*?)</form>", resp.text, re.S | re.I)
        if not m:
            return None
        action, body = m.group(1), m.group(2)
        if "online-edu.mirea.ru" not in action:
            return None
        fields: dict[str, str] = {}
        for tag in re.findall(r"<input[^>]+>", body, re.I):
            nm = re.search(r"name=[\"']([^\"']+)[\"']", tag, re.I)
            if not nm:
                continue
            val = re.search(r"value=[\"']([^\"']*)[\"']", tag, re.I)
            fields[nm.group(1)] = val.group(1) if val else ""
        if "code" not in fields:
            return None
        return action, fields

    # ------------------------------------------------------------------ сдача работ и дедлайны (browser/oidc)

    @staticmethod
    def _norm_name(s: str) -> str:
        return _WS.sub(" ", s).strip().casefold()

    def _course_assignments(self, course_id) -> list[dict]:
        """Страницы заданий курса: ссылка, название, срок, статус сдачи, файлы.

        Результат кэшируется в рамках инстанса (один вызов инструмента — один
        проход по страницам курса).
        """
        key = str(course_id)
        if key in self._assign_cache:
            return self._assign_cache[key]
        assigns: list[dict] = []
        try:
            html = self._get_page(f"/course/view.php?id={course_id}")
        except SdoAuthError:
            self._assign_cache[key] = []
            return []
        soup = BeautifulSoup(html, "html.parser")
        seen: dict[int, dict] = {}
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/mod/assign/view.php" not in href:
                continue
            m = re.search(r"[?&]id=(\d+)", href)
            if not m:
                continue
            aid = int(m.group(1))
            if aid in seen:
                continue
            name = _WS.sub(" ", a.get_text(" ", strip=True)).strip()
            if not name:
                continue
            info: dict = {"id": aid, "name": name,
                          "url": urljoin(SDO_BASE, href)}
            try:
                info.update(self._parse_assign_page(
                    self._get_page(href)))
            except SdoAuthError:
                pass  # страница недоступна — оставляем null'ы
            seen[aid] = info
        assigns = list(seen.values())
        self._assign_cache[key] = assigns
        return assigns

    @staticmethod
    def _parse_assign_page(html: str) -> dict:
        """Срок сдачи, статус отправки и число файлов со страницы задания."""
        soup = BeautifulSoup(html, "html.parser")
        nfiles = len(soup.select(
            'a[href*="assignsubmission_file/submission_files"]'))
        submitted: bool | None = None
        status_el = soup.select_one(
            "[data-region='submission-status']") or soup.select_one(".submissionstatus")
        if status_el is not None:
            t = status_el.get_text(" ", strip=True).casefold()
            if "отправлен" in t:
                submitted = True
            elif "нет ответа" in t or "не отправлен" in t or "отправить работу" in t:
                submitted = False
        if submitted is None:
            # запасной вариант по тексту страницы (разметка статуса отличается между темами)
            page = soup.get_text(" ", strip=True).casefold()
            if "отправлено для оценивания" in page or "отправлено на проверку" in page or nfiles:
                submitted = True
            elif (
                "отправить работу" in page
                or "нет ответа" in page
                or "не представлены" in page  # «Ответы на задание еще не представлены»
            ):
                submitted = False
        due = None
        dates_el = soup.select_one("[data-region='activity-dates']")
        if dates_el is not None:
            dtext = dates_el.get_text(" ", strip=True)
            m = re.search(
                r"(?:Срок сдачи|Доступно до)\s*:\s*(.+?)(?:\s{2,}|Открыто|$)", dtext)
            if m:
                due = _parse_ru_datetime(m.group(1))
        return {"submitted": submitted, "due": due, "nfiles": nfiles}

    def _enrich_works(self, course_id, works: list[Work]) -> None:
        """Заполнить Work.submitted/due/url по assign-страницам курса.

        Маппинг по нормализованному имени (casefold + вложенность) в пределах
        одного курса; без уверенного матча work не трогается (честные null).
        """
        assigns = self._course_assignments(course_id)
        if not assigns:
            return
        used: set[int] = set()
        for w in works:
            nw = self._norm_name(w.name)
            if not nw:
                continue
            best = None
            for a in assigns:
                if a["id"] in used:
                    continue
                na = self._norm_name(a["name"])
                if na and (nw in na or na in nw):
                    best = a
                    break
            if best is None:
                continue
            used.add(best["id"])
            w.url = w.url or best["url"]
            w.submitted = best.get("submitted")
            w.due = best.get("due")

    def _get_page(self, path: str) -> str:
        resp = self._http.get(path, follow_redirects=True)
        if resp.status_code in (301, 302, 303, 307, 308):
            location = urljoin(str(resp.url), resp.headers.get("Location", ""))
            if "login" in location:
                raise SdoAuthError("Сессия СДО истекла, повторите вход.")
            resp = self._http.get(location, follow_redirects=True)
        if resp.status_code >= 400:
            raise SdoAuthError(f"HTTP {resp.status_code} для {path}")
        if "login/index.php" in str(resp.url):
            raise SdoAuthError(
                "СДО перенаправил на страницу входа: сессия истекла.")
        resp.encoding = "utf-8"
        return resp.text

    def _ajax(self, methodname: str, **args):
        """Вызывать AJAX-эндпоинт веб-интерфейса (как делает сам сайт)."""
        if not self._sesskey:
            raise SdoAuthError("Нет sesskey браузерной сессии.")
        resp = self._http.post(
            "/lib/ajax/service.php",
            params={"sesskey": self._sesskey, "info": methodname},
            json=[{"index": 0, "methodname": methodname, "args": args}],
        )
        if resp.status_code >= 400:
            raise SdoAuthError(f"AJAX {methodname}: HTTP {resp.status_code}")
        payload = resp.json()
        item = payload[0] if isinstance(payload, list) and payload else payload
        if not isinstance(item, dict):
            raise SdoAuthError(f"AJAX {methodname}: неожиданный ответ")
        if item.get("error"):
            raise SdoAuthError(f"AJAX {methodname}: {item.get('error')}")
        return item.get("data")

    def _browser_courses(self) -> list[dict]:
        data = self._ajax(
            "core_course_get_enrolled_courses_by_timeline_classification",
            classification="all",
            limit=0,
            offset=0,
            sort="fullname",
        ) or {}
        return list(data.get("courses", []))

    # ------------------------------------------------------------------ данные

    def _courses(self) -> list[dict]:
        self._ensure_mode()
        if self._mode == "rest":
            data = self._rest("core_enrol_get_users_courses",
                              userid=self._userid) or []
            return list(data)
        return self._browser_courses()

    def disciplines(self) -> list[DisciplineGrades]:
        """Дисциплины текущего семестра с баллами (для plan_tools)."""
        return self._grades_for(None)

    def grades(self, discipline_name: str | None = None) -> list[DisciplineGrades]:
        """Баллы по дисциплинам: работы, баллы, флаг проверено."""
        return self._grades_for(discipline_name)

    def _grades_for(self, discipline_name: str | None) -> list[DisciplineGrades]:
        self._ensure_mode()
        courses = self._courses()
        result: list[DisciplineGrades] = []
        for course in courses:
            name = _WS.sub(" ", str(course.get("fullname", ""))).strip()
            if not name:
                continue
            if discipline_name and discipline_name.lower() not in name.lower():
                continue
            course_id = course.get("id")
            category_scores: dict[str, float] = {}
            official_sb: float | None = None
            if self._mode == "rest":
                works = [
                    w for w in self._rest_works(course_id)
                    if not self._is_aggregate_name(w.name)
                ]
            else:
                works, category_scores, official_sb = self._browser_works(
                    course_id)
                self._enrich_works(course_id, works)
            sb = official_sb
            if sb is None:
                sb = sum(
                    w.score for w in works if w.score is not None) if works else None
            total_max = sum(
                w.max for w in works if w.max is not None) if works else None
            result.append(
                DisciplineGrades(
                    name=name,
                    sdo_id=str(course_id),
                    works=works,
                    sb=sb,
                    total_max=total_max or None,
                    category_scores=category_scores,
                    control_from_name=_control_from_name(name),
                )
            )
        return result

    # ---------------- REST: работы из grade items + assignments

    def _rest_works(self, course_id) -> list[Work]:
        items: dict[str, Work] = {}
        data = self._rest("gradereport_user_get_grade_items",
                          courseid=course_id) or {}
        for row in (data.get("grade_items") or []):
            itemname = _WS.sub(" ", str(row.get("itemname") or "")).strip()
            if not itemname:
                continue
            graderaw = row.get("graderaw")
            grademax = row.get("grademax")
            items[itemname] = Work(
                name=itemname,
                score=float(graderaw) if graderaw is not None else None,
                max=float(grademax) if grademax is not None else None,
                graded=graderaw is not None,
            )
        # Дедлайны и статус сдачи из модулей заданий
        data = self._rest("mod_assign_get_assignments", **
                          {"courseids[0]": course_id}) or {}
        for course in data.get("courses") or []:
            for assign in course.get("assignments") or []:
                aname = _WS.sub(" ", str(assign.get("name") or "")).strip()
                if not aname:
                    continue
                due = assign.get("duedate")
                due_iso = time.strftime(
                    "%Y-%m-%dT%H:%M:%S", time.gmtime(int(due))) if due else None
                submitted = None  # per-user статус сдачи REST из этого вызова не отдаёт
                work = items.get(aname)
                if work is None:
                    items[aname] = Work(
                        name=aname,
                        due=due_iso,
                        submitted=submitted,
                    )
                else:
                    work.due = due_iso
                    work.submitted = submitted
        return list(items.values())

    # ---------------- браузерный режим: HTML-таблица оценок

    # БРС-агрегаты таблицы оценок — это НЕ работы (категории и итоги).
    # Совпадение точное (после strip, case-insensitive): «Балл за экзамен» сюда не входит.
    _AGGREGATE_NAMES = {
        "элемент оценивания",
        "текущий контроль",
        "посещаемость",
        "семестровый контроль",
        "трудовая деятельность",
        "достижения",
        "дополнительные баллы",
        "сумма баллов",
        "оценка за промежуточную аттестацию",
    }
    _OFFICIAL_SUM_NAME = "сумма баллов"

    @classmethod
    def _is_aggregate_name(cls, name: str) -> bool:
        return name.strip().lower() in cls._AGGREGATE_NAMES

    def _browser_works(self, course_id) -> tuple[list[Work], dict[str, float], float | None]:
        """Работы, баллы БРС-категорий и официальная «Сумма баллов» (None если нет строки)."""
        html = self._get_page(f"/grade/report/user/index.php?id={course_id}")
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", class_="user-grade")
        if table is None:
            return [], {}, None
        works: list[Work] = []
        category_scores: dict[str, float] = {}
        official_sb: float | None = None
        for tr in table.find_all("tr"):
            th = tr.find("th")
            if th is None:
                continue
            classes = set(th.get("class") or [])
            if "category" in classes or "baggt" in classes:  # заголовок категории / итог
                continue
            name_el = th.find(class_="gradeitemheader")
            name = _WS.sub(" ", (name_el or th).get_text(
                " ", strip=True)).strip()
            if not name or name == "-":
                continue
            grade_cell = tr.find("td", class_="column-grade")
            range_cell = tr.find("td", class_="column-range")
            score = None
            max_: float | None = None
            # Максимум читаем из колонки «Диапазон» независимо («0–7»)
            if range_cell is not None:
                rtext = range_cell.get_text(" ", strip=True).replace("–", "-")
                rm = re.search(r"-\s*([\d.,\s]+)\s*$", rtext)
                if rm:
                    max_ = _to_float(rm.group(1))
            graded = False
            gtext = grade_cell.get_text(" ", strip=True) if grade_cell else ""
            m = _RANGE_CELL.match(gtext.replace("–", "-"))
            if m:
                raw_score = m.group("score").strip()
                if raw_score not in ("-", ""):
                    graded = True
                    score = _to_float(raw_score)
                if max_ is None:
                    max_ = _to_float(m.group("max"))
            elif gtext and gtext.strip() not in ("-", "–"):
                score = _to_float(gtext)
                graded = score is not None
            lowered = name.lower()
            if lowered in self._AGGREGATE_NAMES:
                # БРС-агрегат: в работы не идёт; балл — в категории (или официальную сумму)
                if score is not None:
                    if lowered == self._OFFICIAL_SUM_NAME:
                        official_sb = score
                    else:
                        category_scores[name] = score
                continue
            work = Work(name=name, score=score, max=max_, graded=graded)
            link = th.find("a", href=True)
            if link and link["href"].startswith("/"):
                work.url = urljoin(SDO_BASE, link["href"])
            works.append(work)
        return works, category_scores, official_sb

    # ---------------------------------------------------------------- дедлайны

    def due_works(self, days: int = 14) -> list[dict]:
        """
        Предстоящие работы с дедлайнами
        (по всем дисциплинам, dict'и с полем discipline).
        """
        self._ensure_mode()
        if self._mode == "rest":
            return self._rest_due_works(days)
        return self._browser_due_works(days)

    def _rest_due_works(self, days: int) -> list[dict]:
        now = time.time()
        cutoff = now + days * 86400
        out: list[dict] = []
        for course in self._courses():
            cname = _WS.sub(" ", str(course.get("fullname", ""))).strip()
            data = self._rest("mod_assign_get_assignments", **
                              {"courseids[0]": course.get("id")}) or {}
            for c in data.get("courses") or []:
                for assign in c.get("assignments") or []:
                    due = assign.get("duedate")
                    if not due or not (now <= int(due) <= cutoff):
                        continue
                    out.append(
                        {
                            "discipline": cname,
                            "name": _WS.sub(" ", str(assign.get("name") or "")).strip(),
                            "due": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(int(due))),
                            "submitted": None,
                        }
                    )
        out.sort(key=lambda w: w["due"])
        return out

    def _browser_due_works(self, days: int) -> list[dict]:
        """Несданные работы с дедлайном в окне days — из обогащённых works."""
        now = time.time()
        cutoff = now + days * 86400
        out: list[dict] = []
        for g in self.grades(None):
            for w in g.works:
                if not w.due or w.submitted:
                    continue
                try:
                    due_ts = datetime.fromisoformat(w.due).timestamp()
                except ValueError:
                    continue
                if now <= due_ts <= cutoff:
                    out.append(
                        {
                            "discipline": g.name,
                            "name": w.name,
                            "due": w.due,
                            "submitted": w.submitted,
                            "url": w.url,
                        }
                    )
        out.sort(key=lambda w: w["due"])
        return out

    # ------------------------------------- запись: ответы на работы (ADR-0006)
    #
    # Механика Moodle (reverse-engineering GET-инспекцией форм, 2026-11-22):
    # - редактирование ответа: GET view.php?id=CMID&action=editsubmission;
    #   на странице — форма с action=savesubmission и hidden-полем
    #   files_filemanager=<itemid черновика> (input#id_files_filemanager);
    #   JSON-конфиг M.form_filemanager.init: client_id, itemid, maxbytes,
    #   areamaxbytes, context.id, author, filepicker.defaultlicense,
    #   filepicker.repositories[type=upload].id (репозиторий «Загрузить файл»).
    #   ВАЖНО: itemid перевыдаётся при каждом открытии формы, а повторное
    #   открытие пересевивает черновик ТОЛЬКО из сохранённого ответа: файлы,
    #   поэтапно загруженные в предыдущий itemid, теряются. Поэтому контекст
    #   черновика пиннуется по cmid до успешной отправки (submission_send);
    #   resolve_assign/reload_submission пин НЕ сбрасывают.
    # - загрузка файла: multipart POST /repository/repository_ajax.php
    #   ?action=upload с query repo_id, env=filemanager, sesskey, client_id,
    #   itemid, maxbytes, areamaxbytes, ctx_id, savepath=/; тело: repo_upload_file,
    #   title, author, license, itemid. Конфликт имён -> {"event":"fileexists"}.
    # - операции над файлами черновика: POST urlencoded
    #   /repository/draftfiles_ajax.php?action=<action> с sesskey, client_id,
    #   itemid, filepath; переименование — updatefile (filename, newfilename,
    #   newfilepath=/), удаление — deleteselected (selected=<JSON-массив
    #   объектов {"filepath": "/", "filename": ...}> — Moodle вызывает
    #   get_filepath() на каждом элементе, голые строки дают null).
    # - атомарная замена содержимого: upload нового файла, затем
    #   repository_ajax.php?action=overwrite (existingfilename/existingfilepath/
    #   newfilename/newfilepath) — тот же вызов, что у диалога «файл существует».
    # - сохранение ответа: POST view.php (форма редактирования) со всеми hidden
    #   полями + files_filemanager=<itemid> + нажатой кнопкой. Когда включены
    #   черновики, есть две кнопки: submitbutton («Сохранить» — черновик) и
    #   submitbutton2 («Отправить задание»); при выключенных черновиках одна
    #   кнопка «Сохранить», которая отправляет ответ преподавателю сразу
    #   (на online-edu черновики выключены → submission_save == submission_send).
    # - submissionstatement (чекбокс «я принимаю условия») — если присутствует
    #   в форме, отправляется как submissionstatement=1.
    # Каждая мутация перевытаскивает sesskey со страницы задания (пиннутый
    # sesskey формы может протухнуть в длинной сессии); при ответ Moodle о
    # невалидном sesskey форма редактирования перевыпускается ОДИН раз (пин
    # обновляется под новый itemid) и операция повторяется. После мутации
    # вызывающий обязан показать draft_list(target) — поэтапное состояние
    # черновика, которое submit_post сохранил бы в ответе.

    def _require_write_mode(self) -> None:
        """
        Запись в СДО существует только в браузерной OIDC-сессии (ADR-0004/0006).
        """
        self._ensure_mode()
        if self._mode != "oidc":
            raise SdoAuthError(
                "Запись в СДО недоступна в текущем режиме.",
                hint="запись доступна только в браузерной OIDC-сессии; "
                "выполните вход в Пульс (mirea_auth_start)",
            )

    def _fresh_sesskey(self, html: str | None = None) -> str:
        """Перевытащить sesskey перед каждой мутацией (ADR-0006)."""
        if not self._extract_sesskey(html):
            raise SdoAuthError(
                "Не удалось получить sesskey СДО; повторите вход.", hint=self._SSO_HINT)
        assert self._sesskey is not None
        return self._sesskey

    @staticmethod
    def _ajax_json(resp: httpx.Response, what: str) -> Any:
        """Распарсить JSON-ответ repository_ajax / draftfiles_ajax.

        Принимает ЛЮБОЕ валидное JSON-значение (dict/list/bool/str — Moodle
        отдаёт, например, голый `true` для action=overwrite); не-JSON →
        MireaMcpError. Потребители dict-специфичных полей обязаны проверять
        тип (см. _raise_ajax_error, _is_sesskey_failure).
        """
        try:
            return resp.json()
        except ValueError as exc:
            raise MireaMcpError(
                f"СДО вернул не-JSON для «{what}» (HTTP {resp.status_code}).") from exc

    # ---------------- разбор страницы задания (общий для resolve/reload)

    @staticmethod
    def _parse_attachments(soup: BeautifulSoup) -> list[Attachment]:
        """Вложения ответа: ссылки assignsubmission_file/submission_files."""
        out: list[Attachment] = []
        for a in soup.select('a[href*="assignsubmission_file/submission_files"]'):
            href = a["href"]
            text = _WS.sub(" ", a.get_text(" ", strip=True)).strip()
            filename = text or unquote(
                href.rstrip("/").rsplit("/", 1)[-1].split("?", 1)[0])
            if filename:
                out.append(Attachment(filename=filename, fileurl=href))
        return out

    @staticmethod
    def _assign_status(soup: BeautifulSoup) -> tuple[str, bool]:
        """(status, editable) из «Состояние ответа» и кнопок редактирования.

        status: no_answer | draft | submitted | graded.
        editable: на странице есть форма editsubmission/submitforgrading —
        это ground truth того, что Moodle сейчас примет изменения ответа.
        """
        state_text = ""
        graded = False
        for tr in soup.select(".submissionstatustable tr"):
            th, td = tr.find("th"), tr.find("td")
            if th is None or td is None:
                continue
            if "submissiongraded" in (td.get("class") or []):
                graded = True
            label = _WS.sub(" ", th.get_text(" ", strip=True))
            if "Состояние ответа" in label:
                state_text = _WS.sub(" ", td.get_text(
                    " ", strip=True)).casefold()
        if not state_text:
            # запасной вариант по тексту страницы (темы отличаются разметкой)
            page = soup.get_text(" ", strip=True).casefold()
            if "черновик" in page:
                state_text = "черновик"
            elif "отправлено для оценивания" in page or "отправлено на проверку" in page:
                state_text = "отправлено"
            elif "нет ответа" in page or "не представлены" in page:
                state_text = "не представлены"
        if graded:
            status = "graded"
        elif "черновик" in state_text:
            status = "draft"
        elif "отправлен" in state_text:
            status = "submitted"
        elif "не представлен" in state_text or "нет ответа" in state_text:
            status = "no_answer"
        else:
            status = "no_answer" if not state_text else "submitted"
        editable = bool(
            soup.find("input", {"name": "action", "value": "editsubmission"})
            or soup.find("input", {"name": "action", "value": "submitforgrading"}))
        return status, editable

    @staticmethod
    def _assign_due(soup: BeautifulSoup) -> str | None:
        """Дедлайн из блока activity-dates («Срок сдачи: ...»), ISO Москва."""
        dates_el = soup.select_one("[data-region='activity-dates']")
        if dates_el is None:
            return None
        dtext = dates_el.get_text(" ", strip=True)
        m = re.search(
            r"(?:Срок сдачи|Доступно до)\s*:\s*(.+?)(?:\s{2,}|Открыто|$)", dtext)
        return _parse_ru_datetime(m.group(1)) if m else None

    def _parse_assign_target(self, html: str, cmid: int) -> AssignTarget:
        soup = BeautifulSoup(html, "html.parser")
        name_el = soup.find("h1") or soup.find("h2")
        name = _WS.sub(" ", name_el.get_text(" ", strip=True)
                       ).strip() if name_el else ""
        course_name = ""
        for a in soup.select("#page-navbar a[href], nav a[href]"):
            if "course/view.php" in (a.get("href") or ""):
                course_name = _WS.sub(" ", a.get_text(" ", strip=True)).strip()
        status, editable = self._assign_status(soup)
        return AssignTarget(
            url=f"{SDO_BASE}/mod/assign/view.php?id={cmid}",
            cmid=cmid,
            name=name,
            course_name=course_name,
            status=status,
            editable=editable,
            due=self._assign_due(soup),
            attachments=self._parse_attachments(soup),
        )

    @staticmethod
    def _assign_cmid(url: str) -> int:
        m = re.search(r"[?&]id=(\d+)", url)
        if not m or "/mod/assign/view.php" not in url:
            raise MireaMcpError(
                "Ссылка не распознана: не страница задания СДО.",
                hint="ожидается адрес вида "
                "https://online-edu.mirea.ru/mod/assign/view.php?id=NNN",
            )
        return int(m.group(1))

    def resolve_assign(self, url: str) -> AssignTarget:
        """
        Валидировать страницу задания в цель записи (assign + файловый ответ).

        Без редактируемого ответа или без файлового submission-плагина кидает
        MireaMcpError со специфичной русской подсказкой.
        """
        self._require_write_mode()
        cmid = self._assign_cmid(url)
        target = self._parse_assign_target(
            self._get_page(f"/mod/assign/view.php?id={cmid}"), cmid)
        if not target.editable:
            raise MireaMcpError(
                "Ответ на работу не редактируется.",
                hint="ответ отправлен и редактирование запрещено"
                if target.status in {"submitted", "graded"}
                else "работа сейчас не принимает изменения ответа",
            )
        self._draft_context(target)  # валидирует файловый тип ответа
        return target

    def reload_submission(self, target: AssignTarget) -> list[Attachment]:
        """Перечитать страницу: обновить attachments/status/editable на месте."""
        html = self._get_page(f"/mod/assign/view.php?id={target.cmid}")
        soup = BeautifulSoup(html, "html.parser")
        target.status, target.editable = self._assign_status(soup)
        target.due = self._assign_due(soup)
        target.attachments = self._parse_attachments(soup)
        # пин черновика НЕ сбрасываем: пересев происходит только при
        # перевыпуске формы editsubmission, а reload её не открывает.
        # Пин живёт до успешной submission_send.
        return target.attachments

    # ---------------- параметры черновика (filemanager)

    @staticmethod
    def _fm_config(html: str) -> dict:
        """
        JSON-конфиг M.form_filemanager.init со страницы редактирования ответа.
        """
        marker = "M.form_filemanager.init(Y,"
        i = html.find(marker)
        if i == -1:
            return {}
        j = html.find("{", i + len(marker))
        if j == -1:
            return {}
        depth = 0
        for k in range(j, len(html)):
            if html[k] == "{":
                depth += 1
            elif html[k] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(html[j:k + 1])
                    except ValueError:
                        return {}
        return {}

    def _draft_context(self, target: AssignTarget, html: str | None = None) -> dict:
        """
        Параметры файлового менеджера черновика: itemid, client_id, контекст.

        Лениво создаётся по cmid и пиннуется до успешной submission_send:
        itemid перевыдаётся при каждом открытии editsubmission, а повторное
        открытие пересевивает черновик только из сохранённого ответа — ранее
        поэтапно загруженные файлы при этом терялись бы.
        """
        cached = self._draft_ctx_cache.get(target.cmid)
        if cached:
            return cached
        if html is None:
            html = self._get_page(
                f"/mod/assign/view.php?id={target.cmid}&action=editsubmission")
        soup = BeautifulSoup(html, "html.parser")
        fm_input = soup.find("input", {"name": "files_filemanager"})
        if fm_input is None:
            if soup.find(
                "input",
                {"name": "action", "value": "savesubmission"}
            ) is None:
                raise MireaMcpError(
                    "Ответ больше не редактируется.",
                    hint="повторите resolve_assign: статус работы мог измениться",
                )
            raise MireaMcpError(
                "У работы нет файлового типа ответа.",
                hint="у работы нет файлового типа ответа — "
                "прикрепление файлов для этого задания не поддерживается",
            )
        fm = self._fm_config(html)
        fp = fm.get("filepicker") or {}
        repositories = fp.get("repositories") or {}
        upload_repo = next(
            (r for r in repositories.values() if r.get("type") == "upload"),
            None
        )
        if upload_repo is None:
            raise MireaMcpError(
                "У работы нет репозитория загрузки файлов.",
                hint="у работы нет файлового типа ответа",
            )
        ctx = {
            "itemid": int(fm_input.get("value") or fm.get("itemid") or 0),
            "client_id": fm.get("client_id", ""),
            "ctx_id": (fm.get("context") or {}).get("id"),
            "maxbytes": fm.get("maxbytes", -1),
            "areamaxbytes": fm.get("areamaxbytes", -1),
            "author": fm.get("author") or fp.get("author") or "",
            "license": fp.get("defaultlicense") or "allrightsreserved",
            "upload_repo_id": upload_repo["id"],
        }
        self._draft_ctx_cache[target.cmid] = ctx
        return ctx

    # ---------------- sesskey и повторная попытка мутации

    def _view_sesskey(self, target: AssignTarget) -> str:
        """Свежий sesskey со страницы задания (без перевыпуска формы).

        Страница задания, а не /my/: у pinned-формы sesskey может протухнуть
        в длинной сессии, и каждая мутация обязана взять актуальный.
        """
        html = self._get_page(f"/mod/assign/view.php?id={target.cmid}")
        if not self._extract_sesskey(html):
            raise SdoAuthError(
                "Не удалось получить sesskey СДО; повторите вход.",
                hint=self._SSO_HINT)
        assert self._sesskey is not None
        return self._sesskey

    def _refresh_draft_pin(self, target: AssignTarget) -> tuple[dict, str]:
        """Перевыпустить форму редактирования: новый itemid + свежий sesskey.

        Единственное место, где пин черновика инвалидируется до submission_send:
        Moodle ответил о невалидном sesskey, без новой формы не обойтись.
        ВНИМАНИЕ: повторное открытие формы пересевивает черновик только из
        сохранённого ответа — ранее поэтапно загруженные файлы теряются.
        """
        html = self._get_page(
            f"/mod/assign/view.php?id={target.cmid}&action=editsubmission")
        self._draft_ctx_cache.pop(target.cmid, None)
        ctx = self._draft_context(target, html)
        if not self._extract_sesskey(html):
            raise SdoAuthError(
                "Не удалось получить sesskey СДО; повторите вход.",
                hint=self._SSO_HINT)
        assert self._sesskey is not None
        return ctx, self._sesskey

    @staticmethod
    def _is_sesskey_failure(payload: Any) -> bool:
        """Ответ Moodle AJAX, указывающий на невалидный/протухший sesskey."""
        if not isinstance(payload, dict):
            return False
        exc = payload.get("exception")
        parts: list[str] = [str(payload.get("error") or ""),
                            str(payload.get("message") or "")]
        if isinstance(exc, dict):
            parts.append(str(exc.get("message") or ""))
        return "sesskey" in " ".join(parts).casefold()

    def _raise_ajax_error(self, payload: Any, what: str) -> None:
        """Громкая ошибка по payload["error"], КРОМЕ невалидного sesskey
        (его обрабатывает _mutate повторной попыткой). Dict-only."""
        if not isinstance(payload, dict):
            return
        err = payload.get("error")
        if err and not self._is_sesskey_failure(payload):
            raise MireaMcpError(f"СДО отклонил операцию «{what}»: {err}")

    def _mutate(self, target: AssignTarget, op) -> Any:
        """
        Выполнить один шаг мутации черновика с защитой от протухшего sesskey.

        op(ctx, sesskey) -> Any — POST-операция Moodle AJAX; вернуть
        распарсенный ответ, НЕ выбрасывая исключения по sesskey (см.
        _raise_ajax_error для прочих ошибок). Если Moodle ответил о невалидном
        sesskey, форма редактирования перевыпускается ОДИН раз (новый itemid,
        пин обновляется) и операция повторяется; при повторной неудаче —
        громкая ошибка.
        """
        ctx = self._draft_context(target)
        sesskey = self._view_sesskey(target)
        payload = op(ctx, sesskey)
        if self._is_sesskey_failure(payload):
            ctx, sesskey = self._refresh_draft_pin(target)
            payload = op(ctx, sesskey)
            if self._is_sesskey_failure(payload):
                raise MireaMcpError(
                    "СДО отклонил операцию: невалидный sesskey сессии.",
                    hint="сессия СДО устарела; повторите вход "
                    "(mirea_auth_start → mirea_auth_otp)",
                )
        return payload

    # ---------------- мутации черновика

    def _check_editable(self, target: AssignTarget) -> None:
        if not target.editable:
            raise MireaMcpError(
                "Ответ на работу не редактируется.",
                hint="ответ отправлен и редактирование запрещено"
                if target.status in {"submitted", "graded"}
                else "работа сейчас не принимает изменения ответа",
            )

    @staticmethod
    def _available_hint(attachments: list[Attachment]) -> str:
        names = [a.filename for a in attachments]
        return "доступные файлы: " + (", ".join(names) if names else "нет")

    def _upload_file(self, ctx: dict, path: Path, sesskey: str) -> Any:
        """Загрузить файл в черновик: repository_ajax.php?action=upload."""
        query = {
            "action": "upload",
            "repo_id": ctx["upload_repo_id"],
            "p": "",
            "page": "",
            "env": "filemanager",
            "sesskey": sesskey,
            "client_id": ctx["client_id"],
            "itemid": ctx["itemid"],
            "maxbytes": ctx["maxbytes"],
            "areamaxbytes": ctx["areamaxbytes"],
            "ctx_id": ctx["ctx_id"],
            "savepath": "/",
        }
        data = {
            "itemid": str(ctx["itemid"]),
            "title": path.name,
            "author": ctx["author"],
            "license": ctx["license"],
        }
        resp = self._http.post(
            "/repository/repository_ajax.php",
            params=query,
            data=data,
            files={"repo_upload_file": (
                path.name, path.read_bytes(), "application/octet-stream")},
        )
        payload = self._ajax_json(resp, "upload")
        self._raise_ajax_error(payload, "upload")
        return payload

    def draft_upload(self, target: AssignTarget, path: Path) -> None:
        """Прикрепить файл к черновику ответа (no-cobber по имени файла).

        Проверка уникальности имён — по поэтапно размещённым файлам pinned
        черновика (draft_list), а не по сохранённому ответу.
        """
        self._require_write_mode()
        self._check_editable(target)
        if not path.is_file():
            raise MireaMcpError(f"Файл не найден: {path}")
        staged = self.draft_list(target)
        if path.name in {a.filename for a in staged}:
            raise MireaMcpError(
                f"Файл «{path.name}» уже есть в черновике.",
                hint=self._available_hint(staged)
                + "; используйте submit_replace, чтобы заменить содержимое",
            )
        payload = self._mutate(
            target, lambda ctx, sesskey: self._upload_file(ctx, path, sesskey))
        if payload.get("event") == "fileexists":
            raise MireaMcpError(
                f"Файл «{path.name}» уже существует в черновике.",
                hint=self._available_hint(staged),
            )

    def _draftfiles_action(
            self, ctx: dict, action: str, sesskey: str,
            extra: dict[str, str]) -> Any:
        """Операция над файлами черновика: draftfiles_ajax.php?action=<action>.

        Ответы о невалидном sesskey НЕ выбрасываются — их обрабатывает
        _mutate повторной попыткой; прочие payload["error"] — громко.
        """
        data = {
            "sesskey": sesskey,
            "client_id": ctx["client_id"],
            "itemid": str(ctx["itemid"]),
            "filepath": "/",
            **extra,
        }
        resp = self._http.post(
            "/repository/draftfiles_ajax.php",
            params={"action": action},
            data=data
        )
        payload = self._ajax_json(resp, action)
        self._raise_ajax_error(payload, action)
        return payload

    def _draftfiles_list(self, ctx: dict, sesskey: str) -> dict:
        """
        draftfiles_ajax?action=list → {"error": str} | {"files": [Attachment]}.

        Ответ Moodle — либо голый JSON-массив элементов черновика, либо dict
        с ключом "list"; обе формы принимаются.
        """
        data = {
            "sesskey": sesskey,
            "client_id": ctx["client_id"],
            "itemid": str(ctx["itemid"]),
            "filepath": "/",
        }
        resp = self._http.post(
            "/repository/draftfiles_ajax.php", params={"action": "list"}, data=data)
        try:
            payload = resp.json()
        except ValueError as exc:
            raise MireaMcpError(
                f"СДО вернул не-JSON для «list» (HTTP {resp.status_code}).") from exc
        if isinstance(payload, dict):
            if payload.get("error"):
                return {"error": str(payload["error"])}
            items = payload.get("list")
        else:
            items = payload
        if not isinstance(items, list):
            raise MireaMcpError("СДО вернул неожиданный ответ для «list».")
        files = [Attachment(filename=str(it["filename"]), fileurl="")
                 for it in items
                 if isinstance(it, dict) and it.get("filename")]
        return {"files": files}

    def draft_list(self, target: AssignTarget) -> list[Attachment]:
        """Файлы, поэтапно размещённые в области черновика ответа.

        Именно то состояние, которое submission_send сохранил бы в ответе.
        Пин черновика лениво создаётся по cmid и живёт до успешной отправки.
        """
        self._require_write_mode()
        ctx = self._draft_context(target)
        sesskey = self._view_sesskey(target)
        result = self._draftfiles_list(ctx, sesskey)
        if result.get("error") and self._is_sesskey_failure(result):
            ctx, sesskey = self._refresh_draft_pin(target)
            result = self._draftfiles_list(ctx, sesskey)
        if result.get("error"):
            raise MireaMcpError(
                f"СДО отклонил операцию «list»: {result['error']}")
        return result["files"]

    def draft_rename(self, target: AssignTarget, filename: str, new_name: str) -> None:
        """Переименовать файл в черновике ответа.

        Проверки имён — по поэтапно размещённым файлам pinned черновика.
        """
        self._require_write_mode()
        self._check_editable(target)
        staged = self.draft_list(target)
        names = {a.filename for a in staged}
        if filename not in names:
            raise MireaMcpError(
                f"Файл «{filename}» не найден в черновике.",
                hint=self._available_hint(staged))
        if new_name in names:
            raise MireaMcpError(
                f"Файл «{new_name}» уже есть в черновике.",
                hint=self._available_hint(staged))
        self._mutate(target, lambda ctx, sesskey: self._draftfiles_action(
            ctx, "updatefile", sesskey, {
                "filepath": "/", "filename": filename,
                "newfilename": new_name, "newfilepath": "/",
            }))

    def draft_delete(self, target: AssignTarget, filenames: list[str]) -> None:
        """Удалить перечисленные файлы из черновика ответа."""
        self._require_write_mode()
        self._check_editable(target)
        staged = self.draft_list(target)
        names = {a.filename for a in staged}
        missing = [f for f in filenames if f not in names]
        if missing:
            raise MireaMcpError(
                "Не найдены файлы: " + ", ".join(f"«{f}»" for f in missing),
                hint=self._available_hint(staged))
        self._mutate(target, lambda ctx, sesskey: self._draftfiles_action(
            ctx, "deleteselected", sesskey, {
                # Moodle итерирует объекты и зовёт get_filepath() на каждом
                # элементе — голые строки приводят к ошибке сервера.
                "selected": json.dumps(
                    [{"filepath": "/", "filename": n} for n in filenames],
                    ensure_ascii=False),
            }))

    def _overwrite_file(
        self, ctx: dict, sesskey: str,
        existing: dict, new: dict
    ) -> dict:
        """
        Атомарно подменить содержимое: repository_ajax.php?action=overwrite.
        """
        data = {
            "repo_id": ctx["upload_repo_id"],
            "p": "",
            "page": "",
            "env": "filemanager",
            "sesskey": sesskey,
            "client_id": ctx["client_id"],
            "itemid": str(ctx["itemid"]),
            "maxbytes": ctx["maxbytes"],
            "areamaxbytes": ctx["areamaxbytes"],
            "ctx_id": ctx["ctx_id"],
            "existingfilename": existing["filename"],
            "existingfilepath": existing.get("filepath", "/"),
            "newfilename": new["filename"],
            "newfilepath": new.get("filepath", "/"),
        }
        resp = self._http.post(
            "/repository/repository_ajax.php", params={"action": "overwrite"}, data=data)
        payload = self._ajax_json(resp, "overwrite")
        # Moodle отвечает ГОЛЫМ JSON-булом: true = замена прошла,
        # false = отклонена (сервер НЕ трогал существующий файл).
        if payload is False:
            raise MireaMcpError(
                "СДО не смог заменить файл (overwrite отклонён)",
                hint="содержимое существующего файла НЕ изменилось; "
                "свежезагруженный файл остался в черновике под именем "
                f"«{new['filename']}» — удалите его через draft_delete "
                "(см. draft_list)",
            )
        self._raise_ajax_error(payload, "overwrite")
        return payload

    def draft_replace(
            self, target: AssignTarget, filename: str, path: Path
    ) -> None:
        """Атомарно заменить содержимое файла черновика (upload + overwrite).

        Проверка существования — по поэтапно размещённым файлам pinned
        черновика.
        """
        self._require_write_mode()
        self._check_editable(target)
        if not path.is_file():
            raise MireaMcpError(f"Файл не найден: {path}")
        staged = self.draft_list(target)
        if filename not in {a.filename for a in staged}:
            raise MireaMcpError(
                f"Файл «{filename}» не найден в черновике.",
                hint=self._available_hint(staged))

        def op(ctx: dict, sesskey: str) -> Any:
            payload = self._upload_file(ctx, path, sesskey)
            if payload.get("event") == "fileexists":
                existing = payload["existingfile"]
                new = payload["newfile"]
            else:
                # новый файл лёг в корень черновика (savepath=/)
                existing = {"filename": filename, "filepath": "/"}
                new = {"filename": payload.get(
                    "file") or path.name, "filepath": "/"}
            return self._overwrite_file(ctx, sesskey, existing, new)

        self._mutate(target, op)

    # ---------------- сохранение и отправка ответа

    def _submission_form(
            self, target: AssignTarget, html: str
    ) -> tuple[dict[str, str], dict[str, str]]:
        """Разобрать форму редактирования ответа: hidden-поля и кнопки."""
        soup = BeautifulSoup(html, "html.parser")
        form = None
        for f in soup.find_all("form"):
            if f.find("input", {"name": "action", "value": "savesubmission"}) is not None:
                form = f
                break
        if form is None:
            raise MireaMcpError(
                "Форма ответа не найдена: ответ, вероятно, больше не редактируется.",
                hint="повторите resolve_assign",
            )
        fields: dict[str, str] = {}
        for inp in form.find_all("input"):
            name = inp.get("name")
            typ = (inp.get("type") or "text").lower()
            if not name or typ in ("submit", "button", "file"):
                continue
            if typ in ("checkbox", "radio"):
                # чекбоксы Moodle отправляют только отмеченные; submissionstatement
                # (если есть) будет добавлен ниже как подтверждённое согласие
                if "submissionstatement" in name or inp.has_attr("checked"):
                    fields[name] = inp.get("value") or "1"
                continue
            fields[name] = inp.get("value") or ""
        if form.find("input", attrs={"name": re.compile("submissionstatement")}):
            fields["submissionstatement"] = "1"
        buttons = {
            inp["name"]: inp.get("value") or ""
            for inp in form.find_all("input", type="submit")
            if inp.get("name")
        }
        return fields, buttons

    def _post_submission(self, fields: dict[str, str]) -> None:
        """
        Отправить форму ответа на view.php и проверить, что Moodle принял её.
        """
        fields.setdefault("sesskey", self._fresh_sesskey())
        resp = self._drain_redirects(self._http.post(
            f"{SDO_BASE}/mod/assign/view.php", data=fields, follow_redirects=False))
        if resp.status_code >= 400:
            raise MireaMcpError(
                f"СДО отклонил сохранение ответа: HTTP {resp.status_code}")
        soup = BeautifulSoup(resp.text, "html.parser")
        # alert-danger внутри <noscript> («JavaScript отключен…») вшит Moodle
        # в КАЖДУЮ страницу — это не ошибка приёма ответа, игнорируем.
        danger = next(
            (el for el in soup.select(".alert-danger, .notifyproblem")
             if el.find_parent("noscript") is None), None)
        if danger is not None:
            raise MireaMcpError(
                "СДО не принял ответ.",
                hint=_WS.sub(" ", danger.get_text(" ", strip=True))[:300] or None)
        if "action=editsubmission" in str(resp.url):
            raise MireaMcpError(
                "СДО не принял ответ: остались на форме редактирования.",
                hint="проверьте требования задания (обязательные поля, срок сдачи)",
            )

    def submission_save(self, target: AssignTarget) -> None:
        """Сохранить черновик ответа (кнопка «Сохранить» формы editsubmission).

        При выключенных черновиках (этот Moodle) та же кнопка отправляет ответ
        преподавателю — ср. submission_send.
        """
        self._require_write_mode()
        self._check_editable(target)
        html = self._get_page(
            f"/mod/assign/view.php?id={target.cmid}&action=editsubmission")
        fields, buttons = self._submission_form(target, html)
        ctx = self._draft_context(target, html)
        fields["files_filemanager"] = str(ctx["itemid"])
        for name, value in buttons.items():
            if name != "cancel":
                fields[name] = value
                break
        self._post_submission(fields)

    def submission_send(self, target: AssignTarget) -> None:
        """
        Окончательная отправка ответа преподавателю (кнопка «Отправить задание»).

        Отдельный шаг существует только при включённых черновиках (кнопка
        submitbutton2 в форме). На online-edu.mirea.ru черновики выключены:
        единственная кнопка «Сохранить» отправляет ответ сразу, поэтому здесь
        просто делегируем submission_save.
        """
        self._require_write_mode()
        self._check_editable(target)
        html = self._get_page(
            f"/mod/assign/view.php?id={target.cmid}&action=editsubmission")
        fields, buttons = self._submission_form(target, html)
        if "submitbutton2" not in buttons:
            self.submission_save(target)
            # отправка состоялась (на этом Moodle сохранение == отправка):
            # сохранённое состояние изменилось — следующая мутация начнёт
            # с нового черновика, пересеянного из нового сохранённого ответа.
            self._draft_ctx_cache.pop(target.cmid, None)
            return
        ctx = self._draft_context(target, html)
        fields["files_filemanager"] = str(ctx["itemid"])
        fields["submitbutton2"] = buttons["submitbutton2"]
        self._post_submission(fields)
        # отправка успешна: пин черновика сбрасываем, следующая мутация
        # получит свежий itemid, пересеянный из нового сохранённого ответа.
        self._draft_ctx_cache.pop(target.cmid, None)


def _control_from_name(name: str) -> str | None:
    """
    Тип промежуточной аттестации из суффикса имени дисциплины: _Экзамен / _Зачет(Ё).
    """
    if "_Экзамен" in name:
        return "exam"
    if "_Зачет" in name or "_Зачёт" in name:
        return "zachet"
    return None


def _parse_ru_datetime(text: str) -> str | None:
    """
    «вторник, 8 декабря 2026, 23:41» → ISO 8601 с таймзоной Москвы;
    None при неудаче.
    """
    _RU_MONTHS = {
        "января": 1, "февраля": 2, "марта": 3,
        "апреля": 4, "мая": 5, "июня": 6,
        "июля": 7, "августа": 8, "сентября": 9,
        "октября": 10, "ноября": 11, "декабря": 12,
    }

    m = re.search(
        r"(\d{1,2})\s+([а-яё]+)\s+(\d{4})\s*,?\s*(\d{1,2}):(\d{2})",
        text.strip().casefold(),
    )
    if not m:
        return None
    day, mon_name, year, hour, minute = m.groups()
    month = _RU_MONTHS.get(mon_name)
    if month is None:
        return None
    try:
        dt = datetime(int(year), month, int(day), int(
            hour), int(minute), tzinfo=_MSK)
    except ValueError:
        return None
    return dt.isoformat()


def _to_float(text: str) -> float | None:
    text = text.strip().replace("\u00a0", "").replace(" ", "").replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None

"""Клиент СДО РТУ МИРЭА (Moodle, online-edu.mirea.ru).

Режимы работы (пер-инстанс, лениво определяется при первом вызове, порядок проб):

1. REST (предпочтительно) — wstoken из MIREA_SDO_TOKEN, из state.json или
   через /login/token.php (service=moodle_mobile_app). Токен кэшируется в state.
2. OIDC — проезд по сессии Keycloak (sso.mirea.ru): куки из state["pulse"]["cookies"]
   подсаживаются в jar, GET /auth/oidc/ проходит SSO-редиректы без OTP. Локальный
   логин/пароль Keycloak здесь НЕ реализуется — требуется предварительный вход
   в Пульс (mirea_auth_start → mirea_auth_otp).
3. Браузерная локальная форма (последний резерв) — POST /login/index.php с logintoken.

Успешная oidc/browser-сессия (MoodleSession + sesskey) сохраняется в
state["sdo"]["cookies"] и переиспользуется при следующих запусках.

Подключение ленивое: импорт модуля не требует кредов и сети.
"""
from __future__ import annotations

import re
import time
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from . import state
from .config import LOGIN, PASSWORD, SDO_BASE, SDO_TOKEN_OVERRIDE
from .models import CredentialsMissing, DisciplineGrades, SdoAuthError, Work

_TIMEOUT = 30
_REST_SERVICE = "moodle_mobile_app"
# Коды ошибок Moodle REST, после которых имеет смысл переключаться на браузерный режим
_REST_FATAL_CODES = {"accessexception", "invalidtoken",
                     "servicerequireslogin", "usernotfullysetup"}
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
        self._mode: str | None = None  # "rest" | "oidc" | "browser"
        self._wstoken: str | None = None
        self._sesskey: str | None = None
        self._userid: int | None = None

    # ------------------------------------------------------------------ общее

    @property
    def source(self) -> str:
        """Канал данных текущей сессии: "rest", "oidc" или "browser"."""
        self._ensure_mode()
        assert self._mode is not None
        return self._mode

    def _ensure_mode(self) -> None:
        if self._mode is not None:
            return
        rest_error: CredentialsMissing | None = None
        try:
            if self._try_rest():
                self._mode = "rest"
                return
        except CredentialsMissing as e:
            # Локальная Moodle-авторизация мертва для этого аккаунта — не прерываем
            # цепочку, идём дальше к SSO/браузеру, а ошибку сохраняем на конец
            rest_error = e
        if self._restore_session():
            return
        try:
            if self._try_oidc():
                self._mode = "oidc"
                self._save_session("oidc")
                return
        except SdoAuthError:
            raise  # SSO требует входа в Пульс — подсказка уже в ошибке
        if self._login_browser():
            self._mode = "browser"
            self._save_session("browser")
            return
        if rest_error is not None:
            raise rest_error
        raise SdoAuthError(
            "Не удалось войти в СДО: нет ни REST-токена, ни SSO-сессии Пульса, "
            "ни локальной Moodle-авторизации.",
            hint=self._SSO_HINT + "; либо задайте MIREA_SDO_TOKEN.",
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
        if mode not in ("oidc", "browser"):
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
        if SDO_TOKEN_OVERRIDE:
            return SDO_TOKEN_OVERRIDE.strip()
        saved = (state.load().get("sdo") or {}).get("wstoken")
        if saved:
            return saved
        if not (LOGIN and PASSWORD):
            raise CredentialsMissing(
                "Не заданы учётные данные СДО.",
                hint="Добавьте MIREA_LOGIN и MIREA_PASSWORD в mirea-mcp/.env.",
            )
        resp = self._http.get(
            "/login/token.php",
            params={"username": LOGIN, "password": PASSWORD,
                    "service": _REST_SERVICE},
        )
        try:
            data = resp.json()
        except ValueError as exc:
            raise SdoAuthError("СДО вернул не-JSON на запрос токена.") from exc
        if data.get("error") == "invalidlogin":
            raise CredentialsMissing(
                "СДО отклонил логин/пароль (invalidlogin).",
                hint="Проверьте MIREA_LOGIN/MIREA_PASSWORD; при необходимости задайте MIREA_SDO_TOKEN.",
            )
        token = data.get("token")
        if not token:
            # Например: "service не включён" — токен недоступен, уходим в браузерный режим
            return None
        st = state.load()
        st.setdefault("sdo", {})["wstoken"] = token
        st["sdo"]["saved_at"] = time.time()
        state.save(st)
        return token

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
        except CredentialsMissing:
            raise  # кредов нет — сразу понятно, в браузерный режим тоже не войти
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

    # ------------------------------------------------------------------ браузерный режим

    def _login_browser(self) -> bool:
        if not (LOGIN and PASSWORD):
            return False
        # 1. GET страницы входа — MoodleSession + logintoken
        resp = self._http.get("/login/index.php")
        if resp.status_code >= 400:
            return False
        soup = BeautifulSoup(resp.text, "html.parser")
        token_input = soup.find("input", {"name": "logintoken"})
        logintoken = token_input.get("value", "") if token_input else ""
        # 2. POST формы входа
        resp = self._http.post(
            "/login/index.php",
            data={
                "logintoken": logintoken,
                "username": LOGIN,
                "password": PASSWORD,
                "anchor": "",
            },
        )
        # Успех: редирект на главную / dashboard; неуспех — страница входа снова
        for _ in range(6):
            if resp.status_code in (301, 302, 303, 307, 308):
                location = urljoin(
                    str(resp.url), resp.headers.get("Location", ""))
                path = location.split("://", 1)[-1].split("/", 1)[-1]
                if path.startswith(("login/", "auth/")):
                    return False  # редирект обратно на вход — пароль неверный
                resp = self._http.get(location)
                continue
            break
        if resp.status_code >= 400:
            return False
        if "login/index.php" in str(resp.url):
            return False
        return self._extract_sesskey(resp.text)

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
            score = max_ = None
            graded = False
            source = (grade_cell.get_text(" ", strip=True) if grade_cell else "") or (
                range_cell.get_text(" ", strip=True) if range_cell else ""
            )
            m = _RANGE_CELL.match(source.replace("–", "-"))
            if m:
                raw_score = m.group("score").strip()
                if raw_score not in ("-", ""):
                    graded = True
                    score = _to_float(raw_score)
                max_ = _to_float(m.group("max"))
            elif source and source.strip() not in ("-", "–"):
                score = _to_float(source)
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

    # ------------------------------------------------------------------ дедлайны

    def due_works(self, days: int = 14) -> list[dict]:
        """Предстоящие работы с дедлайнами (по всем дисциплинам, dict'и с полем discipline)."""
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
        now = time.time()
        cutoff = now + days * 86400
        out: list[dict] = []
        for course in self._courses():
            cname = _WS.sub(" ", str(course.get("fullname", ""))).strip()
            html = self._get_page(
                f"/grade/report/user/index.php?id={course.get('id')}")
            soup = BeautifulSoup(html, "html.parser")
            for tr in soup.select("table.user-grade tr"):
                th = tr.find("th")
                if th is None or "baggt" in (th.get("class") or []):
                    continue
                name = _WS.sub(" ", th.get_text(" ", strip=True)).strip()
                if not name:
                    continue
                link = th.find("a", href=True)
                url = urljoin(SDO_BASE, link["href"]) if link and link["href"].startswith(
                    "/") else None
                out.append({"discipline": cname, "name": name,
                           "due": None, "submitted": None, "url": url})
        # Даты сдачи из календаря (AJAX); если недоступен — работы без дат пропускаются
        try:
            events = self._ajax(
                "core_calendar_get_calendar_events",
                options={
                    "userevents": 1,
                    "siteevents": 0,
                    "timestart": int(now),
                    "timeend": int(cutoff),
                    "limitnum": 100,
                },
            ) or {}
        except SdoAuthError:
            events = {}
        by_name: dict[str, dict] = {}
        for ev in (events.get("events") or []):
            evname = _WS.sub(" ", str(ev.get("name") or "")).strip()
            if not evname:
                continue
            by_name.setdefault(
                evname,
                {
                    "due": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(int(ev["timestart"])))
                    if ev.get("timestart")
                    else None
                },
            )
        result: list[dict] = []
        for w in out:
            meta = by_name.get(w["name"])
            if meta and meta.get("due"):
                w["due"] = meta["due"]
                result.append(w)
        result.sort(key=lambda w: w["due"] or "")
        return result


def _control_from_name(name: str) -> str | None:
    """Тип промежуточной аттестации из суффикса имени дисциплины: _Экзамен / _Зачет(Ё)."""
    if "_Экзамен" in name:
        return "exam"
    if "_Зачет" in name or "_Зачёт" in name:
        return "zachet"
    return None


def _to_float(text: str) -> float | None:
    text = text.strip().replace("\u00a0", "").replace(" ", "").replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None

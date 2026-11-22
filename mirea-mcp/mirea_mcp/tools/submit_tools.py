"""Инструменты записи: ответы на работы СДО (ADR-0006).

Каждый action-инструмент: resolve_assign(url) → мутация (только стадит
изменение в черновой области) → draft_list + reload_submission →
наблюдаемое состояние (attachments — сохранённые вложения, staged — что
уйдёт преподавателю). Публикует изменения только submit_post. Свободный
текст запроса (query) никогда не доходит до пути мутации — нечёткий поиск
только ищет и ничего не исполняет.
"""
import re
from dataclasses import asdict
from pathlib import Path

from fastmcp import FastMCP

from .. import abbreviations
from ..models import AssignTarget, MireaMcpError
from .sdo_tools import _get_client  # общий клиент: кэш сессии и draft-контекста

# Виды работ — см. GLOSSARY.md «Виды работ»: статическая расшифровка коротких
# токенов типа работы в полное название для нечёткого поиска.
_WORK_TYPE_MAP = {
    "кр": "контрольная работа",
    "лр": "лабораторная работа",
    "пр": "практическая работа",
    "тк": "текущий контроль",
    "кп": "курсовой проект",
}


def _err(e: MireaMcpError) -> dict:
    return {"error": str(e), "hint": e.hint}


def _attachments_payload(client, target: AssignTarget) -> dict:
    """Наблюдаемое состояние после мутации.

    «staged» — файлы черновой области (draft_list), то, что уйдёт преподавателю
    при submit_post. «attachments» — сохранённые вложения ответа
    (reload_submission), видимые преподавателю. draft_list вызывается ДО
    reload_submission: мутации уже застадированы, а перечитывание страницы
    не сбрасывает draft-контекст.
    """
    staged = client.draft_list(target)
    attachments = client.reload_submission(target)
    return {
        "url": target.url,
        "name": target.name,
        "course_name": target.course_name,
        "status": target.status,
        "editable": target.editable,
        "due": target.due,
        "attachments": [asdict(a) for a in attachments],
        "staged": [asdict(a) for a in staged],
    }


def _fuzzy_candidates(query: str, limit: int) -> dict:
    """Нечёткий поиск работ по дисциплинам текущего семестра (только чтение)."""
    client = _get_client()
    disciplines = client.disciplines()
    names = [d.name for d in disciplines]
    abbr_map: dict[str, list[str]] = {}
    derived = abbreviations.load_or_derive(names)
    # payload: {аббревиатура: [полные имена]} → обратная карта для поиска
    for ab, full_names in derived["abbreviations"].items():
        for full in full_names:
            abbr_map.setdefault(ab.casefold(), []).append(full.casefold())

    # «лр4» → «лр» + «4»: граница буква/цифра дробит токен, каждый кусок
    # дальше получает стандартный набор вариантов (raw/worktype/abbrev),
    # а «4» подстрочно совпадает с номером в названии («... 7-8 (4)»).
    tokens: list[str] = []
    for raw in query.casefold().split():
        tokens.extend(re.findall(r"[^\W\d_]+|\d+", raw, flags=re.UNICODE))
    if not tokens:
        return {"error": "пустой запрос query", "hint": "передайте слова из названия дисциплины или работы"}

    # (текст, источник): raw — сам токен, worktype — статичная расшифровка,
    # abbrev — полное имя дисциплины по производной аббревиатуре.
    per_token: dict[str, list[tuple[str, str]]] = {}
    for token in tokens:
        variants: list[tuple[str, str]] = [(token, "raw")]
        if token in _WORK_TYPE_MAP:
            variants.append((_WORK_TYPE_MAP[token], "worktype"))
        for full in abbr_map.get(token, []):
            variants.append((full, "abbrev"))
        per_token[token] = variants

    candidates: list[dict] = []
    for disc in disciplines:
        disc_cf = disc.name.casefold()
        for work in disc.works:
            if not work.url:
                continue  # без страницы сдачи кандидат непригоден для точного режима
            title_cf = work.name.casefold()
            score = 0
            matched_terms: list[str] = []
            abbrev_hit = False
            ok = True
            for token in tokens:
                hit_text = None
                hit_source = "raw"
                for text, source in per_token[token]:
                    if text in disc_cf or text in title_cf:
                        hit_text, hit_source = text, source
                        break
                if hit_text is None:
                    ok = False
                    break
                score += len(token)
                if hit_source == "abbrev":
                    abbrev_hit = True
                if hit_source == "worktype" and hit_text in title_cf:
                    score += 10
                matched_terms.append(
                    f"{token} → {hit_text}" if hit_text != token else token)
            if not ok:
                continue
            if abbrev_hit:
                score += 50
            candidates.append({
                "url": work.url,
                "discipline": disc.name,
                "work_title": work.name,
                "due": work.due,
                "submitted": work.submitted,
                "score": score,
                "matched_terms": matched_terms,
            })
    candidates.sort(key=lambda c: (-c["score"], c["discipline"], c["work_title"]))
    return {"mode": "fuzzy", "enact": False, "candidates": candidates[:limit]}


def register(mcp: FastMCP) -> None:
    @mcp.tool
    def mirea_submit_find(url: str | None = None, query: str | None = None,
                          limit: int = 5) -> dict:
        """Поиск работы для сдачи: точный режим по url или нечёткий по query.

        Ровно один из аргументов обязателен. Режим url: валидирует страницу
        задания и возвращает её наблюдаемое состояние (статус, вложения,
        застадированные файлы, дедлайн). Режим query: нечёткий поиск по
        дисциплинам и работам текущего семестра — токены сверяются с названием
        дисциплины и работы, токены вроде «лр4» дробятся по границе
        буква/цифра («лр» + «4»), короткие токены типов работ (лр, кр, пр,
        тк, кп) расшифровываются, а аббревиатуры дисциплин — по глоссарию.
        Возвращает до limit кандидатов с объяснением совпадений. Нечёткий
        поиск никогда ничего не отправляет и не изменяет (enact: false),
        даже при единственном совпадении.
        """
        client = _get_client()
        try:
            if bool(url) == bool(query):
                return {"error": "нужен ровно один аргумент: url или query",
                        "hint": "url — точный режим, query — нечёткий поиск"}
            if url:
                target = client.resolve_assign(url)
                staged = client.draft_list(target)
                return {"mode": "exact", **asdict(target),
                        "staged": [asdict(a) for a in staged]}
            return _fuzzy_candidates(query or "", max(1, limit))
        except MireaMcpError as e:
            return _err(e)

    @mcp.tool
    def mirea_submit_attach(url: str, path: str) -> dict:
        """Прикрепить файл к черновику ответа на работу (без отправки).

        Мутация только стадит изменение в черновой области: преподавателю
        файл уйдёт только через submit_post. Безопасность no-cobber: если
        файл с таким именем уже есть в черновой области, операция отклоняется
        ошибкой — существующий файл не затирается и не дублируется. Возвращает
        attachments (сохранённые вложения, видимые преподавателю) и staged
        (застадированные файлы, которые уйдут при отправке).
        """
        client = _get_client()
        try:
            target = client.resolve_assign(url)
            p = Path(path)
            if not p.is_file():
                return {"error": f"файл не найден: {path}"}
            client.draft_upload(target, p)
            return _attachments_payload(client, target)
        except MireaMcpError as e:
            return _err(e)

    @mcp.tool
    def mirea_submit_bulk_attach(url: str, paths: list[str] | None = None,
                                 directory: str | None = None) -> dict:
        """Прикрепить несколько файлов к черновику ответа (без отправки).

        Ровно один из аргументов: paths — список путей к файлам, directory —
        каталог (без рекурсии, только файлы, в отсортированном порядке).
        Мутации только стадят изменения в черновой области; публикует только
        submit_post. No-cobber по черновой области: совпадение имени — ошибка.
        При сбое останавливается на первой ошибке; частично застадированное
        состояние остаётся в силе, перечисляются успешные загрузки,
        attachments (сохранённые) и staged (что уйдёт при отправке).
        """
        client = _get_client()
        try:
            if bool(paths) == bool(directory):
                return {"error": "нужен ровно один аргумент: paths или directory"}
            target = client.resolve_assign(url)
            if directory:
                d = Path(directory)
                if not d.is_dir():
                    return {"error": f"каталог не найден: {directory}"}
                paths = sorted(p.name for p in d.iterdir() if p.is_file())
                resolved = [str(Path(directory) / name) for name in paths]
            else:
                resolved = list(paths or [])
            done: list[str] = []
            try:
                for p in resolved:
                    client.draft_upload(target, Path(p))
                    done.append(p)
            except MireaMcpError as e:
                payload = _attachments_payload(client, target)
                return {**_err(e), "succeeded": done, "partial": True,
                        **payload}
            return _attachments_payload(client, target)
        except MireaMcpError as e:
            return _err(e)

    @mcp.tool
    def mirea_submit_replace(url: str, filename: str, path: str) -> dict:
        """Атомарно заменить содержимое файла в черновике ответа (без отправки).

        Мутация только стадит изменение в черновой области; публикует только
        submit_post. Содержимое filename заменяется содержимым файла path;
        нет окна «файл удалён, новый не доехал». Возвращает attachments
        (сохранённые вложения) и staged (что уйдёт преподавателю при отправке).
        """
        client = _get_client()
        try:
            target = client.resolve_assign(url)
            p = Path(path)
            if not p.is_file():
                return {"error": f"файл не найден: {path}"}
            client.draft_replace(target, filename, p)
            return _attachments_payload(client, target)
        except MireaMcpError as e:
            return _err(e)

    @mcp.tool
    def mirea_submit_rename(url: str, old_name: str, new_name: str) -> dict:
        """Переименовать файл в черновике ответа (без отправки).

        Мутация только стадит изменение в черновой области; публикует только
        submit_post. Возвращает attachments (сохранённые вложения) и staged
        (что уйдёт преподавателю при отправке).
        """
        client = _get_client()
        try:
            target = client.resolve_assign(url)
            client.draft_rename(target, old_name, new_name)
            return _attachments_payload(client, target)
        except MireaMcpError as e:
            return _err(e)

    @mcp.tool
    def mirea_submit_bulk_rename(url: str, renames: dict[str, str]) -> dict:
        """Переименовать несколько файлов в черновике ответа (без отправки).

        Мутации только стадят изменения в черновой области; публикует только
        submit_post. renames — словарь «старое имя → новое имя», применяется
        последовательно. При сбое останавливается на первой ошибке; уже
        застадированные переименования остаются в силе, перечисляются успешные
        пары, attachments (сохранённые) и staged (что уйдёт при отправке).
        """
        client = _get_client()
        try:
            if not renames:
                return {"error": "пустой словарь renames"}
            target = client.resolve_assign(url)
            done: list[dict[str, str]] = []
            try:
                for old, new in renames.items():
                    client.draft_rename(target, old, new)
                    done.append({"old": old, "new": new})
            except MireaMcpError as e:
                payload = _attachments_payload(client, target)
                return {**_err(e), "succeeded": done, "partial": True,
                        **payload}
            return _attachments_payload(client, target)
        except MireaMcpError as e:
            return _err(e)

    @mcp.tool
    def mirea_submit_remove(url: str, filename: str) -> dict:
        """Удалить один файл из черновика ответа (без отправки).

        Мутация только стадит удаление в черновой области; публикует только
        submit_post. Удаляется только filename; возвращает attachments
        (сохранённые вложения) и staged (что уйдёт преподавателю при отправке).
        """
        client = _get_client()
        try:
            target = client.resolve_assign(url)
            client.draft_delete(target, [filename])
            return _attachments_payload(client, target)
        except MireaMcpError as e:
            return _err(e)

    @mcp.tool
    def mirea_submit_bulk_remove(url: str, filenames: list[str]) -> dict:
        """Удалить несколько файлов из черновика ответа (без отправки).

        Мутация только стадит удаление в черновой области; публикует только
        submit_post. Удаляются ровно перечисленные файлы. Возвращает
        attachments (сохранённые вложения) и staged (что уйдёт при отправке).
        """
        client = _get_client()
        try:
            if not filenames:
                return {"error": "пустой список filenames"}
            target = client.resolve_assign(url)
            client.draft_delete(target, list(filenames))
            return _attachments_payload(client, target)
        except MireaMcpError as e:
            return _err(e)

    @mcp.tool
    def mirea_submit_all_remove(url: str) -> dict:
        """Удалить ВСЕ файлы из черновика ответа (wipe, без отправки).

        Мутация только стадит удаление в черновой области; публикует только
        submit_post. Отдельный инструмент, чтобы опечатка в имени не стёрла
        чужой или весь ответ: полная очистка возможна только этим явным
        вызовом. Очищает черновую область: застадированные файлы и пересеянные
        из сохранённого ответа. Возвращает attachments (сохранённые вложения)
        и staged (что уйдёт преподавателю при отправке).
        """
        client = _get_client()
        try:
            target = client.resolve_assign(url)
            names = [a.filename for a in client.draft_list(target)]
            if names:
                client.draft_delete(target, names)
            return _attachments_payload(client, target)
        except MireaMcpError as e:
            return _err(e)

    @mcp.tool
    def mirea_submit_post(url: str, confirm: bool = False) -> dict:
        """Отправить ответ на работу преподавателю (необратимо).

        confirm=False (по умолчанию): ничего не отправляет, возвращает
        превью — работа, сохранённые вложения, застадированные файлы (точно
        то, что уйдёт преподавателю), дедлайн, статус. Отправка происходит
        только при повторном вызове с confirm=True: submit_post публикует
        staged-состояние. После отправки возвращает наблюдаемое состояние
        ответа.
        """
        client = _get_client()
        try:
            target = client.resolve_assign(url)
            if not confirm:
                staged = client.draft_list(target)
                return {
                    "preview": {
                        "url": target.url,
                        "name": target.name,
                        "course_name": target.course_name,
                        "status": target.status,
                        "editable": target.editable,
                        "due": target.due,
                        "attachments": [asdict(a) for a in target.attachments],
                        "staged": [asdict(a) for a in staged],
                    },
                    "would_send": True,
                    "note": "повторите с confirm=True для отправки",
                }
            client.submission_send(target)
            attachments = client.reload_submission(target)
            return {"sent": True, "status": target.status,
                    "attachments": [asdict(a) for a in attachments]}
        except MireaMcpError as e:
            return _err(e)

    @mcp.tool
    def mirea_discipline_abbreviations(refresh: bool = False) -> dict:
        """Аббревиатуры дисциплин текущего семестра (первые буквы слов имени).

        Чистое чтение: результат производной функции с кэшем по хэшу списка
        дисциплин. refresh=True принудительно пересчитывает аббревиатуры.
        Используются нечётким поиском submit_find для расшифровки токенов.
        """
        client = _get_client()
        try:
            names = [d.name for d in client.disciplines()]
            return abbreviations.load_or_derive(names, refresh=refresh)
        except MireaMcpError as e:
            return _err(e)

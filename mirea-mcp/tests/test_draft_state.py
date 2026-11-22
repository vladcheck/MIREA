"""Персистентность пинов черновиков ответов (draft.json) через процессы.

Все тесты без сети: _get_page/_post_submission заменяются фейками.
"""

import json
import stat

import pytest

from mirea_mcp import state
from mirea_mcp.models import AssignTarget
from mirea_mcp.sdo_client import SdoClient

# Ожидаемый контекст, который SdoClient парсит сегодня из fake-HTML.
EXPECTED_CTX = {
    "itemid": 456789,
    "client_id": "abc123client",
    "ctx_id": 4242,
    "maxbytes": 2097152,
    "areamaxbytes": 10485760,
    "author": "Иван Петров",
    "license": "cc-nc-sa",
    "upload_repo_id": 77,
}

_FM_CONFIG = {
    "client_id": "abc123client",
    "itemid": 456789,
    "maxbytes": 2097152,
    "areamaxbytes": 10485760,
    "author": "Иван Петров",
    "context": {"id": 4242},
    "filepicker": {
        "defaultlicense": "cc-nc-sa",
        "repositories": {
            "1": {"type": "upload", "id": 77},
            "2": {"type": "recentfiles", "id": 5},
        },
    },
}


def _editsubmission_html(with_submit2: bool = True) -> str:
    """Минимальный fake страницы editsubmission: форма + init filemanager."""
    submit2 = (
        '<input type="submit" name="submitbutton2" value="Отправить задание"/>'
        if with_submit2
        else ""
    )
    return f"""<html><body>
<form action="/mod/assign/view.php" method="post" id="mform1">
  <input type="hidden" name="action" value="savesubmission"/>
  <input type="hidden" name="sesskey" value="sesskey123"/>
  <input type="hidden" name="files_filemanager" value="456789"/>
  <input type="submit" name="submitbutton" value="Сохранить"/>
  {submit2}
</form>
<script>M.form_filemanager.init(Y,{json.dumps(_FM_CONFIG)});</script>
</body></html>"""


def _target(cmid: int = 123) -> AssignTarget:
    return AssignTarget(
        url=f"https://online-edu.mirea.ru/mod/assign/view.php?id={cmid}",
        cmid=cmid,
        name="ЛР1",
        course_name="Курс",
        status="draft",
        editable=True,
        due=None,
    )


def _make_client() -> SdoClient:
    """Клиент с выставленным режимом — _require_write_mode не лезет в сеть."""
    client = SdoClient()
    client._mode = "oidc"
    return client


@pytest.fixture
def draft_file(tmp_path, monkeypatch):
    """draft.json в tmp; state.py разрешает пути в момент вызова."""
    path = tmp_path / "draft.json"
    monkeypatch.setattr(state, "STATE_DIR", tmp_path)
    monkeypatch.setattr(state, "DRAFT_FILE", path)
    return path


# ---------------------------------------------------------------- state.py


def test_load_missing_file(draft_file):
    assert state.load_draft_pins() == {}


def test_corrupt_draft_file_recovers(draft_file):
    draft_file.write_text("{это не json", encoding="utf-8")
    assert state.load_draft_pins() == {}
    state.save_draft_pins({"7": {"itemid": 1}})
    assert json.loads(draft_file.read_text(encoding="utf-8")) == {"7": {"itemid": 1}}


# ------------------------------------------------------------ sdo_client.py


def test_draft_context_parses_fake_html(draft_file):
    client = _make_client()
    monkey = pytest.MonkeyPatch()
    monkey.setattr(client, "_get_page", lambda path: _editsubmission_html())
    try:
        ctx = client._draft_context(_target())
    finally:
        monkey.undo()
    assert ctx == EXPECTED_CTX
    # создание пина пишет его и на диск (L2)
    assert state.load_draft_pins() == {"123": EXPECTED_CTX}


def test_pin_survives_across_instances(draft_file):
    target = _target()
    html = _editsubmission_html()

    client_a = _make_client()
    monkey_a = pytest.MonkeyPatch()
    monkey_a.setattr(client_a, "_get_page", lambda path: html)
    try:
        ctx_a = client_a._draft_context(target)
    finally:
        monkey_a.undo()
    assert ctx_a == EXPECTED_CTX
    assert draft_file.exists()
    assert stat.S_IMODE(draft_file.stat().st_mode) == 0o600

    # Второй процесс: пустой L1, HTTP запрещён — пин берётся с диска.
    client_b = _make_client()

    def _boom(path):
        raise AssertionError(f"HTTP-вызов не ожидался: {path}")

    monkey_b = pytest.MonkeyPatch()
    monkey_b.setattr(client_b, "_get_page", _boom)
    try:
        ctx_b = client_b._draft_context(target)
    finally:
        monkey_b.undo()
    assert ctx_b == EXPECTED_CTX
    assert client_b._draft_ctx_cache == {123: EXPECTED_CTX}


def test_pin_dropped_after_send_no_submitbutton2(draft_file):
    """Ветка без submitbutton2: submission_send делегирует submission_save."""
    target = _target()
    state.save_draft_pins({"123": dict(EXPECTED_CTX)})
    client = _make_client()
    monkey = pytest.MonkeyPatch()
    monkey.setattr(client, "_get_page", lambda path: _editsubmission_html())
    monkey.setattr(client, "_post_submission", lambda fields: None)
    try:
        client.submission_send(target)
    finally:
        monkey.undo()
    assert state.load_draft_pins() == {}
    assert client._draft_ctx_cache == {}


def test_pin_dropped_after_send_with_submitbutton2(draft_file):
    """Прямая ветка: submitbutton2 присутствует в форме."""
    target = _target()
    state.save_draft_pins({"123": dict(EXPECTED_CTX)})
    client = _make_client()
    posted: list[dict] = []
    monkey = pytest.MonkeyPatch()
    monkey.setattr(
        client, "_get_page", lambda path: _editsubmission_html(with_submit2=True)
    )
    monkey.setattr(client, "_post_submission", lambda fields: posted.append(fields))
    try:
        client.submission_send(target)
    finally:
        monkey.undo()
    assert state.load_draft_pins() == {}
    assert client._draft_ctx_cache == {}
    assert posted and "submitbutton2" in posted[0]

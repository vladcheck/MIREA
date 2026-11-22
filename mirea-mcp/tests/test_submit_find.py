"""Tests for mirea_mcp.tools.submit_tools._fuzzy_candidates (mirea_submit_find).

Без сети: клиент СДО и производные аббревиатуры подменяются фиктивными.
Фикстура смоделирована на реальном курсе PEPiS.
"""

import random

import pytest

import mirea_mcp.tools.submit_tools as submit_tools
from mirea_mcp.models import DisciplineGrades, Work

DISC_NAME = "Программирование электронных приборов и систем_Зачет (часть 1/2) [I.26-27]"

# url=None у последней работы — кандидат без страницы сдачи.
WORKS = [
    Work(
        name="Контрольная работа №1",
        url="https://online-edu.mirea.ru/mod/assign/view.php?id=952080",
    ),
    Work(
        name="Контрольная работа №2",
        url="https://online-edu.mirea.ru/mod/assign/view.php?id=952081",
    ),
    Work(
        name="Лабораторная работа 1-2 (1)",
        url="https://online-edu.mirea.ru/mod/assign/view.php?id=952082",
    ),
    Work(
        name="Лабораторная работа 3-4 (2)",
        url="https://online-edu.mirea.ru/mod/assign/view.php?id=952083",
    ),
    Work(
        name="Лабораторная работа 5-6 (3)",
        url="https://online-edu.mirea.ru/mod/assign/view.php?id=952084",
    ),
    Work(
        name="Лабораторная работа 7-8 (4)",
        url="https://online-edu.mirea.ru/mod/assign/view.php?id=952085",
    ),
    Work(
        name="Практические занятия 7-8 (ПР №4)",
        url="https://online-edu.mirea.ru/mod/assign/view.php?id=952086",
    ),
    Work(name="Работа без страницы сдачи 4", url=None),
]

ABBR_MAP = {"ПЭПИС": [DISC_NAME]}


class _FakeClient:
    def __init__(self, works):
        self._works = works

    def disciplines(self):
        return [DisciplineGrades(name=DISC_NAME, works=self._works)]


@pytest.fixture
def patched(monkeypatch):
    """Подменяет _get_client и load_or_derive фиктивными реализациями."""

    def _patch(works=None):
        works = WORKS if works is None else works
        monkeypatch.setattr(submit_tools, "_get_client", lambda: _FakeClient(works))
        monkeypatch.setattr(
            submit_tools.abbreviations,
            "load_or_derive",
            lambda _names: {"abbreviations": ABBR_MAP},
        )
        return works

    return _patch


def _titles(result):
    return [c["work_title"] for c in result["candidates"]]


def test_lr4_matches_both_labs(patched):
    patched()
    expected = ["Лабораторная работа 3-4 (2)", "Лабораторная работа 7-8 (4)"]
    assert _titles(submit_tools._fuzzy_candidates("ЛР4")) == expected
    assert _titles(submit_tools._fuzzy_candidates("ЛР 4")) == expected


def test_results_alphabetical_regardless_of_input_order(patched):
    shuffled = list(WORKS)
    random.Random(42).shuffle(shuffled)
    patched(shuffled)
    result = submit_tools._fuzzy_candidates("ЛР")
    titles = _titles(result)
    assert titles == sorted(titles)
    # и совпадает с порядком при исходном порядке работ
    patched(WORKS)
    assert _titles(submit_tools._fuzzy_candidates("ЛР")) == titles


def test_no_ranking_fields(patched):
    patched()
    result = submit_tools._fuzzy_candidates("ЛР4")
    assert set(result) == {"mode", "enact", "candidates"}
    assert result["mode"] == "fuzzy"
    assert result["enact"] is False
    for c in result["candidates"]:
        assert "score" not in c
        assert "matched_terms" not in c
        assert set(c) == {"url", "discipline", "work_title", "due", "submitted"}


def test_worktype_expansion(patched):
    patched()
    # «лр» расшифровывается в «лабораторная работа»; «4» подстрочно бьёт
    # в номер пары работ («3-4», «7-8 (4)»).
    assert _titles(submit_tools._fuzzy_candidates("лр 4")) == [
        "Лабораторная работа 3-4 (2)",
        "Лабораторная работа 7-8 (4)",
    ]
    # «пр» бьёт и в «Программирование» (дисциплина), и в «(ПР №4)», поэтому
    # «4» дополнительно сужает до работ с четвёркой — ПР №4 среди них.
    titles = _titles(submit_tools._fuzzy_candidates("пр 4"))
    assert "Практические занятия 7-8 (ПР №4)" in titles


def test_all_tokens_required(patched):
    patched()
    assert submit_tools._fuzzy_candidates("ПЕПиС ЛР4")["candidates"] == []
    assert submit_tools._fuzzy_candidates("несуществующее ЛР4")["candidates"] == []


def test_work_without_url_excluded(patched):
    patched()
    result = submit_tools._fuzzy_candidates("Работа без страницы сдачи")
    assert result["candidates"] == []


def test_empty_query_error(patched):
    patched()
    result = submit_tools._fuzzy_candidates("   ")
    assert result["error"] == "пустой запрос query"
    assert "hint" in result


def test_tool_schema_has_no_limit():
    import asyncio

    from fastmcp import Client

    from mirea_mcp.server import mcp

    async def _check():
        async with Client(mcp) as c:
            tools = await c.list_tools()
        tool = next(t for t in tools if t.name == "mirea_submit_find")
        schema = getattr(tool, "input_schema", None) or tool.inputSchema
        assert "limit" not in schema.get("properties", {})

    asyncio.run(_check())

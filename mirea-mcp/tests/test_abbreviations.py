"""
Tests for mirea_mcp.abbreviations
"""

import json

import pytest

from mirea_mcp import abbreviations as abbr
from mirea_mcp.abbreviations import ALGO_VERSION, derive, load_or_derive, source_hash

NAMES = [
    "Программирование электронных систем и приборов",
    "Информатика и вычислительная техника",
    "Основы схемотехники",
]


def test_punctuation_removed():
    result = derive(["Информатика и вычислительная техника (ИВТ)"])
    assert result == {"ИИВТИ": ["Информатика и вычислительная техника (ИВТ)"]}


def test_decorated_moodle_name_uses_base_only():
    name = (
        "Программирование электронных приборов и систем"
        "_Зачет (часть 1/2) [I.26-27]"
    )
    result = derive([name])
    assert result == {"ПЭПИС": [name]}


def test_decorated_moodle_name_second_case():
    name = "Компьютерный дизайн_Экзамен (часть 1/1) [I.26-27]"
    result = derive([name])
    assert result == {"КД": [name]}


def test_name_without_underscore_unchanged():
    result = derive(["Основы схемотехники"])
    assert result == {"ОС": ["Основы схемотехники"]}


def test_suffix_only_fallback_to_whole_name():
    # "_Зачет" alone: no base before "_", so the whole name is used.
    # "_" is stripped as punctuation, leaving the word "Зачет" -> "З".
    result = derive(["_Зачет"])
    assert result == {"З": ["_Зачет"]}


def test_multi_word_first_letters():
    result = derive(NAMES)
    assert "ПЭСИП" in result
    assert result["ОС"] == ["Основы схемотехники"]


def test_uppercase_regardless_of_input_case():
    result = derive(["информатика И ВЫЧИСЛИТЕЛЬНАЯ техника"])
    key = next(iter(result))
    assert key == key.upper()


def test_collision_keeps_all_names():
    result = derive(["Основы схемотехники", "Объектно-скалярные системы"])
    assert sorted(result["ОС"]) == sorted(
        ["Основы схемотехники", "Объектно-скалярные системы"]
    )


def test_empty_and_whitespace_names_skipped():
    result = derive(["", "   ", "Информатика"])
    assert list(result) == ["И"]


def test_key_order_first_seen():
    result = derive(NAMES)
    assert list(result) == ["ПЭСИП", "ИИВТ", "ОС"]


def test_source_hash_order_stable():
    assert source_hash(NAMES) == source_hash(list(reversed(NAMES)))


def test_source_hash_normalizes_case_and_whitespace():
    assert source_hash(["Основы  схемотехники"]) == source_hash(
        [" основы схемотехники "])


def test_cache_hit_roundtrip(tmp_path):
    cache = tmp_path / "cache" / "abbreviations.json"
    log_dir = tmp_path / "logs"
    first = load_or_derive(NAMES, cache_path=cache, log_dir=log_dir)
    assert first["refreshed"] is True
    second = load_or_derive(NAMES, cache_path=cache, log_dir=log_dir)
    assert second["refreshed"] is False
    assert second["abbreviations"] == first["abbreviations"]
    assert second["source_hash"] == first["source_hash"]
    # Only the first (refresh) call logs.
    logs = list(log_dir.glob("*.log"))
    assert len(logs) == 1
    assert "reason=hash_mismatch" in logs[0].read_text(encoding="utf-8")


def test_stale_algo_version_refreshes_with_algo_change(tmp_path):
    cache = tmp_path / "abbreviations.json"
    log_dir = tmp_path / "logs"
    # Simulate a cache written by the previous derive() algorithm.
    payload = {
        "source_hash": source_hash(NAMES),
        "algo": "1",
        "derived_at": "2026-01-01T00:00:00",
        "abbreviations": {"СТАРОЕ": NAMES},
    }
    cache.write_text(json.dumps(payload), encoding="utf-8")
    result = load_or_derive(NAMES, cache_path=cache, log_dir=log_dir)
    assert result["refreshed"] is True
    assert result["abbreviations"] == derive(NAMES)
    # Cache rewritten with the current algo.
    rewritten = json.loads(cache.read_text(encoding="utf-8"))
    assert rewritten["algo"] == ALGO_VERSION
    text = next(log_dir.glob("*.log")).read_text(encoding="utf-8")
    assert "reason=algo_change" in text


def test_algo_version_mismatch_via_monkeypatch(tmp_path, monkeypatch):
    cache = tmp_path / "abbreviations.json"
    log_dir = tmp_path / "logs"
    monkeypatch.setattr(abbr, "ALGO_VERSION", "1")
    first = load_or_derive(NAMES, cache_path=cache, log_dir=log_dir)
    assert first["refreshed"] is True
    # Same names, but the module-level algo now differs from the cache.
    monkeypatch.setattr(abbr, "ALGO_VERSION", "2")
    second = load_or_derive(NAMES, cache_path=cache, log_dir=log_dir)
    assert second["refreshed"] is True
    text = next(log_dir.glob("*.log")).read_text(encoding="utf-8")
    assert "reason=algo_change" in text
    # A third call with the matching algo is a cache hit again.
    third = load_or_derive(NAMES, cache_path=cache, log_dir=log_dir)
    assert third["refreshed"] is False


def test_cache_missing_algo_field_falls_back_to_hash_mismatch(tmp_path):
    cache = tmp_path / "abbreviations.json"
    log_dir = tmp_path / "logs"
    payload = {
        "source_hash": source_hash(NAMES),
        "derived_at": "2026-01-01T00:00:00",
        "abbreviations": {"СТАРОЕ": NAMES},
    }
    cache.write_text(json.dumps(payload), encoding="utf-8")
    result = load_or_derive(NAMES, cache_path=cache, log_dir=log_dir)
    assert result["refreshed"] is True
    text = next(log_dir.glob("*.log")).read_text(encoding="utf-8")
    assert "reason=hash_mismatch" in text
    assert "reason=algo_change" not in text


def test_changed_names_refresh_and_log(tmp_path):
    cache = tmp_path / "abbreviations.json"
    log_dir = tmp_path / "logs"
    first = load_or_derive(NAMES, cache_path=cache, log_dir=log_dir)
    old_hash = first["source_hash"]
    changed = NAMES + ["Физика"]
    result = load_or_derive(changed, cache_path=cache, log_dir=log_dir)
    assert result["refreshed"] is True
    assert "Ф" in result["abbreviations"]
    text = next(log_dir.glob("*.log")).read_text(encoding="utf-8")
    assert "reason=hash_mismatch" in text
    assert "disciplines=4" in text
    assert "abbreviations=4" in text
    assert f"want={result['source_hash']}" in text
    assert f"got={old_hash}" in text
    assert result["source_hash"] != old_hash


def test_forced_refresh_logs_forced(tmp_path):
    cache = tmp_path / "abbreviations.json"
    log_dir = tmp_path / "logs"
    load_or_derive(NAMES, cache_path=cache, log_dir=log_dir)
    result = load_or_derive(NAMES, cache_path=cache,
                            log_dir=log_dir, refresh=True)
    assert result["refreshed"] is True
    lines = next(log_dir.glob("*.log")
                 ).read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert "reason=forced" in lines[1]


def test_corrupt_cache_falls_back_to_derive(tmp_path):
    cache = tmp_path / "abbreviations.json"
    log_dir = tmp_path / "logs"
    cache.write_text("not json", encoding="utf-8")
    result = load_or_derive(NAMES, cache_path=cache, log_dir=log_dir)
    assert result["refreshed"] is True
    assert result["abbreviations"]["ПЭСИП"]


def test_cache_file_written_atomic_0644(tmp_path):
    cache = tmp_path / "sub" / "abbreviations.json"
    load_or_derive(NAMES, cache_path=cache, log_dir=tmp_path / "logs")
    assert cache.is_file()
    assert oct(cache.stat().st_mode & 0o777) == "0o644"
    payload = json.loads(cache.read_text(encoding="utf-8"))
    assert payload["source_hash"] == source_hash(NAMES)
    assert set(payload) >= {"source_hash", "derived_at", "abbreviations"}


@pytest.mark.parametrize("bad", [[], [""]])
def test_all_empty_names_valid(tmp_path, bad):
    result = load_or_derive(bad, cache_path=tmp_path /
                            "c.json", log_dir=tmp_path / "l")
    assert result["abbreviations"] == {}
    assert result["refreshed"] is True

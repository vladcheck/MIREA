"""Discipline-name abbreviation derivation with hash-checked file cache.

Pure derivation logic lives in :func:`derive` and :func:`source_hash`;
:func:`load_or_derive` wraps them with an on-disk cache and a refresh log.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import unicodedata
from datetime import datetime
from pathlib import Path

# Package root = parent of the mirea_mcp/ package directory.
_PKG_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CACHE = _PKG_ROOT / ".cache" / "abbreviations.json"
DEFAULT_LOG_DIR = _PKG_ROOT / ".logs"

# Bump when derive() semantics change; stale caches with a mismatched
# "algo" field are re-derived even if the source_hash is unchanged.
ALGO_VERSION: str = "2"

_PUNCT_CATEGORY_PREFIXES = ("P", "S")
_WORD_RE = re.compile(r"\S+")
# Administrative suffix separator in СДО names: "<base>_Зачет", "<base>_Экзамен", ...
_SUFFIX_SEP = "_"
# Bracketed / parenthesized segments inside the base name, e.g. "(часть 1/2)".
_BRACKETED_RE = re.compile(r"\[[^\]]*\]|\([^)]*\)")


def _base_name(name: str) -> str:
    """Strip the administrative suffix and its bracketed decoration.

    Moodle decorates discipline names as "<base>_Зачет (часть 1/2) [I.26-27]".
    When the "_" suffix separator is present with a non-empty base, only that
    base is abbreviated, with bracketed [...] / parenthesized (...) segments
    removed from it. Names without a usable "_" keep their full text so
    parenthetical acronyms like "(ИВТ)" still contribute letters.
    """
    head, sep, _tail = name.partition(_SUFFIX_SEP)
    if not sep or not head.strip():
        return name
    return _BRACKETED_RE.sub(" ", head)


def _words(name: str) -> list[str]:
    """Split a discipline name into words, stripping unicode punctuation."""
    stripped = "".join(
        ch for ch in name if not unicodedata.category(ch).startswith(_PUNCT_CATEGORY_PREFIXES)
    )
    return _WORD_RE.findall(stripped)


def derive(discipline_names: list[str]) -> dict[str, list[str]]:
    """Map each discipline name to the first-letter abbreviation.

    Punctuation is removed (unicode-aware), the name is split on
    whitespace, and the first letter of every word is uppercased and
    joined. The base discipline name is used: the part before the first
    "_" (administrative suffix separator) with bracketed / parenthesized
    segments removed. Collisions keep every full name; key order is
    first-seen. Empty / whitespace-only names are skipped.
    """
    abbreviations: dict[str, list[str]] = {}
    for name in discipline_names:
        words = _words(_base_name(name))
        if not words:
            continue
        abbrev = "".join(word[0].upper() for word in words)
        abbreviations.setdefault(abbrev, []).append(name)
    return abbreviations


def source_hash(names: list[str]) -> str:
    """Stable hash of the name list, insensitive to order, case, spacing."""
    normalized = sorted(
        " ".join(name.split()).casefold() for name in names
    )
    payload = json.dumps(normalized, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _log_refresh(
        log_dir: Path, reason: str, disciplines: int, abbreviations: int
) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    log_path = log_dir / f"{now:%Y-%m-%d}.log"
    line = (
        f"{now.isoformat(timespec='seconds')} refresh reason={reason} "
        f"disciplines={disciplines} abbreviations={abbreviations}\n"
    )
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(line)


def _write_cache(
        cache_path: Path, abbreviations: dict[str, list[str]], hash_value: str
) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = cache_path.with_suffix(cache_path.suffix + ".tmp")
    payload = {
        "source_hash": hash_value,
        "algo": ALGO_VERSION,
        "derived_at": datetime.now().isoformat(timespec="seconds"),
        "abbreviations": abbreviations,
    }
    tmp_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    os.chmod(tmp_path, 0o644)
    os.replace(tmp_path, cache_path)


def load_or_derive(
    names: list[str],
    *,
    refresh: bool = False,
    cache_path: Path = DEFAULT_CACHE,
    log_dir: Path = DEFAULT_LOG_DIR,
) -> dict:
    """Return abbreviations with cache; re-derive and log on mismatch/force.

    Cache hit requires the file to exist, its stored ``source_hash`` to
    match :func:`source_hash` of ``names``, its stored ``algo`` to equal
    :data:`ALGO_VERSION`, and ``refresh=False``.
    """
    hash_value = source_hash(names)
    algo_mismatch = False
    if not refresh and cache_path.is_file():
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            cached = None
        if (
            isinstance(cached, dict)
            and cached.get("source_hash") == hash_value
            and cached.get("algo") == ALGO_VERSION
            and isinstance(cached.get("abbreviations"), dict)
        ):
            cached["refreshed"] = False
            return cached
        algo_mismatch = (
            isinstance(cached, dict)
            and cached.get("source_hash") == hash_value
            and "algo" in cached
            and cached.get("algo") != ALGO_VERSION
        )

    abbreviations = derive(names)
    _write_cache(cache_path, abbreviations, hash_value)
    if refresh:
        reason = "forced"
    elif algo_mismatch:
        reason = "algo_change"
    else:
        reason = "hash_mismatch"
    _log_refresh(log_dir, reason, len(names), len(abbreviations))
    return {
        "abbreviations": abbreviations,
        "derived_at": datetime.now().isoformat(timespec="seconds"),
        "source_hash": hash_value,
        "refreshed": True,
    }

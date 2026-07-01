"""Tiny JSON-file store. One file, atomic writes, a lock for the scheduler+API.

Shape of db.json:
{
  "models":      { model_id: {id,name,lab,blurb,search_terms,release_match,
                              status,released_at,release_evidence,added_at} },
  "predictions": { model_id: <prediction dict from agent, plus meta> },
  "history":     { model_id: [ {generated_at, point_estimate, confidence, hit,
                               error_days, released_at} ... ] },
  "scores":      { resolved, hits, brier_sum, brier_n },
  "log":         [ {ts, msg} ... ]   # last ~120 activity lines
  "last_predict_refresh": iso, "last_release_check": iso
}
"""
from __future__ import annotations

import json
import os
import tempfile
import threading
from pathlib import Path
from typing import Any

from config import DATA_DIR
from models_seed import SEED_MODELS

_LOCK = threading.RLock()
_DB_PATH = DATA_DIR / "db.json"

_DEFAULT: dict[str, Any] = {
    "models": {},
    "predictions": {},
    "history": {},
    "scores": {"resolved": 0, "hits": 0, "brier_sum": 0.0, "brier_n": 0},
    "log": [],
    "last_predict_refresh": None,
    "last_release_check": None,
}


def _seed_models() -> dict[str, Any]:
    out: dict[str, Any] = {}
    for m in SEED_MODELS:
        out[m["id"]] = {
            **m,
            "status": "upcoming",
            "released_at": None,
            "release_evidence": None,
            "added_at": None,
        }
    return out


def _load_raw() -> dict[str, Any]:
    if _DB_PATH.exists():
        try:
            data = json.loads(_DB_PATH.read_text("utf-8"))
        except Exception:
            data = {}
    else:
        data = {}
    # Fill any missing top-level keys.
    for k, v in _DEFAULT.items():
        data.setdefault(k, json.loads(json.dumps(v)))
    # Merge any brand-new seed models (added to the seed list after first run)
    # without clobbering existing status/predictions.
    if not data["models"]:
        data["models"] = _seed_models()
    else:
        for m in SEED_MODELS:
            data["models"].setdefault(m["id"], {
                **m, "status": "upcoming", "released_at": None,
                "release_evidence": None, "added_at": None,
            })
            # keep static metadata fresh from the seed file
            existing = data["models"][m["id"]]
            for key in ("name", "lab", "blurb", "search_terms", "release_match"):
                if not existing.get(key):
                    existing[key] = m[key]
    return data


def _atomic_write(data: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(DATA_DIR), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        os.replace(tmp, _DB_PATH)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def load() -> dict[str, Any]:
    with _LOCK:
        return _load_raw()


def save(data: dict[str, Any]) -> None:
    with _LOCK:
        _atomic_write(data)


def update(mutator) -> dict[str, Any]:
    """Load, apply mutator(data) in-place, persist, return the new data."""
    with _LOCK:
        data = _load_raw()
        mutator(data)
        _atomic_write(data)
        return data


def log(data: dict[str, Any], msg: str, ts: str) -> None:
    entry = {"ts": ts, "msg": msg}
    data.setdefault("log", []).insert(0, entry)
    del data["log"][120:]

"""probabilities.ssh.codes — an AI that forecasts when unreleased frontier models
will ship, then grades itself against ai-tracker.

Backend: FastAPI + two background loops (predict refresh, release detection).
Public traffic reaches this through the Pi router, which buffers SSE/WebSockets,
so the frontend polls /api/state over plain HTTP.
"""
from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import agent
import config
import sources
import storage

STATIC_DIR = Path(__file__).resolve().parent / "static"
HIT_TOLERANCE_DAYS = int(os.getenv("PROB_HIT_TOLERANCE_DAYS", "45"))

_predict_gate = asyncio.Lock()  # never run two model calls at once


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_date(s: str | None):
    if not s:
        return None
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


# --------------------------------------------------------------------------- #
# Prediction + scoring core
# --------------------------------------------------------------------------- #
async def refresh_model(model_id: str) -> bool:
    """Run one prediction for model_id and persist it. Returns True on success."""
    data = storage.load()
    model = data["models"].get(model_id)
    if not model or model.get("status") == "released":
        return False
    async with _predict_gate:
        try:
            pred = await agent.predict(model)
        except Exception as exc:  # noqa: BLE001
            def _fail(d: dict[str, Any]):
                storage.log(d, f"⚠ predict failed for {model['name']}: {exc.__class__.__name__}: {exc}", now_iso())
            storage.update(_fail)
            return False

    def _apply(d: dict[str, Any]):
        prev = d["predictions"].get(model_id)
        # archive the previous point estimate into history (for the track record)
        if prev and prev.get("point_estimate"):
            d.setdefault("history", {}).setdefault(model_id, []).insert(0, {
                "generated_at": prev.get("generated_at"),
                "point_estimate": prev.get("point_estimate"),
                "point_estimate_label": prev.get("point_estimate_label"),
                "confidence": prev.get("confidence"),
            })
            del d["history"][model_id][12:]
        d["predictions"][model_id] = pred
        d["last_predict_refresh"] = now_iso()
        storage.log(d, f"✔ forecast updated for {model['name']}: {pred.get('point_estimate_label') or pred.get('point_estimate') or '—'} (conf {round(pred.get('confidence',0)*100)}%)", now_iso())
    storage.update(_apply)
    return True


def _finalize_release(d: dict[str, Any], model_id: str, evidence: dict[str, Any]) -> None:
    """Mark a model released and grade the last active prediction."""
    model = d["models"][model_id]
    if model.get("status") == "released":
        return
    actual = _parse_date(evidence.get("detectedAt"))
    model["status"] = "released"
    model["released_at"] = (evidence.get("detectedAt") or "")[:10]
    model["release_evidence"] = evidence

    pred = d["predictions"].get(model_id)
    error_days = None
    hit = None
    if pred and pred.get("point_estimate") and actual:
        pe = _parse_date(pred["point_estimate"])
        if pe:
            error_days = (actual - pe).days
            hit = abs(error_days) <= HIT_TOLERANCE_DAYS
    if pred:
        pred["resolved"] = True
        pred["actual_release"] = model["released_at"]
        pred["error_days"] = error_days
        pred["hit"] = hit

    scores = d.setdefault("scores", {"resolved": 0, "hits": 0, "brier_sum": 0.0, "brier_n": 0})
    scores["resolved"] += 1
    if hit:
        scores["hits"] += 1
    d.setdefault("history", {}).setdefault(model_id, []).insert(0, {
        "resolved_at": now_iso(),
        "actual_release": model["released_at"],
        "point_estimate": pred.get("point_estimate") if pred else None,
        "error_days": error_days,
        "hit": hit,
    })
    verdict = "no active estimate" if hit is None else ("HIT ✅" if hit else f"miss (off {error_days:+d}d)")
    storage.log(d, f"🚀 {model['name']} released ({model['released_at']}, via ai-tracker {evidence.get('via')}) — {verdict}", now_iso())


async def check_releases() -> None:
    data = storage.load()
    upcoming = [m for m in data["models"].values() if m.get("status") != "released"]
    for model in upcoming:
        try:
            evidence = await sources.detect_release(model)
        except Exception:
            evidence = None
        if not evidence:
            continue
        if evidence.get("via") == "addedModels":
            storage.update(lambda d, mid=model["id"], ev=evidence: _finalize_release(d, mid, ev))
        else:
            # weaker text-only signal: surface as a candidate, don't grade yet
            def _cand(d: dict[str, Any], mid=model["id"], ev=evidence):
                d["models"][mid]["release_candidate"] = ev
            storage.update(_cand)
    storage.update(lambda d: d.__setitem__("last_release_check", now_iso()))


# --------------------------------------------------------------------------- #
# Background loops
# --------------------------------------------------------------------------- #
def _is_stale(pred: dict[str, Any] | None) -> bool:
    if not pred or not pred.get("generated_at"):
        return True
    gen = pred["generated_at"]
    try:
        dt = datetime.fromisoformat(gen)
    except ValueError:
        return True
    age_h = (datetime.now(timezone.utc) - dt).total_seconds() / 3600
    return age_h >= config.PREDICT_REFRESH_HOURS


async def prediction_loop() -> None:
    if config.missing_api_key():
        storage.update(lambda d: storage.log(d, "⚠ OPENCODE_GO_API_KEY missing — forecasting disabled.", now_iso()))
        return
    await asyncio.sleep(3)
    while True:
        try:
            data = storage.load()
            stale = [m["id"] for m in data["models"].values()
                     if m.get("status") != "released" and _is_stale(data["predictions"].get(m["id"]))]
            for mid in stale:
                await refresh_model(mid)
                await asyncio.sleep(config.PREDICT_STAGGER_SECONDS)
        except Exception as exc:  # noqa: BLE001
            storage.update(lambda d, e=exc: storage.log(d, f"⚠ prediction loop error: {e}", now_iso()))
        await asyncio.sleep(30 * 60)  # re-scan for staleness every 30 min


async def release_loop() -> None:
    await asyncio.sleep(8)
    while True:
        try:
            await check_releases()
        except Exception as exc:  # noqa: BLE001
            storage.update(lambda d, e=exc: storage.log(d, f"⚠ release loop error: {e}", now_iso()))
        await asyncio.sleep(config.RELEASE_CHECK_MINUTES * 60)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    storage.update(lambda d: storage.log(d, "▶ probabilities service started.", now_iso()))
    tasks = [asyncio.create_task(prediction_loop()), asyncio.create_task(release_loop())]
    try:
        yield
    finally:
        for t in tasks:
            t.cancel()


app = FastAPI(title="probabilities", lifespan=lifespan)


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def _public_state() -> dict[str, Any]:
    data = storage.load()
    models_out = []
    for m in data["models"].values():
        models_out.append({
            "id": m["id"], "name": m["name"], "lab": m["lab"], "blurb": m.get("blurb", ""),
            "status": m.get("status", "upcoming"), "released_at": m.get("released_at"),
            "release_evidence": m.get("release_evidence"), "release_candidate": m.get("release_candidate"),
            "prediction": data["predictions"].get(m["id"]),
            "history": data.get("history", {}).get(m["id"], [])[:6],
        })
    # released last, then by confidence desc
    models_out.sort(key=lambda x: (x["status"] == "released",
                                   -((x["prediction"] or {}).get("confidence", 0))))
    scores = data.get("scores", {})
    resolved = scores.get("resolved", 0)
    hits = scores.get("hits", 0)
    return {
        "models": models_out,
        "scores": {
            "resolved": resolved, "hits": hits,
            "accuracy": round(hits / resolved, 4) if resolved else None,
            "tolerance_days": HIT_TOLERANCE_DAYS,
        },
        "meta": {
            "model": config.MODEL, "reasoning_effort": config.REASONING_EFFORT,
            "sources": ["Polymarket", "X / web leaks", "ai-tracker"],
            "ai_tracker_url": "https://ai-tracker.ssh.codes",
            "refresh_hours": config.PREDICT_REFRESH_HOURS,
        },
        "last_predict_refresh": data.get("last_predict_refresh"),
        "last_release_check": data.get("last_release_check"),
        "log": data.get("log", [])[:24],
        "now": now_iso(),
    }


@app.get("/api/state")
async def api_state():
    return JSONResponse(_public_state())


@app.get("/api/health")
async def api_health():
    return {"ok": True, "model": config.MODEL, "has_key": not config.missing_api_key(), "now": now_iso()}


def _check_admin(request: Request) -> None:
    if not config.ADMIN_TOKEN:
        raise HTTPException(403, "admin actions are disabled (no PROB_ADMIN_TOKEN set)")
    tok = request.headers.get("x-admin-token") or request.query_params.get("token") or ""
    if tok != config.ADMIN_TOKEN:
        raise HTTPException(401, "bad admin token")


@app.post("/api/refresh/{model_id}")
async def api_refresh(model_id: str, request: Request):
    _check_admin(request)
    data = storage.load()
    if model_id not in data["models"]:
        raise HTTPException(404, "unknown model")
    ok = await refresh_model(model_id)
    return {"ok": ok, "model": model_id}


@app.post("/api/models")
async def api_add_model(request: Request):
    _check_admin(request)
    body = await request.json()
    name = str(body.get("name", "")).strip()
    lab = str(body.get("lab", "")).strip()
    if not name or not lab:
        raise HTTPException(400, "name and lab are required")
    mid = str(body.get("id") or name).lower().strip().replace(" ", "-")
    mid = "".join(c for c in mid if c.isalnum() or c == "-")[:40] or "model"

    def _add(d: dict[str, Any]):
        d["models"][mid] = {
            "id": mid, "name": name, "lab": lab,
            "blurb": str(body.get("blurb", "")).strip()[:200],
            "search_terms": body.get("search_terms") or [name, f"{lab} {name}"],
            "release_match": body.get("release_match") or [name.lower()],
            "status": "upcoming", "released_at": None,
            "release_evidence": None, "added_at": now_iso(),
        }
        storage.log(d, f"➕ model added: {name} ({lab})", now_iso())
    storage.update(_add)
    asyncio.create_task(refresh_model(mid))
    return {"ok": True, "id": mid}


# --------------------------------------------------------------------------- #
# Static site
# --------------------------------------------------------------------------- #
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def root():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/favicon.ico")
async def favicon():
    fav = STATIC_DIR / "favicon.svg"
    if fav.exists():
        return FileResponse(str(fav))
    raise HTTPException(404)

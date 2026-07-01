"""The forecasting agent: gather signals -> deepseek-v4-pro (medium reasoning) ->
calibrated release-date probability distribution."""
from __future__ import annotations

import asyncio
import json
import re
from datetime import datetime, timezone
from typing import Any

import httpx

import config
import sources

_JSON_FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


# --------------------------------------------------------------------------- #
# Model call (OpenCode Go, OpenAI-compatible)
# --------------------------------------------------------------------------- #
async def call_model(messages: list[dict[str, str]], thinking: bool | None = None) -> str:
    use_thinking = config.THINKING_ENABLED if thinking is None else thinking
    payload: dict[str, Any] = {
        "model": config.MODEL,
        "messages": messages,
        "max_tokens": config.MODEL_MAX_TOKENS,
        "temperature": config.MODEL_TEMPERATURE,
    }
    if use_thinking:
        payload["thinking"] = {"type": "enabled"}
        if config.REASONING_EFFORT:
            payload["reasoning_effort"] = config.REASONING_EFFORT
    headers = {
        "Authorization": f"Bearer {config.OPENCODE_GO_API_KEY}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=config.MODEL_TIMEOUT) as client:
        r = await client.post(f"{config.OPENCODE_GO_BASE_URL}/chat/completions",
                              json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()
    return data["choices"][0]["message"]["content"] or ""


# --------------------------------------------------------------------------- #
# Research
# --------------------------------------------------------------------------- #
async def build_research(model: dict[str, Any]) -> dict[str, Any]:
    name, lab = model["name"], model["lab"]
    terms = model.get("search_terms", [name])
    pm, xw, cad = await asyncio.gather(
        sources.polymarket(f"{lab} {name}", terms),
        sources.x_web_search(name, lab, terms),
        sources.tracker_cadence(lab, name),
    )
    return {"polymarket": pm, "x_web": xw, "cadence": cad}


SYSTEM_PROMPT = (
    "You are a sharp, calibrated forecasting analyst who predicts when unreleased "
    "frontier AI models will be released. You weigh prediction-market odds, leaks, "
    "rumours, official employee posts, and each lab's historical release cadence. "
    "You are honest about uncertainty, never overconfident, and you reason from the "
    "evidence provided plus your own knowledge of the field. You output ONLY a single "
    "JSON object — no prose outside it."
)


def build_user_prompt(model: dict[str, Any], research: dict[str, Any]) -> str:
    name, lab = model["name"], model["lab"]
    return f"""TODAY: {_today()}
TARGET MODEL: {name}  (lab: {lab})
CONTEXT: {model.get('blurb','')}

=== POLYMARKET — prediction-market odds ===
{sources.format_polymarket(research['polymarket'])}

=== X / WEB — recent leaks, rumours, official posts ===
{sources.format_x_web(research['x_web'])}

=== HISTORICAL RELEASE CADENCE ({lab}, via ai-tracker) ===
{sources.format_cadence(research['cadence'])}

TASK:
Estimate when {name} will be publicly released. Build a probability distribution
over 4-6 forward-looking time windows starting from TODAY (use calendar quarters or
month ranges, ending with an open-ended "later / not soon" bucket). Give a single
most-likely point-estimate date. Consider that the model may ALREADY be released — if
the evidence clearly shows it shipped, set "released": true.

Return ONLY this JSON object (probabilities are 0..1 and the windows must sum to ~1):
{{
  "released": false,
  "point_estimate": "YYYY-MM-DD",
  "point_estimate_label": "human-friendly date, e.g. 'mid-November 2026'",
  "confidence": 0.0,
  "windows": [
    {{"label": "Jul-Sep 2026", "prob": 0.0}},
    {{"label": "Oct-Dec 2026", "prob": 0.0}},
    {{"label": "Q1 2027", "prob": 0.0}},
    {{"label": "H2 2027 or later", "prob": 0.0}}
  ],
  "summary": "2-3 sentence rationale citing the strongest signals",
  "key_signals": ["short signal 1", "short signal 2", "short signal 3"],
  "polymarket_note": "one line on what the markets imply (or 'no direct market')",
  "sources_used": ["polymarket", "x_web", "cadence"]
}}"""


# --------------------------------------------------------------------------- #
# Parsing / normalisation
# --------------------------------------------------------------------------- #
def _extract_json(text: str) -> dict[str, Any] | None:
    m = _JSON_FENCE.search(text)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # first balanced { .. } scan
    start = text.find("{")
    while start != -1:
        depth = 0
        for i in range(start, len(text)):
            c = text[i]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    chunk = text[start:i + 1]
                    try:
                        return json.loads(chunk)
                    except Exception:
                        break
        start = text.find("{", start + 1)
    return None


def _clamp01(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, v))


def _normalize(raw: dict[str, Any]) -> dict[str, Any]:
    windows = []
    for w in raw.get("windows", []) or []:
        if not isinstance(w, dict):
            continue
        label = str(w.get("label", "")).strip()
        if not label:
            continue
        windows.append({"label": label[:40], "prob": _clamp01(w.get("prob"))})
    windows = windows[:6]
    total = sum(w["prob"] for w in windows)
    if total > 0:
        for w in windows:
            w["prob"] = round(w["prob"] / total, 4)
    conf = _clamp01(raw.get("confidence"))
    if conf == 0.0 and windows:
        conf = max(w["prob"] for w in windows)

    pe = str(raw.get("point_estimate", "")).strip()
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", pe):
        pe = ""

    signals = [str(s).strip()[:160] for s in (raw.get("key_signals") or []) if str(s).strip()][:6]
    return {
        "released": bool(raw.get("released", False)),
        "point_estimate": pe,
        "point_estimate_label": str(raw.get("point_estimate_label", "")).strip()[:80],
        "confidence": round(conf, 4),
        "windows": windows,
        "summary": str(raw.get("summary", "")).strip()[:600],
        "key_signals": signals,
        "polymarket_note": str(raw.get("polymarket_note", "")).strip()[:220],
        "sources_used": [str(s) for s in (raw.get("sources_used") or [])][:6],
    }


# --------------------------------------------------------------------------- #
# Top-level prediction
# --------------------------------------------------------------------------- #
async def predict(model: dict[str, Any]) -> dict[str, Any]:
    """Return a normalised prediction dict (with meta) for one model.
    Raises on hard failures so the caller can keep the previous prediction."""
    research = await build_research(model)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(model, research)},
    ]
    # Up to 3 tries. deepseek-v4-pro occasionally returns an empty/garbled body;
    # the final attempt drops thinking to force a plain-text JSON answer.
    raw = None
    last_err = "no attempts"
    for attempt in range(3):
        try:
            content = await call_model(messages, thinking=(attempt < 2))
        except Exception as exc:  # noqa: BLE001
            last_err = f"call error: {exc}"
            await asyncio.sleep(2)
            continue
        raw = _extract_json(content)
        if raw is not None:
            break
        last_err = "no parseable JSON in response" + (" (empty body)" if not content.strip() else "")
        await asyncio.sleep(1)
    if raw is None:
        raise ValueError(f"model failed after retries: {last_err}")
    pred = _normalize(raw)
    pred["generated_at"] = _now_iso()
    pred["model_used"] = config.MODEL
    pred["reasoning_effort"] = config.REASONING_EFFORT
    # keep a compact snapshot of the evidence the call saw (for the UI / audit)
    pred["evidence"] = {
        "polymarket": research["polymarket"]["markets"][:6],
        "polymarket_note": research["polymarket"]["note"],
        "x_web": research["x_web"]["results"][:8],
        "x_web_note": research["x_web"]["note"],
        "cadence": research["cadence"]["recent"][:6],
        "cadence_note": research["cadence"]["note"],
    }
    return pred

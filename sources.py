"""Live data the forecasting agent reasons over:

  * Polymarket  — prediction-market odds on model releases (implied probabilities)
  * X / web     — recent leaks, rumours, and official posts (DuckDuckGo text search)
  * ai-tracker  — historical release cadence + authoritative release detection

Every fetcher degrades gracefully: on any error it returns an empty result plus a
short note, so a flaky network never breaks a prediction.
"""
from __future__ import annotations

import asyncio
import json
import re
from typing import Any

import httpx

from config import AI_TRACKER_URL, POLYMARKET_BASE

_UA = {"User-Agent": "probabilities.ssh.codes forecaster/1.0"}
_RELEASE_WORDS = ("release", "launch", "debut", "announce", "available", "ship", "drop", "by ")


# ----------------------------------------------------------------------------- #
# Polymarket
# ----------------------------------------------------------------------------- #
def _as_list(v: Any) -> list:
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        try:
            parsed = json.loads(v)
            return parsed if isinstance(parsed, list) else []
        except Exception:
            return []
    return []


async def polymarket(query: str, terms: list[str]) -> dict[str, Any]:
    """Return {markets: [...], note: str}. Each market has question, odds, endDate."""
    url = f"{POLYMARKET_BASE}/public-search"
    params = {"q": query, "limit_per_type": 12, "events_status": "active"}
    markets: list[dict[str, Any]] = []
    seen: set[str] = set()
    lows = [t.lower() for t in terms] + [query.lower()]
    try:
        async with httpx.AsyncClient(timeout=25, headers=_UA) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
    except Exception as exc:  # noqa: BLE001
        return {"markets": [], "note": f"Polymarket unavailable ({exc.__class__.__name__})."}

    for ev in data.get("events", []) or []:
        ev_title = (ev.get("title") or "").strip()
        for mk in ev.get("markets", []) or []:
            q = (mk.get("question") or "").strip()
            if not q or q in seen:
                continue
            hay = f"{ev_title} {q} {mk.get('description','')}".lower()
            relevant = any(t in hay for t in lows) or any(w in hay for w in _RELEASE_WORDS)
            if not relevant:
                continue
            outs = _as_list(mk.get("outcomes"))
            prices = _as_list(mk.get("outcomePrices"))
            odds = []
            for i, name in enumerate(outs):
                try:
                    p = float(prices[i])
                except (IndexError, ValueError, TypeError):
                    p = None
                odds.append({"outcome": str(name), "prob": p})
            try:
                vol = float(mk.get("volume") or 0)
            except (ValueError, TypeError):
                vol = 0.0
            seen.add(q)
            markets.append({
                "event": ev_title,
                "question": q,
                "odds": odds,
                "endDate": mk.get("endDate"),
                "volume": vol,
                "closed": bool(mk.get("closed")),
            })

    markets.sort(key=lambda m: m["volume"], reverse=True)
    markets = markets[:10]
    note = f"{len(markets)} relevant active market(s)." if markets else "No directly relevant markets found."
    return {"markets": markets, "note": note}


def format_polymarket(pm: dict[str, Any]) -> str:
    if not pm["markets"]:
        return pm["note"]
    lines = []
    for m in pm["markets"]:
        odds = ", ".join(
            f"{o['outcome']}={round(o['prob']*100)}%" if o["prob"] is not None else f"{o['outcome']}=?"
            for o in m["odds"]
        )
        end = (m.get("endDate") or "")[:10]
        vol = f"${round(m['volume']):,}" if m["volume"] else "$0"
        lines.append(f"- \"{m['question']}\" [{odds}] resolves≤{end} vol={vol}")
    return "\n".join(lines)


# ----------------------------------------------------------------------------- #
# X / web search (DuckDuckGo, no API key)
# ----------------------------------------------------------------------------- #
def _ddg_sync(queries: list[str], per_query: int = 6) -> list[dict[str, str]]:
    try:
        from ddgs import DDGS  # type: ignore
    except Exception:
        try:
            from duckduckgo_search import DDGS  # type: ignore
        except Exception:
            return []
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    try:
        with DDGS() as ddgs:
            for q in queries:
                try:
                    for item in ddgs.text(q, max_results=per_query):
                        href = item.get("href") or item.get("url") or ""
                        title = item.get("title") or ""
                        key = href or title
                        if not key or key in seen:
                            continue
                        seen.add(key)
                        out.append({
                            "title": title.strip(),
                            "body": (item.get("body") or "").strip(),
                            "href": href.strip(),
                            "query": q,
                        })
                except Exception:
                    continue
    except Exception:
        return out
    return out


async def x_web_search(name: str, lab: str, terms: list[str]) -> dict[str, Any]:
    queries = [
        f"{name} release date",
        f"{name} leak rumor",
        f"{lab} {name} announcement",
        f'"{name}" twitter',
    ]
    # de-dupe extra search terms into the query set
    for t in terms:
        if t.lower() not in {q.lower() for q in queries}:
            queries.append(t)
    results = await asyncio.to_thread(_ddg_sync, queries[:5], 6)
    results = results[:14]
    note = f"{len(results)} web/X snippet(s)." if results else "No web/X snippets (search unavailable)."
    return {"results": results, "note": note}


def format_x_web(xw: dict[str, Any]) -> str:
    if not xw["results"]:
        return xw["note"]
    lines = []
    for r in xw["results"]:
        body = re.sub(r"\s+", " ", r["body"])[:220]
        src = r["href"].replace("https://", "").replace("http://", "")[:60]
        lines.append(f"- {r['title'][:110]} — {body} ({src})")
    return "\n".join(lines)


# ----------------------------------------------------------------------------- #
# ai-tracker: cadence + release detection
# ----------------------------------------------------------------------------- #
def _added_model_strings(ev: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for am in ev.get("addedModels", []) or []:
        if isinstance(am, str):
            out.append(am)
        elif isinstance(am, dict):
            out.append(str(am.get("name") or am.get("id") or am.get("model") or am))
        else:
            out.append(str(am))
    return out


async def _fetch_events(limit: int = 400) -> list[dict[str, Any]]:
    try:
        async with httpx.AsyncClient(timeout=20, headers=_UA) as client:
            r = await client.get(f"{AI_TRACKER_URL}/api/events", params={"limit": limit})
            r.raise_for_status()
            data = r.json()
    except Exception:
        return []
    return data.get("events", []) if isinstance(data, dict) else (data or [])


async def tracker_cadence(lab: str, name: str) -> dict[str, Any]:
    events = await _fetch_events(400)
    lab_l = lab.lower()
    lab_tokens = [t for t in re.split(r"\W+", lab_l) if len(t) > 2]
    recent: list[dict[str, str]] = []
    for ev in events:
        added = _added_model_strings(ev)
        if not added:
            continue
        blob = (" ".join(added) + " " + (ev.get("sourceName") or "")).lower()
        if any(tok in blob for tok in lab_tokens):
            for a in added[:4]:
                recent.append({"model": a[:80], "detectedAt": (ev.get("detectedAt") or "")[:10],
                               "source": ev.get("sourceName") or ""})
    # newest first, dedup
    seen: set[str] = set()
    uniq = []
    for r in sorted(recent, key=lambda x: x["detectedAt"], reverse=True):
        k = r["model"].lower()
        if k in seen:
            continue
        seen.add(k)
        uniq.append(r)
    note = f"{len(uniq)} recent {lab} model add(s) seen by ai-tracker." if uniq else \
        f"No recent {lab} model adds recorded by ai-tracker."
    return {"recent": uniq[:8], "note": note}


def format_cadence(cad: dict[str, Any]) -> str:
    if not cad["recent"]:
        return cad["note"]
    return "\n".join(f"- {r['model']} — first seen {r['detectedAt']} ({r['source']})"
                     for r in cad["recent"])


async def detect_release(model: dict[str, Any]) -> dict[str, Any] | None:
    """Authoritative release check. Returns evidence dict if ai-tracker has seen
    this model ship, else None. Matches distinctive release tokens against added
    models / event diffs, preferring addedModels hits (fewest false positives)."""
    events = await _fetch_events(400)
    tokens = [t.lower() for t in model.get("release_match", []) if t]
    if not tokens:
        return None
    best = None
    for ev in events:
        added_blob = " ".join(_added_model_strings(ev)).lower()
        diff_blob = (ev.get("diff") or "")[:4000].lower()
        title_blob = (ev.get("sourceName") or "").lower()
        hit_added = any(tok in added_blob for tok in tokens)
        hit_text = any(tok in diff_blob or tok in title_blob for tok in tokens)
        if not (hit_added or hit_text):
            continue
        matched = next((t for t in tokens if t in added_blob or t in diff_blob or t in title_blob), tokens[0])
        evidence = {
            "detectedAt": ev.get("detectedAt"),
            "source": ev.get("sourceName") or "",
            "url": ev.get("url") or "",
            "matched": matched,
            "via": "addedModels" if hit_added else "text",
            "eventId": ev.get("id"),
        }
        # Prefer an addedModels hit; among those, the earliest detection.
        if hit_added:
            if best is None or best["via"] != "addedModels" or \
               (evidence.get("detectedAt") or "") < (best.get("detectedAt") or "z"):
                best = evidence
        elif best is None:
            best = evidence
    return best

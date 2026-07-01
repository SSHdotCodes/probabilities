"""Runtime configuration for the probabilities agent/site.

Secrets (the OpenCode Go API key) are reused from pro-ai.ssh.codes by injecting
its env at deploy time — see README. Nothing sensitive is hard-coded here.
"""
from __future__ import annotations

import os
from pathlib import Path


def _get(name: str, default: str = "") -> str:
    return (os.getenv(name) or default).strip()


# --- Model (OpenCode Go, reusing pro-ai's key) ---------------------------------
OPENCODE_GO_BASE_URL = _get("OPENCODE_GO_BASE_URL", "https://opencode.ai/zen/go/v1").rstrip("/")
OPENCODE_GO_API_KEY = _get("OPENCODE_GO_API_KEY")
MODEL = _get("PROB_MODEL", "deepseek-v4-pro")
REASONING_EFFORT = _get("PROB_REASONING_EFFORT", "medium")   # user asked for medium
# thinking + json_object returns corrupt JSON on this endpoint, so we keep thinking
# on but parse JSON out of free text instead of using response_format.
THINKING_ENABLED = _get("PROB_THINKING", "enabled").lower() != "disabled"
MODEL_TIMEOUT = int(_get("PROB_MODEL_TIMEOUT", "240"))
MODEL_MAX_TOKENS = int(_get("PROB_MAX_TOKENS", "6000"))
MODEL_TEMPERATURE = float(_get("PROB_TEMPERATURE", "0.35"))

# --- External data sources -----------------------------------------------------
AI_TRACKER_URL = _get("AI_TRACKER_URL", "http://127.0.0.1:8788").rstrip("/")
POLYMARKET_BASE = _get("POLYMARKET_BASE", "https://gamma-api.polymarket.com").rstrip("/")

# --- Storage -------------------------------------------------------------------
# Keep data OUTSIDE the app dir — rasppost release wipes the app dir on redeploy.
DATA_DIR = Path(_get("PROB_DATA_DIR", str(Path(__file__).resolve().parent / "data")))

# --- Scheduler -----------------------------------------------------------------
PREDICT_REFRESH_HOURS = float(_get("PROB_PREDICT_REFRESH_HOURS", "12"))
RELEASE_CHECK_MINUTES = float(_get("PROB_RELEASE_CHECK_MINUTES", "60"))
# Space out per-model model calls so we never hammer the endpoint.
PREDICT_STAGGER_SECONDS = float(_get("PROB_PREDICT_STAGGER_SECONDS", "8"))

# Optional token to gate the "add model" admin endpoint (blank = disabled).
ADMIN_TOKEN = _get("PROB_ADMIN_TOKEN")

PORT = int(_get("PORT", "8199"))
PUBLIC_URL = _get("PROB_PUBLIC_URL", "https://probabilities.ssh.codes")


def missing_api_key() -> bool:
    return not OPENCODE_GO_API_KEY

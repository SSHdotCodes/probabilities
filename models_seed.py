"""Seed list of anticipated, not-yet-released frontier models.

These are starting blocks; the agent researches live signals for each and the
scheduler retires a model (status -> "released") the moment ai-tracker sees it
ship. `search_terms` widen the Polymarket / web queries; `release_match` are the
distinctive tokens used to recognise the release in ai-tracker events.

Grounding note (refreshed 2026-06-30): every entry below is a model that has NOT
publicly shipped yet. Blurbs cite the lab's most recent *released* model plus the
observed cadence between its prior releases, and give a cadence-derived predicted
window. Released reference points used here:
  * OpenAI     — GPT-5.4 (Mar 5), GPT-5.5 (Apr 23), GPT-5.6 (Jun 26 2026)
  * Anthropic  — Opus 4.5 (Nov'25) -> 4.6 (Feb) -> 4.7 (Apr 16) -> 4.8 (May 28);
                 Sonnet 5 (Jun 30), Haiku 4.5 (Oct'25), Fable 5 (Jun 9 2026)
  * Google     — Gemini 3 (Nov'25), Gemini 3.5 Flash (May 19 2026)
  * xAI        — Grok 4.3 shipped; Grok 5 still training (slipped Q1 -> Q3 2026)
  * DeepSeek   — V4 (Apr 24 2026)
  * Meta       — pivoted from Llama to Muse Spark (Meta Superintelligence Labs, Apr 8 2026)
  * Alibaba    — Qwen3.7-Max (May 2026)
  * Moonshot   — Kimi K2.5 (Jan) -> K2.6 (Apr) -> K2.7 Code (Jun 12 2026)
  * Mistral    — Mistral Large 3 (Dec 2 2025)
  * MiniMax    — M2.1 (Dec 23 2025)
  * Baidu      — ERNIE 5.0, then ERNIE 5.1 (May 9 2026)
"""
from __future__ import annotations

SEED_MODELS = [
    {
        "id": "gpt-5.7",
        "name": "GPT-5.7",
        "lab": "OpenAI",
        "blurb": "OpenAI's next GPT-5 point release after GPT-5.6 (shipped Jun 26 2026). "
                 "GPT-5.4 -> 5.5 -> 5.6 landed on a ~monthly-to-six-week cadence, so 5.7 is "
                 "expected around Aug-Sep 2026.",
        "search_terms": ["GPT-5.7", "OpenAI GPT-5.7 release", "GPT 5.7 launch"],
        "release_match": ["gpt-5.7", "gpt 5.7", "gpt5.7"],
    },
    {
        "id": "gpt-6",
        "name": "GPT-6",
        "lab": "OpenAI",
        "blurb": "OpenAI's next flagship frontier model after the GPT-5.x line (GPT-5.5 Apr 2026, "
                 "GPT-5.6 Jun 2026). Full-integer jumps trail the 5.x point releases; expected "
                 "late 2026-2027.",
        "search_terms": ["GPT-6", "OpenAI next frontier model", "OpenAI GPT-6 release"],
        "release_match": ["gpt-6", "gpt 6"],
    },
    {
        "id": "gemini-4",
        "name": "Gemini 4",
        "lab": "Google DeepMind",
        "blurb": "Google DeepMind's next-generation successor to the Gemini 3 family (Gemini 3 "
                 "Nov 2025, Gemini 3.5 Flash May 2026). A major-version jump is expected around "
                 "late 2026.",
        "search_terms": ["Gemini 4", "Google DeepMind Gemini 4 release", "Gemini 4 Ultra"],
        "release_match": ["gemini 4", "gemini-4", "gemini4"],
    },
    {
        "id": "claude-opus-4-9",
        "name": "Claude Opus 4.9",
        "lab": "Anthropic",
        "blurb": "Anthropic's next Opus point release after Opus 4.8 (May 28 2026). Opus "
                 "4.5 -> 4.6 -> 4.7 -> 4.8 shipped roughly every 1-2 months, so 4.9 is expected "
                 "around Jul-Aug 2026.",
        "search_terms": ["Claude Opus 4.9", "Anthropic Opus 4.9 release", "Claude Opus 4.9 launch"],
        "release_match": ["opus 4.9", "opus-4.9", "claude opus 4.9"],
    },
    {
        "id": "claude-opus-5",
        "name": "Claude Opus 5",
        "lab": "Anthropic",
        "blurb": "Anthropic's next major Opus-tier model after the Opus 4.x line (latest Opus 4.8, "
                 "May 2026). A major-version jump is expected late 2026-early 2027.",
        "search_terms": ["Claude Opus 5", "Anthropic Claude 5 Opus release", "Claude Opus 5"],
        "release_match": ["opus 5", "opus-5", "claude 5 opus", "claude opus 5"],
    },
    {
        "id": "claude-sonnet-5-1",
        "name": "Claude Sonnet 5.1",
        "lab": "Anthropic",
        "blurb": "Anthropic's next Sonnet point release after Claude Sonnet 5 (launched Jun 30 2026). "
                 "Sonnet has taken point bumps (4.5 -> 4.6) on a multi-month cadence, so 5.1 is "
                 "expected around Q4 2026.",
        "search_terms": ["Claude Sonnet 5.1", "Anthropic Sonnet 5.1 release", "Claude Sonnet 5.1 launch"],
        "release_match": ["sonnet 5.1", "sonnet-5.1", "claude sonnet 5.1"],
    },
    {
        "id": "claude-haiku-5",
        "name": "Claude Haiku 5",
        "lab": "Anthropic",
        "blurb": "Anthropic's next-generation Haiku after Haiku 4.5 (Oct 2025), as the Opus and "
                 "Sonnet lines move to v5. Expected around Q3-Q4 2026.",
        "search_terms": ["Claude Haiku 5", "Anthropic Haiku 5 release", "Claude Haiku 5 launch"],
        "release_match": ["haiku 5", "haiku-5", "claude haiku 5"],
    },
    {
        "id": "grok-5",
        "name": "Grok 5",
        "lab": "xAI",
        "blurb": "xAI's Grok 5, still in training as of mid-2026 after slipping from Q1 to Q2; "
                 "expected Q3 2026 (latest shipped is Grok 4.3).",
        "search_terms": ["Grok 5", "xAI Grok 5 release date"],
        "release_match": ["grok 5", "grok-5", "grok5"],
    },
    {
        "id": "grok-6",
        "name": "Grok 6",
        "lab": "xAI",
        "blurb": "xAI's next Grok generation after the still-unreleased Grok 5; expected 2027 "
                 "given xAI's roughly yearly major cadence.",
        "search_terms": ["Grok 6", "xAI Grok 6 release", "Grok 6 launch"],
        "release_match": ["grok 6", "grok-6", "grok6"],
    },
    {
        "id": "deepseek-v5",
        "name": "DeepSeek V5",
        "lab": "DeepSeek",
        "blurb": "DeepSeek's next base/reasoning generation after V4 (Apr 24 2026). V3 -> V4 spanned "
                 "roughly a year, so V5 is expected in 2027.",
        "search_terms": ["DeepSeek V5", "DeepSeek-V5 release", "DeepSeek V5 launch"],
        "release_match": ["deepseek v5", "deepseek-v5", "deepseekv5"],
    },
    {
        "id": "muse-spark-2",
        "name": "Muse Spark 2",
        "lab": "Meta",
        "blurb": "Meta Superintelligence Labs' successor to Muse Spark (Apr 8 2026), the "
                 "closed-weight model that replaced the Llama line. First-of-line, so timing is "
                 "uncertain - expected 2027.",
        "search_terms": ["Muse Spark 2", "Meta Muse Spark 2 release", "Meta Superintelligence Labs Muse Spark"],
        "release_match": ["muse spark 2", "muse-spark-2", "muse spark 2.0"],
    },
    {
        "id": "qwen4-max",
        "name": "Qwen4-Max",
        "lab": "Alibaba",
        "blurb": "Alibaba's next flagship Qwen after the Qwen3.x line (latest Qwen3.7-Max, May 2026). "
                 "A major Qwen4 jump is expected late 2026-2027.",
        "search_terms": ["Qwen4-Max", "Alibaba Qwen 4 release", "Qwen4 Max launch"],
        "release_match": ["qwen4", "qwen 4", "qwen-4"],
    },
    {
        "id": "kimi-k2.8",
        "name": "Kimi K2.8",
        "lab": "Moonshot AI",
        "blurb": "Moonshot AI's next Kimi K2 iteration after K2.7 Code (Jun 12 2026). K2.5 (Jan) -> "
                 "K2.6 (Apr) -> K2.7 (Jun) shipped on a roughly quarterly cadence, so K2.8 is "
                 "expected around Q3 2026.",
        "search_terms": ["Kimi K2.8", "Moonshot AI Kimi K2.8 release", "Kimi K2.8 launch"],
        "release_match": ["kimi k2.8", "kimi-k2.8", "k2.8"],
    },
    {
        "id": "mistral-large-4",
        "name": "Mistral Large 4",
        "lab": "Mistral AI",
        "blurb": "Mistral AI's next flagship after Mistral Large 3 (Dec 2 2025). Large 2 -> Large 3 "
                 "spanned roughly a year, so a Large 4 is expected around late 2026-2027.",
        "search_terms": ["Mistral Large 4", "Mistral AI Large 4 release", "Mistral Large 4 launch"],
        "release_match": ["mistral large 4", "mistral-large-4", "mistral large4"],
    },
    {
        "id": "minimax-m3",
        "name": "MiniMax M3",
        "lab": "MiniMax",
        "blurb": "MiniMax's next-generation model after the M2 line (M2.1, Dec 23 2025). A major M3 "
                 "jump is expected around 2026.",
        "search_terms": ["MiniMax M3", "MiniMax M3 release", "MiniMax M3 launch"],
        "release_match": ["minimax m3", "minimax-m3", "minimax m3.0"],
    },
    {
        "id": "ernie-5-2",
        "name": "ERNIE 5.2",
        "lab": "Baidu",
        "blurb": "Baidu's next ERNIE point release after ERNIE 5.1 (May 9 2026). ERNIE 5.0 -> 5.1 "
                 "were fast successive point releases, so 5.2 is expected around Q3 2026.",
        "search_terms": ["ERNIE 5.2", "Baidu ERNIE 5.2 release", "ERNIE 5.2 launch"],
        "release_match": ["ernie 5.2", "ernie-5.2", "ernie5.2"],
    },
]

"""Seed list of anticipated, not-yet-released frontier models.

These are starting blocks; the agent researches live signals for each and the
scheduler retires a model (status -> "released") the moment ai-tracker sees it
ship. `search_terms` widen the Polymarket / web queries; `release_match` are the
distinctive tokens used to recognise the release in ai-tracker events.
"""
from __future__ import annotations

SEED_MODELS = [
    {
        "id": "gpt-6",
        "name": "GPT-6",
        "lab": "OpenAI",
        "blurb": "OpenAI's next flagship frontier model after the GPT-5.x line.",
        "search_terms": ["GPT-6", "OpenAI next frontier model", "OpenAI GPT-6 release"],
        "release_match": ["gpt-6", "gpt 6"],
    },
    {
        "id": "gemini-4",
        "name": "Gemini 4",
        "lab": "Google DeepMind",
        "blurb": "Google DeepMind's successor to the Gemini 3 family.",
        "search_terms": ["Gemini 4", "Google DeepMind Gemini 4 release", "Gemini 4 Ultra"],
        "release_match": ["gemini 4", "gemini-4", "gemini4"],
    },
    {
        "id": "claude-opus-5",
        "name": "Claude Opus 5",
        "lab": "Anthropic",
        "blurb": "Anthropic's next Opus-tier model after the Claude 4.x / Opus 4.8 line.",
        "search_terms": ["Claude Opus 5", "Anthropic Claude 5 Opus release", "Claude Opus 5"],
        "release_match": ["opus 5", "opus-5", "claude 5 opus", "claude opus 5"],
    },
    {
        "id": "grok-6",
        "name": "Grok 6",
        "lab": "xAI",
        "blurb": "xAI's next Grok generation after Grok 4/5.",
        "search_terms": ["Grok 6", "xAI Grok 6 release", "Grok 6 launch"],
        "release_match": ["grok 6", "grok-6", "grok6"],
    },
    {
        "id": "deepseek-v5",
        "name": "DeepSeek V5",
        "lab": "DeepSeek",
        "blurb": "DeepSeek's next base/reasoning generation after V4.",
        "search_terms": ["DeepSeek V5", "DeepSeek-V5 release", "DeepSeek V5 launch"],
        "release_match": ["deepseek v5", "deepseek-v5", "deepseekv5"],
    },
    {
        "id": "grok-5",
        "name": "Grok 5",
        "lab": "xAI",
        "blurb": "xAI's Grok 5, the generation expected immediately after Grok 4.",
        "search_terms": ["Grok 5", "xAI Grok 5 release date"],
        "release_match": ["grok 5", "grok-5", "grok5"],
    },
    {
        "id": "qwen4-max",
        "name": "Qwen4-Max",
        "lab": "Alibaba",
        "blurb": "Alibaba's next flagship Qwen after the Qwen3 line.",
        "search_terms": ["Qwen4-Max", "Alibaba Qwen 4 release", "Qwen4 Max launch"],
        "release_match": ["qwen4", "qwen 4", "qwen-4"],
    },
    {
        "id": "kimi-k2.8",
        "name": "Kimi K2.8",
        "lab": "Moonshot AI",
        "blurb": "Moonshot AI's next Kimi K2 iteration, extending the K2 agentic/long-context line.",
        "search_terms": ["Kimi K2.8", "Moonshot AI Kimi K2.8 release", "Kimi K2.8 launch"],
        "release_match": ["kimi k2.8", "kimi-k2.8", "k2.8"],
    },
    {
        "id": "gpt-5.7",
        "name": "GPT-5.7",
        "lab": "OpenAI",
        "blurb": "OpenAI's incremental GPT-5.x update bridging toward the GPT-6 flagship.",
        "search_terms": ["GPT-5.7", "OpenAI GPT-5.7 release", "GPT 5.7 launch"],
        "release_match": ["gpt-5.7", "gpt 5.7", "gpt5.7"],
    },
    {
        "id": "gemini-3.5-pro",
        "name": "Gemini 3.5 Pro",
        "lab": "Google DeepMind",
        "blurb": "Google DeepMind's mid-cycle Pro upgrade in the Gemini 3 family ahead of Gemini 4.",
        "search_terms": ["Gemini 3.5 Pro", "Google DeepMind Gemini 3.5 Pro release", "Gemini 3.5 Pro launch"],
        "release_match": ["gemini 3.5 pro", "gemini-3.5-pro", "gemini3.5 pro"],
    },
    {
        "id": "mistral-large-3",
        "name": "Mistral Large 3",
        "lab": "Mistral AI",
        "blurb": "Mistral AI's next flagship dense model after the Mistral Large 2 line.",
        "search_terms": ["Mistral Large 3", "Mistral AI Large 3 release", "Mistral Large 3 launch"],
        "release_match": ["mistral large 3", "mistral-large-3", "mistral large3"],
    },
    {
        "id": "ernie-5",
        "name": "ERNIE 5",
        "lab": "Baidu",
        "blurb": "Baidu's next-generation ERNIE foundation model after the ERNIE 4.x series.",
        "search_terms": ["ERNIE 5", "Baidu ERNIE 5 release", "ERNIE 5.0 launch"],
        "release_match": ["ernie 5", "ernie-5", "ernie5"],
    },
    {
        "id": "minimax-m2.1",
        "name": "MiniMax M2.1",
        "lab": "MiniMax",
        "blurb": "MiniMax's next agentic reasoning model iterating on the MiniMax M2 release.",
        "search_terms": ["MiniMax M2.1", "MiniMax M2.1 release", "MiniMax M2.1 launch"],
        "release_match": ["minimax m2.1", "minimax-m2.1", "m2.1"],
    },
]

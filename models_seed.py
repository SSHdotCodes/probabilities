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
        "id": "llama-5",
        "name": "Llama 5",
        "lab": "Meta",
        "blurb": "Meta's next open-weight Llama generation after Llama 4.",
        "search_terms": ["Llama 5", "Meta Llama 5 release", "Llama 5 launch"],
        "release_match": ["llama 5", "llama-5", "llama5"],
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
]

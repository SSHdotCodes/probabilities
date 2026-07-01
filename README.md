# probabilities

An AI agent that forecasts **when unreleased frontier AI models will be released**,
then grades itself against reality.

Live: https://probabilities.ssh.codes

## How it works

For each tracked upcoming model (GPT-6, Gemini 4, Claude Opus 5, Grok 6, …) the agent:

1. **Gathers signals**
   - **Polymarket** — prediction-market odds on the release (`gamma-api.polymarket.com`).
   - **X / web** — recent leaks, rumours, and official employee posts (DuckDuckGo text search).
   - **Historical cadence** — the lab's recent model adds, from **ai-tracker.ssh.codes**.
2. **Reasons** with `deepseek-v4-pro` (medium reasoning) via the OpenCode Go endpoint
   (key reused from `pro-ai.ssh.codes`) to produce a calibrated **probability distribution
   over release windows** plus a single point-estimate date.
3. **Grades itself** — a background loop watches **ai-tracker**'s `/api/events`; when a model
   actually ships, the prediction is scored (hit if within ±45 days of the point estimate) and
   the site-wide hit rate updates.

The site shows one clickable **block per model**; click it for the full distribution, the
agent's rationale, the Polymarket odds, the X/web snippets, and (once shipped) the verdict.

## Architecture

| File | Role |
|------|------|
| `app.py` | FastAPI app, API routes, two background loops (predict refresh + release check) |
| `agent.py` | Builds the research prompt, calls `deepseek-v4-pro`, parses the forecast JSON |
| `sources.py` | Polymarket / X-web / ai-tracker fetchers (all degrade gracefully) |
| `storage.py` | Atomic JSON store (`db.json`) in a data dir outside the app dir |
| `models_seed.py` | Seed list of anticipated models |
| `config.py` | Env-driven config (no secrets committed) |
| `static/` | Frontend (polls `/api/state` — the Pi router buffers SSE/WS) |

Data lives in `PROB_DATA_DIR` (outside the app dir) so `rasppost release --clear` never wipes it.

## Deploy (Pi)

```sh
# reuse the OpenCode Go key from pro-ai's env, keep data outside the app dir
rasppost release ~/probabilities --name probabilities \
  --cmd ".venv/bin/uvicorn app:app --host 127.0.0.1 --port 8199" \
  --port 8199 --subdomain probabilities --no-start
rasppost exec probabilities -- python3 -m venv .venv
rasppost exec probabilities -- .venv/bin/pip install -r requirements.txt
# env: OPENCODE_GO_API_KEY (from pro-ai), PROB_DATA_DIR, PROB_ADMIN_TOKEN
rasppost start probabilities
```

## API

- `GET /api/state` — everything the frontend renders (models, predictions, scores, log).
- `GET /api/health`
- `POST /api/refresh/{id}` — force a re-forecast (needs `x-admin-token`).
- `POST /api/models` — add a model `{name, lab, blurb?}` (needs `x-admin-token`).

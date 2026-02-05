# AI Ops Assistant

Minimal AI Operations Assistant implementing Planner, Executor and Verifier agents.

## Features ✅
- Planner agent (LLM) that produces a JSON plan of steps and tools
- Executor agent that runs steps and calls tools (GitHub search, Weather)
- Verifier agent (LLM) that validates results and attempts to repair missing outputs
- Local LLM via GPT4All
- FastAPI demo server at `/run`

## Quickstart 🔧
1. Create a Python venv and activate it.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Download a GPT4All model and set `GPT4ALL_MODEL` in a `.env` file or `export`/set environment variables. Example: `orca-mini-3b-gguf2-q4_0.gguf`.
4. Run the API:

```bash
uvicorn main:app --reload
```

5. Example request:

```bash
curl -X POST "http://127.0.0.1:8000/run" -H "Content-Type: application/json" -d '{"task": "Find 2 popular python repos and the weather in London"}'
```

## Notes 💡
- Optionally configure `GITHUB_TOKEN` in `.env` to avoid GitHub rate limits.
- The Verifier may re-run missing steps automatically to produce a complete final answer.

## Project structure
- `agents/` — Planner, Executor, Verifier
- `tools/` — API wrappers for GitHub and Weather
- `llm/` — GPT4All client wrapper
- `main.py` — FastAPI server

## Improvements (future)
- Caching, parallel execution, more robust monitoring and retry policies

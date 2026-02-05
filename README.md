# AI Operations Assistant

Multi-agent AI system that processes natural language tasks, creates execution plans, calls real APIs, and returns structured results.

## Quick Start

1. Create and activate Python virtual environment
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Set up environment variables (see below)
4. Run the server:
```bash
uvicorn main:app --reload
```
5. Access API at: `http://127.0.0.1:8000/docs`

## Environment Variables

Create a `.env` file using `.env.example`.

Required variables:
- **GPT4ALL_MODEL** – Path or filename of the local GPT4All model (default: `orca-mini-3b-gguf2-q4_0.gguf`)
- **GITHUB_TOKEN** – (Optional) GitHub personal access token to avoid rate limits

## Architecture (High Level)

1. User sends a natural language task to the `/run` endpoint
2. **Planner agent** (LLM) converts the task into a structured JSON plan of steps and required tools
3. **Executor agent** executes each step by calling the appropriate tool (GitHub API, Weather API)
4. **Verifier agent** (LLM) validates that all planned steps were completed and results are present
5. If any step result is missing, the Verifier requests re-execution before producing the final answer

## Integrated APIs

- **GitHub REST API** – Used to search public repositories with stars and metadata
- **Open-Meteo Weather API** – Used to fetch live weather information by city name

## Example Prompts

- Find 2 popular Python repositories and the weather in London
- Find 3 popular JavaScript repositories and the weather in Delhi  
- Find trending machine learning repositories and the weather in New York
- Find 2 popular backend repositories and the weather in Bangalore
- Get weather in Tokyo and search for Go repositories

## Usage Examples

### Query Parameter (Swagger UI compatible)
```bash
curl -X POST "http://127.0.0.1:8000/run?task=Find 2 popular python repositories and the weather in London"
```

### JSON Body
```bash
curl -X POST "http://127.0.0.1:8000/run" \
  -H "Content-Type: application/json" \
  -d '{"task": "Find 2 popular python repositories and the weather in London"}'
```

## Known Limitations / Tradeoffs

- The local LLM (GPT4All) may occasionally produce invalid or incomplete JSON plans
- Planning quality depends on the selected local model and its size
- The system does not use memory or conversation history
- Tool execution is currently sequential and not parallel
- Error handling and retries are minimal and intended for demonstration purposes
- Weather API may fail for very small or unknown cities

## Project Structure

- `agents/` — Planner, Executor, and Verifier agents
- `tools/` — API wrappers for GitHub and Weather
- `llm/` — GPT4All client wrapper
- `main.py` — FastAPI server entry point
- `requirements.txt` — Python dependencies
- `.env.example` — Environment variable template

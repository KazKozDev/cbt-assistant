<p align="center">
  <img src="docs/img/rounded-logo.png" alt="CBT Assistant logo" height="200">
</p>

A local CBT-style assistant with a web UI, Ollama, RAG-powered knowledge search, conversational memory, journals, assessments, and SOS practices.

Current release: `1.0.1`

CBT Assistant is designed to run locally: the backend is built with FastAPI, the frontend is served as a static web app, and both model responses and embeddings are handled through a local Ollama server.

![CBT Assistant screenshot](docs/img/screenshot.png)

## What This Is

CBT Assistant brings several workflows together in a single local application:

- chat with an assistant powered by a local LLM;
- semantic RAG search across CBT materials;
- message history and session summaries stored in SQLite;
- thought and sleep journaling;
- self-assessment tools including PHQ-9, GAD-7, and the Rosenberg Self-Esteem Scale;
- SOS tools for breathing, grounding, and quick calming practices;
- TTS playback and browser voice input.

This is not a medical device and not a replacement for a doctor or therapist. It can be useful as a local self-help assistant, but it should not be used for diagnosis or emergency support.

## Key Features

- `RU/EN` interface with assistant reply language switching.
- Standard and streaming chat via `/api/chat` and `/api/chat/stream`.
- In-conversation tool calling for knowledge search, sleep history, test history, activity history, activity creation, breathing practice triggers, and assessment recommendations.
- Local knowledge base in `knowledge_base/*.md` with embeddings powered by Ollama.
- Session memory with background conversation summarization.
- Data stored in SQLite and partially in browser `localStorage`.
- Export flows for reports and user history.
- Web UI built with plain `HTML/CSS/JS`, no heavy frontend framework.

## How It Works

### Request Flow

```text
Browser (frontend)
    |
    v
FastAPI backend (backend/server.py)
    |-- loads the system prompt from config/prompts.yaml
    |-- fetches session history and summary from SQLite
    |-- runs tool calls (knowledge search, activity lookup, etc.)
    |    `-- RAG: embeds the query and searches knowledge_base/ via Ollama embeddings
    `-- sends the full context to Ollama and streams the reply back to the browser
```

1. The user opens the frontend at `http://localhost:8000`.
2. The FastAPI backend serves the API, WebSocket chat, TTS, and static files.
3. Messages and user records are stored in SQLite.
4. When generating a reply, the assistant uses:
   - the system prompt from `config/prompts.yaml`,
   - session history and summary,
   - tool calling,
   - RAG search over the local knowledge base.
5. Ollama is used for:
   - the main LLM;
   - the embedding model for semantic search.

### Main Components

- [backend/server.py](backend/server.py) - FastAPI server and API logic.
- [src/llm/ollama_client.py](src/llm/ollama_client.py) - client for `Ollama /api/chat`.
- [src/rag/knowledge_base.py](src/rag/knowledge_base.py) - knowledge base loading and semantic search.
- [src/utils/db.py](src/utils/db.py) - SQLite storage for sessions, journals, and synced data.
- [src/memory/summarizer.py](src/memory/summarizer.py) - conversation memory and summary logic.
- [frontend/index.html](frontend/index.html) - main UI.

## Technology Stack

- Backend: FastAPI
- Frontend: vanilla HTML/CSS/JS
- LLM: Ollama
- Default model: `qwen3:8b`
- Embeddings: `qwen3-embedding:4b`
- TTS: `edge-tts` / Microsoft Edge voices
- Storage: SQLite + browser `localStorage`
- Tests: `pytest`
- License: MIT

## Quick Start

### Requirements

- Python 3.10+
- [Ollama](https://ollama.com/) installed and running
- Ollama server available at `http://localhost:11434`

> **Windows / Linux:** the macOS `.command` launcher is not available, but the manual steps below work on all platforms.

### Installation

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Prepare Models

```bash
ollama serve
ollama pull qwen3:8b
ollama pull qwen3-embedding:4b
```

### Run

In one terminal:

```bash
ollama serve
```

In another:

```bash
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python backend/server.py
```

Then open:

```text
http://localhost:8000
```

### Quick Launch on macOS

The repo includes a helper script, [start_cbt_assistant.command](start_cbt_assistant.command), which:

- checks that `.venv/bin/python` exists;
- starts the backend in Terminal;
- waits for the healthcheck;
- opens the app in the browser.

## Configuration

Supported environment variables:

```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
```

Model parameters live in [config/model_config.yaml](config/model_config.yaml), and system prompts live in [config/prompts.yaml](config/prompts.yaml).

## Data Storage

### Backend

- SQLite database: `data/cbt_sessions.db`
- It stores:
  - sessions;
  - message history;
  - mood logs;
  - thought records;
  - sleep logs;
  - assessment results;
  - activities;
  - session summaries.

### Browser

Some settings and client-side data are stored in `localStorage`:

| Key | What it holds |
|-----|---------------|
| `sleepLog` | Sleep journal entries (bedtime, wake time, quality) |
| `activities` | User-defined behavioral activation activities |
| `phqHistory` | PHQ-9 depression assessment history |
| `gadHistory` | GAD-7 anxiety assessment history |
| `esteemHistory` | Rosenberg Self-Esteem Scale history |
| `notifSettings` | Notification preferences |
| `ttsSettings` | Text-to-speech voice and speed settings |
| `APP_LANG` | Selected interface language (`ru` or `en`) |

Local runtime data in `data/` is intentionally gitignored so personal session data does not get committed to the repository.

## API Overview

### Chat

- `POST /api/chat`
- `POST /api/chat/stream`
- `WS /ws/chat/{session_id}`

### User Data

- `POST /api/mood`
- `GET /api/mood/{session_id}`
- `POST /api/thoughts`
- `GET /api/thoughts/{session_id}`
- `GET /api/session/{session_id}`
- `POST /api/session/{session_id}/save`

### Sync

- `POST /api/sync/sleep`
- `POST /api/sync/tests`
- `POST /api/sync/activities`

### Knowledge and Insights

- `GET /api/knowledge/search`
- `POST /api/insights`
- `GET /api/health`
- `GET /api/report/{session_id}`
- `POST /api/tts`

## Project Structure

```text
backend/
  server.py                FastAPI backend
frontend/
  index.html               main interface
  css/
  js/
src/
  llm/                     Ollama client
  rag/                     semantic RAG
  memory/                  summary / memory logic
  prompts/                 prompt builder
  utils/                   SQLite and helpers
knowledge_base/            CBT materials for RAG
config/                    model and prompt config
data/                      SQLite database (gitignored)
docs/
  img/                     screenshots and assets
tests/                     pytest suite
```

## Tests

Run:

```bash
pytest
```

The project includes tests for:

- database logic;
- the RAG component;
- prompt logic;
- server endpoints;
- memory logic;
- parts of end-to-end user flows.

## Troubleshooting

**Startup is slow or hangs**  
On first run, embeddings are generated for all files in `knowledge_base/`. This can take a minute or two depending on your hardware. Subsequent starts are much faster.

**`qwen3-embedding:4b` not found**  
The backend will attempt to pull it automatically via Ollama, but it is better to pull it manually before starting:
```bash
ollama pull qwen3-embedding:4b
```

**Port 8000 already in use**  
Another process is already using the port. Stop that process or change the port in `backend/server.py`.

**Ollama connection refused**  
Make sure `ollama serve` is running before starting the backend. Also check that `OLLAMA_BASE_URL` points to the correct address.

**Voice input not working**  
Voice input uses the browser's Web Speech API, which is available in Chromium-based browsers (Chrome, Edge) and Safari. It does not work in Firefox.

**TTS not working**  
This feature requires the `edge-tts` package (included in `requirements.txt`) and a working internet connection for the first request. Also check that the backend is running and reachable.

## Practical Notes

- Some state lives in the browser and some in SQLite, so synchronization is not fully automatic in every scenario.
- A production deployment would require additional work around security, authentication, privacy controls, and deployment hardening.

## Limitations and Safety

- The application is not intended for emergency psychiatric support.
- The assistant can be wrong, hallucinate, or produce incomplete recommendations.
- Assessment results and assistant responses must not be treated as medical advice or diagnosis.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).

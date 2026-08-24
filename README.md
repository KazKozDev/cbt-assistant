# CBT Assistant — Local AI CBT Companion with Ollama

A local AI mental-health assistant for CBT-informed conversations, structured journaling, self-assessments, guided SOS exercises, and private session memory. The browser app runs on FastAPI, SQLite, and local Ollama models; its default chat and retrieval path does not require a hosted LLM API key.

```bash
# macOS 14+
git clone https://github.com/KazKozDev/cbt-assistant.git && cd cbt-assistant && ./start_cbt_assistant.command

# Windows 10 22H2+ (PowerShell or cmd)
git clone https://github.com/KazKozDev/cbt-assistant.git
cd cbt-assistant
start_cbt_assistant.bat
```

<p align="center">
  <a href="start_cbt_assistant.command"><img src="assets/badges/macos.png" alt="macOS" height="36"></a>
  <a href="start_cbt_assistant.bat"><img src="assets/badges/windows.png" alt="Windows" height="36"></a>
  <a href="#manual-installation"><img src="assets/badges/linux.png" alt="Linux" height="36"></a>
</p>

<p align="center">
  <img src="assets/cbt-assistant-demo.gif" alt="CBT Assistant opening SOS breathing support, reframing an anxious thought, and saving it to the Thought Diary" width="900">
</p>

## Quick start

1. Run the platform command above. The launcher creates `.venv`, installs the Python dependencies, prepares Ollama, downloads `ornith-1.5:9b` and `qwen3-embedding:4b`, starts the server on port `8000`, waits for `/api/health`, and opens the browser.
2. Start with the chat or open **SOS** for breathing, grounding, muscle relaxation, or STOP. Each fullscreen practice has a visual scene and optional local ambient sound. After you agree to begin, the assistant can choose the practice, scene, and a 1–10 minute timer.
3. Switch between English and Russian in **Settings**. Later launches reuse the environment and downloaded models.

> [!IMPORTANT]
> CBT Assistant is a self-help and journaling tool, not a therapist, medical device, crisis service, or substitute for professional care. Its responses and assessment results can be wrong. If you may be in immediate danger or at risk of harming yourself or someone else, contact local emergency services or a qualified crisis service now.

## What it does

- **Local CBT chat** retrieves relevant passages from the bundled knowledge base before every answer.
- **Thought Diary** records a situation, automatic thought, emotion, intensity, possible distortion, and balanced response.
- **Mood and sleep logs** keep scores, notes, sleep times, interruptions, duration, and quality.
- **Activities and assessments** track planned actions plus PHQ-9, GAD-7, and Rosenberg Self-Esteem Scale results.
- **SOS portals** guide paced breathing, 5-4-3-2-1 grounding, progressive muscle relaxation, and STOP with visual scenes, sound, and optional countdowns.
- **Reports** download a text summary or create a printable PDF report in the browser.

These records provide future conversation context instead of leaving each chat isolated. Some data is synchronized to SQLite; interface-side state also uses browser `localStorage`.

## Local chat, memory, and tools

The default chat model is [`ornith-1.5:9b`](https://ollama.com/library/ornith-1.5:9b). Each request combines retrieved CBT passages, the latest 20 messages, synchronized journal records, a structured personal profile, and a rolling summary refreshed after every 15 new messages.

The browser stores its `SESSION_ID` in `localStorage`, so the same profile, transcript, and summary return after a reload or application restart. A different browser profile or cleared browser storage creates a different session identity. Inspect or erase the derived profile and summary with:

```text
GET    /api/memory/{session_id}
DELETE /api/memory/{session_id}
```

The assistant can open an agreed SOS practice, suggest a self-assessment, add an agreed action to the planner, and read recent sleep, assessment, or activity data. Retrieved passages and profile memory are inserted into the prompt as delimited data, not instructions.

## Local CBT retrieval

At startup, `src/rag/knowledge_base.py` splits the bundled Markdown knowledge base by heading hierarchy and requests embeddings from `qwen3-embedding:4b`. REST, streaming, and WebSocket chat share this retrieval path; the model cannot skip it.

```text
GET /api/knowledge/search?q=sleep&top_k=3
GET /api/knowledge/status
```

Results include stable chunk and document IDs, source paths, section hierarchy, similarity scores, index version, and a local trace ID. The browser displays selected sources, and the model is instructed to cite clinical claims as `[KB:chunk_id]`.

The default threshold is `0.35`. When no passage clears it, the assistant may continue supportive conversation but must not invent a specific CBT protocol or clinical justification. Retrieval grounding does not make generated advice clinically correct for an individual user.

## How it works

```text
Browser UI
   ↓
FastAPI REST + WebSocket API
   ↓
Prompt assembly ← CBT knowledge search
   ↓                     ↓
Ollama chat          Ollama embeddings
   ↓                     ↓
Response             Markdown knowledge base
   └──────── SQLite + browser localStorage
```

The backend persists messages and structured records in SQLite. RAG restores a matching cached NumPy index or rebuilds it after the knowledge content changes. Failed first builds remain unavailable; failed rebuilds keep the previous complete in-memory index in degraded mode.

See [Architecture](docs/ARCHITECTURE.md) for the request path, storage model, RAG contract, configuration, and important files.

<a id="manual-installation"></a>

## Manual installation

Install [Python 3.10+](https://www.python.org/) and [Ollama](https://ollama.com/), then run:

```bash
git clone https://github.com/KazKozDev/cbt-assistant.git
cd cbt-assistant
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
ollama pull ornith-1.5:9b
ollama pull qwen3-embedding:4b
python backend/server.py
```

Open `http://localhost:8000`. If Ollama is installed but not running, start `ollama serve` in another terminal first. Linux currently uses this manual path; the repository has no Dockerfile or automatic Linux launcher.

## Requirements and configuration

- macOS 14+ for `start_cbt_assistant.command`, or Windows 10 22H2+ for the `.bat` and PowerShell launchers.
- Python 3.10+, Ollama, a modern browser, and enough memory and disk space for the selected models.
- Internet access on the first run for Python dependencies and Ollama models. Optional browser media and speech features can also use external services.

| Setting | Default | Override |
|---|---|---|
| App | `http://localhost:8000` | Server binds to `0.0.0.0:8000` |
| Ollama | `http://localhost:11434` | `OLLAMA_BASE_URL` |
| Chat model | `ornith-1.5:9b` | `OLLAMA_MODEL`, `CBT_ASSISTANT_CHAT_MODEL`, or Settings |
| Embeddings | `qwen3-embedding:4b` | `RAG_EMBED_MODEL` |
| RAG threshold | `0.35` | `RAG_SCORE_THRESHOLD` |
| Data | `data/cbt_sessions.db` | Local SQLite file |

Generation defaults are 1,024 maximum tokens, temperature `0.7`, and top-p `0.9`. See [Architecture](docs/ARCHITECTURE.md#configuration) for the complete configuration contract.

## Privacy, safety, and limitations

Chat generation, embeddings, the bundled knowledge base, and SQLite persistence are local by default, but the application is local-first rather than strictly offline. Fonts, frontend libraries, text-to-speech, browser speech recognition, YouTube media, and printable reports may contact external services.

The server has permissive CORS, no authentication, no encryption layer, and no multi-user isolation. Do not expose port `8000` to the public internet or an untrusted network. Personal memory is session-scoped but not encrypted; deleting derived memory does not delete the transcript.

Model quality and latency depend on local hardware and the selected models. Assessments are self-help aids, not diagnoses. The application does not monitor emergencies, contact a clinician, dispatch help, or automatically escalate a crisis.

Read the full [Privacy, safety, and limitations](docs/PRIVACY_AND_SAFETY.md) before entering sensitive information.

## Development

Run the deterministic suite without the live memory integration:

```bash
python -m pytest -q --ignore=tests/test_real_memory.py
```

The current suite passes 51 tests. Live memory, RAG evaluation, baseline metrics, and manual interaction checks are documented in [Development and evaluation](docs/DEVELOPMENT.md). Read [CONTRIBUTING.md](CONTRIBUTING.md) before a substantial pull request and [SECURITY.md](SECURITY.md) for sensitive reports.

## License

CBT Assistant is free and open-source software licensed under the [MIT License](LICENSE).

<p align="center">
  <a href="https://github.com/KazKozDev/cbt-assistant/actions/workflows/tests.yml"><img alt="CI" src="https://github.com/KazKozDev/cbt-assistant/actions/workflows/tests.yml/badge.svg"></a>
  <a href="https://www.python.org/"><img alt="Python 3.10+" src="https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&amp;logoColor=white"></a>
  <a href="https://github.com/KazKozDev/cbt-assistant/blob/main/LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-blue.svg"></a>
</p>

<p align="center">
  <a href="https://github.com/KazKozDev/cbt-assistant/issues">Issues</a> ·
  <a href="CONTRIBUTING.md">Contributing</a> ·
  <a href="SECURITY.md">Security</a> ·
  <a href="https://www.linkedin.com/in/kazkozdev/">LinkedIn</a>
</p>

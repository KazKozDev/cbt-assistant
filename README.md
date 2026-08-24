# CBT Assistant — Local AI CBT Companion with Ollama

A local AI mental health assistant for CBT-informed conversations, thought journaling, mood and sleep tracking, self-assessments, guided SOS exercises, and private session memory. The browser app runs on FastAPI, SQLite, and local Ollama models; English is the default interface language, with Russian available in Settings.

```bash
# macOS 14+
git clone https://github.com/KazKozDev/cbt-assistant.git && cd cbt-assistant && ./start_cbt_assistant.command

# Windows 10 22H2+ (PowerShell or cmd, after cloning)
git clone https://github.com/KazKozDev/cbt-assistant.git
cd cbt-assistant
start_cbt_assistant.bat
```

<p align="center">
  <a href="start_cbt_assistant.command"><img src="assets/badges/macos.png" alt="macOS" height="36"></a>
  <a href="start_cbt_assistant.bat"><img src="assets/badges/windows.png" alt="Windows" height="36"></a>
  <a href="#manual-installation"><img src="assets/badges/linux.png" alt="Linux" height="36"></a>
</p>

<p align="center">Launchers after clone — run <code>.command</code> on macOS or double-click <code>.bat</code> on Windows. Linux uses the manual setup below.</p>

<p align="center">
  <img src="assets/cbt-assistant-demo.gif" alt="CBT Assistant opening SOS breathing support, reframing an anxious thought, and saving it to the Thought Diary" width="900">
</p>

---

## Quick start

1. Run the command above. The launcher creates `.venv`, installs the Python dependencies, installs and starts Ollama when needed, downloads `qwen3:8b` and `qwen3-embedding:4b`, releases port `8000`, starts CBT Assistant, waits for `/api/health`, and opens `http://localhost:8000` in your browser.

2. Start with the chat or open **SOS** for a guided breathing, grounding, muscle-relaxation, or STOP exercise. The interface starts in English; switch to Russian in **Settings** if you prefer.

3. Save useful context in the **Thought Diary**, mood tracker, sleep journal, assessments, or activity planner. CBT Assistant can use the synchronized records and session summary when preparing later responses.

The first launch takes longer because the Python environment and Ollama models must be downloaded. Later launches reuse them.

> [!IMPORTANT]
> CBT Assistant is a self-help and journaling tool, not a therapist, medical device, crisis service, or substitute for professional care. Its responses and assessment results can be wrong. If you may be in immediate danger or at risk of harming yourself or someone else, contact local emergency services or a qualified crisis service now.

## Run a private CBT chatbot with a local LLM

The chat uses `qwen3:8b` through Ollama by default. Before each answer, the backend retrieves relevant passages from the bundled CBT knowledge base and combines them with recent conversation history, synchronized journal data, and the saved session summary.

```text
Message → CBT knowledge search → Local Ollama response → Saved session context
```

The assistant can also call application tools when they are relevant to the conversation: open a breathing exercise, suggest a PHQ-9 or GAD-7 self-assessment, add an agreed action to the activity planner, or read recent sleep, assessment, and activity data.

The default chat and retrieval path does not require a hosted LLM API key. Optional speech and media features can still contact external services; see **Privacy and safety** below.

## Keep a CBT thought diary, mood log, and sleep journal

CBT Assistant keeps structured self-reflection beside the conversation instead of treating every interaction as disposable chat.

- **Thought Diary** records the situation, automatic thought, emotion, intensity, possible distortion, and a balanced response.
- **Mood tracker** saves a score and note for later review in the dashboard and calendar.
- **Sleep Journal** stores bedtime, wake time, interruptions, duration, quality, and notes.
- **Activity planner** keeps concrete actions and completion state.
- **Self-assessments** save PHQ-9, GAD-7, and Rosenberg Self-Esteem Scale results.
- **Reports** download a text summary or create a printable PDF report in the browser.

```text
Situation → Automatic thought → Emotion → Balanced response → Future context
```

Some records are synchronized to SQLite. Browser-only interface state also uses `localStorage`, so keep the same browser profile if you want that local history to remain available.

## Use guided SOS exercises for immediate self-regulation

Open **SOS** to choose paced breathing, 5-4-3-2-1 grounding, progressive muscle relaxation, or the STOP exercise. A personal crisis-plan note can also be saved in the browser.

These are short self-regulation aids. The application does not monitor emergencies or contact a clinician, emergency service, or trusted person on your behalf.

## Search a local CBT knowledge base with RAG

The bundled Markdown knowledge base covers clinical CBT guidance, anxiety protocols, insomnia protocols, and psychological skills. At startup, `src/rag/knowledge_base.py` divides these files into sections and requests embeddings from the local `qwen3-embedding:4b` model.

For every chat message, semantic search selects relevant passages before the prompt is sent to the chat model. The same index is available through the API:

```text
GET /api/knowledge/search?q=sleep&top_k=3
```

The knowledge base grounds retrieval, but it does not guarantee that a generated answer is clinically correct or suitable for an individual user.

## How it works

The browser talks to a FastAPI server running on your computer.<br>
**RAG** retrieves relevant CBT passages with local Ollama embeddings.<br>
**Chat** combines those passages with recent history and structured records.<br>
**Memory** summarizes longer sessions and saves the result in SQLite.<br>
**Tools** connect the conversation to assessments, activities, and guided exercises.

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

<details>
<summary>Technical architecture</summary>

### Request path

1. **Startup** — FastAPI initializes `data/cbt_sessions.db`, reads `knowledge_base/*.md`, and embeds the knowledge chunks through Ollama.
2. **Retrieve** — a chat request runs semantic search and selects the most relevant local CBT passages.
3. **Assemble** — the prompt combines system instructions, retrieved passages, recent messages, synchronized records, and any rolling session summary.
4. **Generate** — `src/llm/ollama_client.py` sends the request to the configured Ollama model. REST, streaming, or WebSocket responses return to the browser.
5. **Persist** — messages and structured records are written to SQLite. After the configured threshold, `src/memory/summarizer.py` updates the session summary.

### Storage

- `data/cbt_sessions.db` stores sessions, messages, mood logs, thought records, sleep logs, assessment results, activities, and summaries.
- Browser `localStorage` stores the session identifier and interface-side mood, sleep, activity, assessment, language, reminder, voice, and crisis-plan settings.
- The default chat, embeddings, knowledge base, and SQLite path run on the machine hosting the application.

### Important files

- `backend/server.py` — FastAPI application, REST/WebSocket endpoints, tools, reports, TTS, and frontend hosting.
- `src/llm/ollama_client.py` — Ollama chat and streaming client.
- `src/rag/knowledge_base.py` — Markdown loading, embeddings, and semantic retrieval.
- `src/memory/summarizer.py` — rolling conversation summaries.
- `src/utils/db.py` — SQLite schema and persistence.
- `config/prompts.yaml` — assistant behavior, safety instructions, and tool guidance.
- `config/model_config.yaml` — default models and generation settings.
- `frontend/` — English and Russian browser interface.
- `knowledge_base/` — local CBT material used for retrieval.
- `tests/` — database, prompt, RAG, memory, API, and interaction checks.

</details>

<details>
<summary>Configuration</summary>

| Setting | Default | What it means |
|---|---|---|
| App address | `http://localhost:8000` | Browser interface and API; the server binds to `0.0.0.0:8000` |
| Ollama address | `http://localhost:11434` | Override with `OLLAMA_BASE_URL` |
| Chat model | `qwen3:8b` | Override with `OLLAMA_MODEL` for manual starts or `CBT_ASSISTANT_CHAT_MODEL` for the launchers |
| Embedding model | `qwen3-embedding:4b` | Configured in `config/model_config.yaml` |
| Maximum generated tokens | `1024` | `num_predict` sent to Ollama |
| Temperature | `0.7` | Chat sampling value |
| Top-p | `0.9` | Chat sampling value |
| Interface language | English | Russian is available in Settings |
| Data file | `data/cbt_sessions.db` | Local SQLite application storage |

Example manual model override:

```bash
OLLAMA_BASE_URL=http://localhost:11434 \
OLLAMA_MODEL=qwen3:8b \
python backend/server.py
```

The embedding model is not controlled by an environment variable. Change `config/model_config.yaml` if you intentionally replace it.

</details>

<details>
<summary>Requirements</summary>

- **macOS 14 or newer** for `start_cbt_assistant.command`.
- **Windows 10 22H2 or newer** for `start_cbt_assistant.bat` and `start_cbt_assistant_windows.ps1`.
- **Python 3.10+** and **Ollama** for manual installation on Linux or another supported environment.
- Enough memory and disk space for `qwen3:8b` and `qwen3-embedding:4b`, or compatible models you configure yourself.
- Internet access on the first run to download Python dependencies and Ollama models.
- A modern browser. Some optional browser features continue to require network access.

The automatic launchers install a local Python 3.12 environment through `uv` when needed, install the project dependencies, prepare Ollama, stop the current listener on port `8000`, and open the application after its health check succeeds.

</details>

<details>
<summary>Privacy and safety</summary>

- Chat generation, embeddings, the bundled knowledge base, and SQLite persistence use the local machine and local Ollama server by default.
- The frontend loads Google Fonts, Lucide icons, and Chart.js from public CDNs.
- Text-to-speech uses Microsoft Edge TTS and sends the selected text to that service.
- Browser speech recognition may use a remote service depending on the browser and operating system.
- Video thumbnails and playback use YouTube domains.
- Printable PDF reports load Chart.js from a CDN when the report window is created.
- The server binds to `0.0.0.0:8000` and enables permissive CORS. Do not expose it to the public internet or an untrusted network without authentication and restrictive network controls.
- The application has no user accounts, encryption layer, clinician review, emergency dispatch, or automatic crisis escalation.
- PHQ-9, GAD-7, and Rosenberg results are self-assessment aids, not diagnoses.

Review the code and network behavior before entering sensitive information. A strictly offline deployment requires replacing or disabling external fonts, scripts, speech, and video integrations.

</details>

<details>
<summary>Limitations</summary>

- Generated mental health guidance can be incomplete, inappropriate, or incorrect. Prompt safeguards and local retrieval do not make the model clinically reliable.
- CBT Assistant does not diagnose conditions, prescribe treatment, monitor emergencies, or replace a qualified professional.
- This is a single-user local application with no authentication or multi-user isolation.
- Privacy is local-first, not fully offline, because optional speech, media, fonts, and CDN assets can contact external services.
- Model quality and latency depend on the selected Ollama models and local hardware.
- The embedding model must be available before the knowledge index and chat become usable.
- The repository does not currently include a Dockerfile or automatic Linux launcher.

</details>

<a id="manual-installation"></a>

<details>
<summary>Manual installation and development setup</summary>

### Manual installation

Install [Python 3.10+](https://www.python.org/) and [Ollama](https://ollama.com/), then run:

```bash
git clone https://github.com/KazKozDev/cbt-assistant.git
cd cbt-assistant
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
ollama pull qwen3:8b
ollama pull qwen3-embedding:4b
python backend/server.py
```

Open `http://localhost:8000` after the server starts. Start `ollama serve` in another terminal first if Ollama is installed but not already running.

The platform launchers automate the same preparation:

- macOS: run `./start_cbt_assistant.command`
- Windows: double-click `start_cbt_assistant.bat`
- Linux: use the manual commands above

### Development setup

Run the deterministic tests without a live model response:

```bash
python -m pytest -q --ignore=tests/test_real_memory.py
```

These tests cover SQLite behavior, prompt construction, mocked retrieval and summarization, API endpoints, and tool execution. Run the live memory integration separately when Ollama and the selected model are available:

```bash
python -m pytest tests/test_real_memory.py -s
```

`tests/test_real_interaction.py` is a manual end-to-end script for an already running application. Passing the software checks does not validate the clinical quality of generated responses.

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a substantial pull request. Report security-sensitive problems as described in [SECURITY.md](SECURITY.md).

</details>

## License

CBT Assistant is free and open-source software licensed under the [MIT License](LICENSE).

<br><br>

<p align="center">
  <a href="https://github.com/KazKozDev/cbt-assistant/blob/main/LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-blue.svg"></a>
  <a href="https://github.com/KazKozDev/cbt-assistant/actions/workflows/tests.yml"><img alt="CI" src="https://github.com/KazKozDev/cbt-assistant/actions/workflows/tests.yml/badge.svg"></a>
  <a href="https://www.python.org/"><img alt="Python 3.10+" src="https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&amp;logoColor=white"></a>
</p>

<p align="center">
  <a href="https://github.com/KazKozDev/cbt-assistant/issues">Issues</a> ·
  <a href="https://github.com/KazKozDev/cbt-assistant/blob/main/CONTRIBUTING.md">Contributing</a> ·
  <a href="https://github.com/KazKozDev/cbt-assistant/blob/main/SECURITY.md">Security</a> ·
  <a href="https://github.com/KazKozDev/cbt-assistant/blob/main/LICENSE">LICENSE</a> ·
  <a href="https://www.linkedin.com/in/kazkozdev/">LinkedIn</a>
</p>

# CBT Assistant — Local AI Mental Health Chatbot & CBT Journal with Ollama

Local-first CBT assistant: structured thought records, mood and sleep tracking, self-assessments, and SOS exercises — with chat grounded in a local CBT knowledge base via RAG and persistent session memory.

<a id="installation"></a>

```bash
# macOS 14+
git clone https://github.com/KazKozDev/cbt-assistant.git && cd cbt-assistant && ./start_cbt_assistant.command
```
```bash
# Windows 10 22H2+ (PowerShell or cmd)
git clone https://github.com/KazKozDev/cbt-assistant.git
cd cbt-assistant
start_cbt_assistant.bat
```
```bash
# Linux
git clone https://github.com/KazKozDev/cbt-assistant.git && cd cbt-assistant
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
ollama pull ornith-1.5:9b
ollama pull qwen3-embedding:4b
python backend/server.py
```

<p align="center">
  <img src="assets/cbt-assistant-demo.gif" alt="CBT Assistant opening SOS breathing support, reframing an anxious thought, and saving it to the Thought Diary" width="900">
</p>

## Quick start: run the local AI CBT chatbot

1. Run the command for your platform above. The macOS and Windows launchers create `.venv`, install the Python dependencies, prepare Ollama, download `ornith-1.5:9b` and `qwen3-embedding:4b`, start the server on port `8000`, wait for `/api/health`, and open the browser. On Linux, open `http://localhost:8000` after the server starts; if Ollama is installed but not running, start `ollama serve` in another terminal first.
2. Start with the chat or open **SOS** for breathing, grounding, muscle relaxation, or STOP. Each fullscreen practice has a visual scene and optional local ambient sound. After you agree to begin, the assistant can choose the practice, scene, and a 1–10 minute timer.
3. Switch between English and Russian in **Settings**. Later launches reuse the environment and downloaded models.

> [!IMPORTANT]
> CBT Assistant is a self-help and journaling tool, not a therapist, medical device, crisis service, or substitute for professional care. Its responses and assessment results can be wrong. If you may be in immediate danger or at risk of harming yourself or someone else, contact local emergency services or a qualified crisis service now.

## CBT journal app, mood tracker, self-assessments, and SOS exercises

- **Local CBT chat** retrieves relevant passages from the bundled knowledge base before every answer.
- **Thought Diary** records a situation, automatic thought, emotion, intensity, possible distortion, and balanced response.
- **Mood and sleep logs** keep scores, notes, sleep times, interruptions, duration, and quality.
- **Activities and assessments** track planned actions plus PHQ-9, GAD-7, and Rosenberg Self-Esteem Scale results.
- **SOS portals** guide paced breathing, 5-4-3-2-1 grounding, progressive muscle relaxation, and STOP with visual scenes, sound, and optional countdowns.
- **Reports** download a text summary or create a printable PDF report in the browser.

These records provide future conversation context instead of leaving each chat isolated. Some data is synchronized to SQLite; interface-side state also uses browser `localStorage`.

## Private AI mental health chatbot with local memory

The default chat model is [`ornith-1.5:9b`](https://ollama.com/library/ornith-1.5:9b). Each request combines retrieved CBT passages, the latest 20 messages, synchronized journal records, a structured personal profile, and a rolling summary refreshed after every 15 new messages.

The browser stores its `SESSION_ID` in `localStorage`, so the same profile, transcript, and summary return after a reload or application restart. A different browser profile or cleared browser storage creates a different session identity. Inspect or erase the derived profile and summary with:

```text
GET    /api/memory/{session_id}
DELETE /api/memory/{session_id}
```

The assistant can open an agreed SOS practice, suggest a self-assessment, add an agreed action to the planner, and read recent sleep, assessment, or activity data. Retrieved passages and profile memory are inserted into the prompt as delimited data, not instructions.

## Local CBT knowledge base with RAG and Ollama

At startup, `src/rag/knowledge_base.py` splits the bundled Markdown knowledge base by heading hierarchy and requests embeddings from `qwen3-embedding:4b`. REST, streaming, and WebSocket chat share this retrieval path; the model cannot skip it.

The RAG implementation covers the full local retrieval path: hierarchical chunking, embedding generation, similarity gating, cached index restoration, traceable source metadata, and degraded-mode handling when an index rebuild fails.

```text
GET /api/knowledge/search?q=sleep&top_k=3
GET /api/knowledge/status
```

Results include stable chunk and document IDs, source paths, section hierarchy, similarity scores, index version, and a local trace ID. The browser displays selected sources, and the model is instructed to cite clinical claims as `[KB:chunk_id]`.

The default threshold is `0.35`. When no passage clears it, the assistant may continue supportive conversation but must not invent a specific CBT protocol or clinical justification. Retrieval grounding does not make generated advice clinically correct for an individual user.

## How the local AI assistant works

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

See Architecture for the request path, storage model, RAG contract, configuration, and important files.

## Limitations

- CBT Assistant is local-first, not fully offline: text-to-speech, browser speech recognition, Google Fonts, CDN scripts, YouTube media, and printable reports may contact external services.
- The server binds to `0.0.0.0:8000`, enables permissive CORS, and has no authentication, encryption layer, or multi-user isolation. Do not expose it to the public internet or an untrusted network.
- Chat quality, response time, and memory use depend on the selected Ollama models and local hardware. Chat is unavailable until the embedding model has built or restored the CBT knowledge index.
- Generated responses and self-assessments can be wrong. The application does not diagnose, monitor emergencies, contact a clinician, dispatch help, or replace professional care.
- Linux requires manual installation; Docker and an automatic Linux launcher are not included.

<br>
<br>

<p align="center">
  <a href="start_cbt_assistant.command"><img src="assets/badges/macos.png" alt="macOS" height="28"></a>
  <a href="start_cbt_assistant.bat"><img src="assets/badges/windows.png" alt="Windows" height="28"></a>
  <a href="#installation"><img src="assets/badges/linux.png" alt="Linux" height="28"></a>
  <a href="https://github.com/KazKozDev/cbt-assistant/actions/workflows/tests.yml"><img alt="CI" src="https://github.com/KazKozDev/cbt-assistant/actions/workflows/tests.yml/badge.svg" height="28"></a>
  <a href="https://www.python.org/"><img alt="Python 3.10+" src="https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&amp;logoColor=white" height="28"></a>
  <a href="https://github.com/KazKozDev/cbt-assistant/blob/main/LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-blue.svg" height="28"></a>
</p>

<p align="center">
  <a href="https://github.com/KazKozDev/cbt-assistant/issues">Issues</a> ·
  <a href="docs/ARCHITECTURE.md">Architecture</a> ·
  <a href="docs/PRIVACY_AND_SAFETY.md">Privacy &amp; Safety</a> ·
  <a href="LICENSE">LICENSE</a> ·
  <a href="https://www.linkedin.com/in/kazkozdev/">LinkedIn</a>
</p>

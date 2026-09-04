# CBT Assistant — local-first CBT journal and AI mental health chatbot on Ollama

An offline, self-hosted cognitive behavioral therapy (CBT) app: structured thought records, mood and sleep tracking, clinical self-assessments, and guided SOS exercises — plus a chat assistant grounded in a built-in CBT knowledge base via RAG. No cloud and no account; the model runs on your own machine through Ollama.

<p align="center">
  <img src="assets/CBT3.gif" alt="CBT Assistant opening SOS breathing support, reframing an anxious thought, and saving it to the Thought Diary" width="900">
</p>

<a id="installation"></a>

## Quick start

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

The launcher sets up the Python environment, prepares Ollama, downloads `qwen3.5:9b`, starts the server on port 8000, and opens your browser; later launches reuse the same setup. On Linux, make sure `ollama serve` is running, run the steps manually, and open http://localhost:8000. English and Russian are switchable in Settings.

> [!IMPORTANT]
> CBT Assistant is a self-help and journaling tool — not a therapist, medical device, or crisis service. Its knowledge base follows evidence-based CBT protocols, but AI responses and self-assessments can still be wrong. If you may be in immediate danger or at risk of harming yourself or someone else, contact local emergency services or a crisis line now.

## CBT journal, mood tracker, self-assessments, and SOS exercises

- **Thought Diary** — situations, automatic thoughts, emotions and intensities, cognitive distortions, rational responses.
- **Mood & Sleep Logs** — daily scores and notes, sleep duration, interruptions, quality.
- **Self-Assessments** — PHQ-9, GAD-7, Rosenberg Self-Esteem, and Burnout, with score interpretation.
- **Dashboard & Calendar** — mood and sleep trends over time, and a month view unifying every daily entry.
- **SOS Portals** — fullscreen paced breathing, 5-4-3-2-1 grounding, progressive muscle relaxation, and STOP, with scenes, sound, and countdowns.
- **Reports** — text summaries or printable PDF, generated in the browser.

## Private AI mental health chatbot with local memory

- Warm, non-judgmental dialogue with `qwen3.5:9b` running locally — nothing leaves your machine.
- Grounded, not improvised: every clinical claim comes from the bundled CBT library via FastEmbed RAG and is cited as `[KB:chunk_id]`. Below the similarity threshold (0.46) the assistant gives general support instead of inventing protocols.
- Writes your records for you: ask it to log a thought record or a sleep entry, launch an agreed SOS portal, or schedule a planned activity.
- Remembers you across restarts: a personal profile and rolling summary persist in SQLite, so chats aren't isolated.
- Voice mode — speech recognition and neural text-to-speech in English and Russian.

## How the local CBT assistant works

```text
Browser UI
   ↓
FastAPI REST + WebSocket API
   ↓
Prompt assembly ← CBT knowledge search
   ↓                     ↓
Ollama chat          FastEmbed (CPU / ONNX)
   ↓                     ↓
Response             Markdown knowledge base
   └──────── SQLite + browser localStorage
```

At startup the Markdown CBT library is split by heading hierarchy and embedded locally with FastEmbed (`paraphrase-multilingual-mpnet-base-v2`); the model cannot bypass this retrieval path. Messages and structured records live in SQLite, while interface logs and screening state also use browser `localStorage`.

```text
GET    /api/knowledge/search?q=sleep&top_k=3
GET    /api/knowledge/status
GET    /api/memory/{session_id}
DELETE /api/memory/{session_id}
```

Index caching, rebuilds, and degraded-mode behaviour are described in [ARCHITECTURE](docs/ARCHITECTURE.md).

## Limitations

- **Network** — text-to-speech, speech recognition, Google Fonts, CDN scripts, and YouTube media need internet access.
- **Security** — binds to `0.0.0.0:8000` with permissive CORS and no auth or encryption. Keep it off public and untrusted networks.
- **Performance** — chat quality, latency, and memory use depend on your hardware and model; chat is unavailable until the embedding index is built.
- **Platform** — no Docker image and no Linux launcher; Linux setup is manual.

<br>
<br>

<p align="center">
  <img src="assets/cbt-assistant-art-flow.gif" alt="CBT Assistant Art Flow" width="34%">&nbsp;&nbsp;
  <img src="assets/cbt-assistant-art-mind.png" alt="CBT Assistant Art Mind" width="64%">
</p>

<br>
<br>

<p align="center">
  <a href="start_cbt_assistant.command"><img alt="macOS" src="https://img.shields.io/badge/macOS-2D6A4F.svg?logo=apple&amp;logoColor=white" height="28"></a>
  <a href="start_cbt_assistant.bat"><img alt="Windows" src="https://img.shields.io/badge/Windows-0078D4.svg?logo=windows&amp;logoColor=white" height="28"></a>
  <a href="#installation"><img alt="Linux" src="https://img.shields.io/badge/Linux-FCC624.svg?logo=linux&amp;logoColor=black" height="28"></a>
  <a href="https://github.com/KazKozDev/cbt-assistant/actions/workflows/tests.yml"><img alt="CI" src="https://github.com/KazKozDev/cbt-assistant/actions/workflows/tests.yml/badge.svg" height="28"></a>
  <a href="https://www.python.org/"><img alt="Python 3.10+" src="https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&amp;logoColor=white" height="28"></a>
  <a href="https://github.com/KazKozDev/cbt-assistant/blob/main/LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-blue.svg" height="28"></a>
</p>

<p align="center">
  <a href="https://github.com/KazKozDev/cbt-assistant/issues">Issues</a> ·
  <a href="docs/ARCHITECTURE.md">ARCHITECTURE</a> ·
  <a href="docs/PRIVACY_AND_SAFETY.md">Privacy &amp; Safety</a> ·
  <a href="LICENSE">LICENSE</a> ·
  <a href="https://www.linkedin.com/in/kazkozdev/">LinkedIn</a>
</p>

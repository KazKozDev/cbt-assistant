# Privacy, safety, and limitations

CBT Assistant is a self-help and journaling application. It is not a therapist, medical device, crisis service, diagnostic tool, or substitute for professional care.

## Local and external processing

The following paths use the machine hosting the application and its configured local Ollama server by default:

- chat generation;
- embeddings and knowledge-base retrieval;
- the bundled Markdown knowledge base;
- SQLite persistence;
- bundled SOS images and ambient audio.

The application is local-first rather than strictly offline. These optional or frontend resources can contact external services:

- Google Fonts;
- Lucide icons and Chart.js loaded from public CDNs;
- Microsoft Edge TTS, which receives selected speech text;
- browser speech recognition, depending on the browser and operating system;
- YouTube thumbnails and video playback;
- Chart.js loaded when a printable PDF report window is created.

A strictly offline deployment requires replacing or disabling those external fonts, scripts, speech, and video integrations.

## Network and data boundaries

- The FastAPI server binds to `0.0.0.0:8000` and enables permissive CORS.
- The application has no user accounts, authentication, encryption layer, or multi-user isolation.
- Do not expose the server to the public internet or an untrusted network without authentication and restrictive network controls.
- Personal profile memory is local and session-scoped but not encrypted.
- Browser `localStorage` holds the session identity and some interface-side records and settings.
- Clearing browser storage, changing browser profiles, or manually changing the session ID starts a separate memory context even if older SQLite rows remain on disk.
- `DELETE /api/memory/{session_id}` removes the derived profile and summary. Deleting the transcript is a separate operation.
- Local RAG traces can contain sensitive query text and should not be shared casually.

Review the code and network behavior before entering sensitive information.

## Clinical and emergency limitations

- Generated mental-health guidance can be incomplete, inappropriate, or incorrect. Prompt safeguards and local retrieval do not make the model clinically reliable.
- PHQ-9, GAD-7, and Rosenberg results are self-assessment aids, not diagnoses.
- CBT Assistant does not diagnose conditions, prescribe treatment, monitor emergencies, or replace a qualified professional.
- It has no clinician review, emergency dispatch, trusted-person contact, or automatic crisis escalation.
- SOS exercises are short self-regulation aids, not emergency monitoring or treatment.
- If you may be in immediate danger or at risk of harming yourself or someone else, contact local emergency services or a qualified crisis service now.

## Technical limitations

- Model quality and latency depend on the selected Ollama models and local hardware.
- The embedding model must be available before the knowledge index and chat become usable.
- This is a single-user local application.
- The repository does not currently include a Dockerfile or automatic Linux launcher.

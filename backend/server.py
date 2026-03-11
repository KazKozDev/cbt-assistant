"""
CBT Depression AI Assistant — Backend Server
=============================================
FastAPI server integrating Modular genAI components.
"""

import os
import json
from pathlib import Path
from contextlib import asynccontextmanager
import yaml
import sys

# Ensure src can be imported
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from fastapi.responses import FileResponse, PlainTextResponse, Response  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from src.llm.ollama_client import OllamaClient, ContentCleaner  # noqa: E402
from src.utils.db import SQLiteSessionManager  # noqa: E402
from src.rag.knowledge_base import SemanticRAG  # noqa: E402
from src.prompts.templates import PromptManager  # noqa: E402
from src.memory.summarizer import MemorySummarizer  # noqa: E402
from src import __version__  # noqa: E402

# ─── Configuration ───────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Load configs
CONFIG_DIR = Path(__file__).parent.parent / "config"
with open(CONFIG_DIR / "model_config.yaml", "r", encoding="utf-8") as f:
    model_config = yaml.safe_load(f)["models"]

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", model_config["qwen"]["model_name"])
EMBED_MODEL = model_config["embeddings"]["model_name"]
LLM_OPTIONS = {
    "temperature": model_config["qwen"]["temperature"],
    "top_p": model_config["qwen"]["top_p"],
    "num_predict": model_config["qwen"]["max_tokens"],
}

KNOWLEDGE_BASE_DIR = Path(__file__).parent.parent / "knowledge_base"
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

# ─── Component Initialization ─────────────────────────────────────
llm_client = OllamaClient(OLLAMA_BASE_URL, OLLAMA_MODEL)
kb = SemanticRAG(KNOWLEDGE_BASE_DIR, OLLAMA_BASE_URL, EMBED_MODEL)
sessions = SQLiteSessionManager(DATA_DIR / "cbt_sessions.db")
prompt_manager = PromptManager(CONFIG_DIR / "prompts.yaml")
summarizer = MemorySummarizer(sessions, llm_client)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load and embed knowledge base
    await kb.load_and_embed()
    yield


# ─── FastAPI App ─────────────────────────────────────────────────
app = FastAPI(title="CBT Depression AI Assistant", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── REST Endpoints ─────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    language: str = "ru"


class MoodRequest(BaseModel):
    score: int
    note: str = ""
    session_id: str = "default"


class TTSRequest(BaseModel):
    text: str
    language: str = "ru"
    voice: str | None = None


class ThoughtRecordRequest(BaseModel):
    session_id: str = "default"
    situation: str
    thought: str
    emotion: str
    intensity: int
    distortion: str
    rational_response: str


class SyncRequest(BaseModel):
    session_id: str = "default"
    items: list[dict]


def get_user_data_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": "get_user_sleep_history",
                "description": "Получить последние записи дневника сна пользователя.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "Количество дней для получения истории сна (по умолчанию 14).",
                        }
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_user_test_results",
                "description": "Получить последние результаты психологических тестов (PHQ-9 депрессия, GAD-7 тревога).",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_user_activities",
                "description": "Получить данные о планировании активности пользователя (что сделано, а что нет).",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "add_user_activity",
                "description": "Добавить новую активность или задачу в планировщик пользователя (например, после рекомендации).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "activity_text": {
                            "type": "string",
                            "description": "Текст активности, которую нужно добавить. Максимум 50 символов.",
                        }
                    },
                    "required": ["activity_text"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "start_breathing",
                "description": "Запустить дыхательную разминку/упражнение на клиенте, если пользователь жалуется на панику, тревогу или сильный стресс.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "recommend_test",
                "description": "Порекомендовать и открыть диалог прохождения психологического теста (PHQ-9 при признаках депрессии или GAD-7 при симптомах тревоги).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "test_type": {
                            "type": "string",
                            "enum": ["PHQ-9", "GAD-7"],
                            "description": "Тип теста для прохождения.",
                        }
                    },
                    "required": ["test_type"],
                },
            },
        },
    ]


def build_language_instruction(language: str) -> str:
    if language == "en":
        return (
            "IMPORTANT: Reply in English only. "
            "Even if the user writes in Russian, keep your response in English "
            "because the interface language is English."
        )
    return (
        "ВАЖНО: Отвечай только на русском языке. "
        "Даже если пользователь вставляет английские слова, основной ответ должен быть на русском."
    )


TTS_VOICES = {
    "ru": {
        "ru-RU-SvetlanaNeural",
        "ru-RU-DmitryNeural",
    },
    "en": {
        "en-US-JennyNeural",
        "en-US-GuyNeural",
    },
}


def get_tts_voice(language: str, voice: str | None = None) -> str:
    lang = "en" if language == "en" else "ru"
    if voice and voice in TTS_VOICES[lang]:
        return voice
    if lang == "en":
        return "en-US-JennyNeural"
    return "ru-RU-SvetlanaNeural"


@app.post("/api/chat")
async def chat(req: ChatRequest):
    session = sessions.get_or_create(req.session_id)
    system_prompt = prompt_manager.build_system_prompt(
        [], session.get("mood_log"), session.get("thought_records"), session.get("summary")
    )
    system_prompt = f"{system_prompt}\n\n{build_language_instruction(req.language)}"

    messages = [{"role": "system", "content": system_prompt}]
    for msg in sessions.get_history(req.session_id):
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": req.message})

    available_tools = [kb.get_tool_schema()] + get_user_data_tools()

    try:
        while True:
            resp = await llm_client.chat(
                messages, options=LLM_OPTIONS, tools=available_tools
            )
            tool_calls = resp.get("tool_calls", [])
            content = resp.get("content", "")

            if tool_calls:
                messages.append(
                    {"role": "assistant", "content": content, "tool_calls": tool_calls}
                )

                for tc in tool_calls:
                    fn_name = tc.get("function", {}).get("name")
                    args = tc.get("function", {}).get("arguments", {})

                    if fn_name == "search_cbt_knowledge":
                        query = args.get("query", "")
                        results = await kb.search(query, top_k=3)
                        tool_res_str = f"Found {len(results)} results:\n"
                        for r in results:
                            tool_res_str += (
                                f"- [{r['chunk']['title']}] {r['chunk']['content']}\n"
                            )

                        messages.append(
                            {"role": "tool", "content": tool_res_str, "name": fn_name}
                        )
                    elif fn_name == "get_user_sleep_history":
                        days = args.get("days", 14)
                        sleep_logs = sessions.get_sleep_logs(req.session_id, limit=days)
                        messages.append(
                            {
                                "role": "tool",
                                "content": json.dumps(sleep_logs, ensure_ascii=False),
                                "name": fn_name,
                            }
                        )
                    elif fn_name == "get_user_test_results":
                        tests = sessions.get_tests(req.session_id)
                        messages.append(
                            {
                                "role": "tool",
                                "content": json.dumps(tests, ensure_ascii=False),
                                "name": fn_name,
                            }
                        )
                    elif fn_name == "get_user_activities":
                        acts = sessions.get_activities(req.session_id, limit=30)
                        messages.append(
                            {
                                "role": "tool",
                                "content": json.dumps(acts, ensure_ascii=False),
                                "name": fn_name,
                            }
                        )
                    elif fn_name == "add_user_activity":
                        # For now, simulate success but tell the assistant it needs to ask the UI to do it
                        act_text = args.get("activity_text", "")
                        messages.append(
                            {
                                "role": "tool",
                                "content": f"Successfully added activity: {act_text}. Note: This will be sent as a client command in the final response.",
                                "name": fn_name,
                            }
                        )
                    elif fn_name == "start_breathing":
                        messages.append(
                            {
                                "role": "tool",
                                "content": "Successfully triggered the breathing exercise on the user's interface.",
                                "name": fn_name,
                            }
                        )
                    elif fn_name == "recommend_test":
                        test_type = args.get("test_type", "PHQ-9")
                        messages.append(
                            {
                                "role": "tool",
                                "content": f"Successfully recommended the {test_type} test. The interface will open the test modal.",
                                "name": fn_name,
                            }
                        )
                    else:
                        messages.append(
                            {
                                "role": "tool",
                                "content": f"Error: Unknown tool {fn_name}",
                                "name": fn_name,
                            }
                        )
            else:
                sessions.add_message(req.session_id, "user", req.message)
                sessions.add_message(req.session_id, "assistant", content)
                # Check if there were any tool calls in the history of this request
                client_events = []
                for msg in messages:
                    if msg.get("role") == "assistant" and "tool_calls" in msg:
                        for tc in msg["tool_calls"]:
                            fc_name = tc.get("function", {}).get("name")
                            if fc_name == "add_user_activity":
                                client_events.append({
                                    "type": "add_activity",
                                    "text": tc.get("function", {}).get("arguments", {}).get("activity_text", "")
                                })
                            elif fc_name == "start_breathing":
                                client_events.append({
                                    "type": "start_breathing"
                                })
                            elif fc_name == "recommend_test":
                                client_events.append({
                                    "type": "open_test",
                                    "test_type": tc.get("function", {}).get("arguments", {}).get("test_type", "PHQ-9")
                                })

                return {
                    "response": content,
                    "context_used": [],
                    "session_id": req.session_id,
                    "client_events": client_events
                }

    except Exception as e:
        raise HTTPException(500, f"Error communicating with model: {str(e)}")


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    from fastapi.responses import StreamingResponse

    session = sessions.get_or_create(req.session_id)
    system_prompt = prompt_manager.build_system_prompt(
        [], session.get("mood_log"), session.get("thought_records")
    )
    system_prompt = f"{system_prompt}\n\n{build_language_instruction(req.language)}"

    messages = [{"role": "system", "content": system_prompt}]
    for msg in sessions.get_history(req.session_id):
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": req.message})

    # Available tools
    available_tools = [kb.get_tool_schema()] + get_user_data_tools()

    async def generate():
        nonlocal messages

        while True:
            full_response = ""
            tool_calls = []

            try:
                # 1. Ask model
                async for chunk in llm_client.chat_stream(
                    messages, options=LLM_OPTIONS, tools=available_tools
                ):
                    msg = chunk.get("message", {})

                    # Ollama streams tool calls too
                    if "tool_calls" in msg and msg["tool_calls"]:
                        # Merge tool calls from stream (often sent in one piece anyway, but let's be safe)
                        tool_calls = msg["tool_calls"]

                    token = msg.get("content", "")
                    if token:
                        full_response += token
                        # Only yield to frontend if it's not an empty tool trigger
                        if token.strip():
                            yield f"data: {json.dumps({'token': token})}\n\n"

                    if chunk.get("done"):
                        # If there were tool calls, we don't end the stream yet!
                        if tool_calls:
                            # 2. Add assistant's tool call intent to history
                            messages.append(
                                {
                                    "role": "assistant",
                                    "content": full_response,
                                    "tool_calls": tool_calls,
                                }
                            )

                            # 3. Execute tools
                            for tc in tool_calls:
                                fn_name = tc.get("function", {}).get("name")
                                args = tc.get("function", {}).get("arguments", {})

                                if fn_name == "search_cbt_knowledge":
                                    query = args.get("query", "")
                                    print(f"🔧 Model called tool: {fn_name}('{query}')")
                                    # Yield a special event to frontend showing tool action
                                    yield f"data: {json.dumps({'tool_call': fn_name, 'query': query})}\n\n"

                                    # Search KB
                                    results = await kb.search(query, top_k=3)
                                    tool_res_str = f"Found {len(results)} results:\n"
                                    for r in results:
                                        tool_res_str += f"- [{r['chunk']['title']}] {r['chunk']['content']}\n"

                                    messages.append(
                                        {
                                            "role": "tool",
                                            "content": tool_res_str,
                                            "name": fn_name,
                                        }
                                    )
                                elif fn_name == "get_user_sleep_history":
                                    days = args.get("days", 14)
                                    print(f"🔧 Model called tool: {fn_name}('{days}')")
                                    yield f"data: {json.dumps({'tool_call': fn_name, 'query': f'Сон за {days} дней'})}\n\n"
                                    sleep_logs = sessions.get_sleep_logs(
                                        req.session_id, limit=days
                                    )
                                    messages.append(
                                        {
                                            "role": "tool",
                                            "content": json.dumps(
                                                sleep_logs, ensure_ascii=False
                                            ),
                                            "name": fn_name,
                                        }
                                    )
                                elif fn_name == "get_user_test_results":
                                    print(f"🔧 Model called tool: {fn_name}()")
                                    yield f"data: {json.dumps({'tool_call': fn_name, 'query': 'Результаты тестов'})}\n\n"
                                    tests = sessions.get_tests(req.session_id)
                                    messages.append(
                                        {
                                            "role": "tool",
                                            "content": json.dumps(
                                                tests, ensure_ascii=False
                                            ),
                                            "name": fn_name,
                                        }
                                    )
                                elif fn_name == "get_user_activities":
                                    print(f"🔧 Model called tool: {fn_name}()")
                                    yield f"data: {json.dumps({'tool_call': fn_name, 'query': 'Активности'})}\n\n"
                                    acts = sessions.get_activities(
                                        req.session_id, limit=30
                                    )
                                    messages.append(
                                        {
                                            "role": "tool",
                                            "content": json.dumps(
                                                acts, ensure_ascii=False
                                            ),
                                            "name": fn_name,
                                        }
                                    )
                                else:
                                    messages.append(
                                        {
                                            "role": "tool",
                                            "content": f"Error: Unknown tool {fn_name}",
                                            "name": fn_name,
                                        }
                                    )

                            # Break out of loop to run llm_client.chat_stream AGAIN with tool results
                            break

                        else:
                            # Standard completion done
                            clean = ContentCleaner.strip_think_tags(full_response)
                            sessions.add_message(req.session_id, "user", req.message)
                            sessions.add_message(req.session_id, "assistant", clean)
                            await summarizer.maybe_summarize(req.session_id)
                            yield f"data: {json.dumps({'done': True, 'full_response': clean})}\n\n"
                            return  # Exit generator completely
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                return

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/api/mood")
async def log_mood(req: MoodRequest):
    sessions.add_mood(req.session_id, req.score, req.note)
    return {
        "status": "ok",
        "mood_log": sessions.get_or_create(req.session_id)["mood_log"],
    }


@app.post("/api/tts")
async def synthesize_tts(req: TTSRequest):
    text = (req.text or "").strip()
    if not text:
        raise HTTPException(400, "Text is required")

    safe_text = " ".join(text.split())[:1500]

    try:
        import edge_tts
    except ImportError as exc:
        raise HTTPException(500, "Microsoft TTS backend is not installed") from exc

    audio_chunks = []
    try:
        communicate = edge_tts.Communicate(
            text=safe_text,
            voice=get_tts_voice(req.language, req.voice),
        )
        async for chunk in communicate.stream():
            if chunk.get("type") == "audio":
                audio_chunks.append(chunk.get("data", b""))
    except Exception as exc:
        raise HTTPException(500, f"TTS synthesis failed: {str(exc)}") from exc

    audio_data = b"".join(audio_chunks)
    if not audio_data:
        raise HTTPException(500, "TTS synthesis returned no audio")

    return Response(
        content=audio_data,
        media_type="audio/mpeg",
        headers={"Cache-Control": "no-store"},
    )


@app.get("/api/mood/{session_id}")
async def get_mood(session_id: str):
    session = sessions.get_or_create(session_id)
    return {"mood_log": session["mood_log"]}


@app.post("/api/thoughts")
async def add_thought_record(req: ThoughtRecordRequest):
    sessions.add_thought_record(
        req.session_id,
        req.situation,
        req.thought,
        req.emotion,
        req.intensity,
        req.distortion,
        req.rational_response,
    )
    return {
        "status": "ok",
        "thought_records": sessions.get_or_create(req.session_id)["thought_records"],
    }


@app.get("/api/thoughts/{session_id}")
async def get_thought_records(session_id: str):
    session = sessions.get_or_create(session_id)
    return {"thought_records": session.get("thought_records", [])}


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    return sessions.get_or_create(session_id)


@app.post("/api/session/{session_id}/save")
async def save_session(session_id: str):
    sessions.save_session(session_id)
    return {"status": "saved"}


# DATA SYNC ENDPOINTS


@app.post("/api/sync/sleep")
async def sync_sleep(req: SyncRequest):
    sessions.sync_sleep_logs(req.session_id, req.items)
    return {"status": "ok"}


@app.post("/api/sync/tests")
async def sync_tests(req: SyncRequest):
    sessions.sync_test_results(req.session_id, req.items)
    return {"status": "ok"}


@app.post("/api/sync/activities")
async def sync_activities(req: SyncRequest):
    sessions.sync_activities(req.session_id, req.items)
    return {"status": "ok"}


# ─── INSIGHTS ENDPOINT ───────────────────────────────────────────


class InsightsRequest(BaseModel):
    session_id: str = "default"
    mood_log: list[dict] = []
    sleep_log: list[dict] = []
    activities: list[dict] = []
    phq_history: list[dict] = []
    gad_history: list[dict] = []
    thought_records: list[dict] = []


def _build_insights_prompt(req: InsightsRequest) -> str:
    """Build a data summary for the LLM, only including sections that have real data."""
    sections = []

    # IMPORTANT: we only include a section if data actually exists.
    # Absence of data = not tracked, NOT a negative signal.

    if req.mood_log:
        recent = sorted(req.mood_log, key=lambda x: x.get("date", ""), reverse=True)[:14]
        scores = [e.get("score") for e in recent if e.get("score") is not None]
        if scores:
            avg = round(sum(scores) / len(scores), 1)
            sections.append(
                f"НАСТРОЕНИЕ (из записей дневника настроения — {len(scores)} оценок за последние дни):\n"
                f"  Средняя оценка: {avg}/10. Оценки: {scores[:10]}"
            )

    if req.sleep_log:
        recent_sleep = sorted(req.sleep_log, key=lambda x: x.get("isoDate", ""), reverse=True)[:7]
        sleep_info = []
        for s in recent_sleep:
            hours = s.get("hours") or s.get("duration")
            quality = s.get("quality")
            if hours or quality:
                sleep_info.append(f"часов сна: {hours}, качество: {quality}")
        if sleep_info:
            sections.append(
                f"СОН (записи дневника сна — {len(sleep_info)} дней):\n  " +
                "\n  ".join(sleep_info)
            )

    if req.activities:
        done = [a for a in req.activities if a.get("done")]
        pending = [a for a in req.activities if not a.get("done")]
        sections.append(
            f"АКТИВНОСТИ (планировщик): выполнено {len(done)}, не выполнено/в плане {len(pending)}"
        )

    if req.phq_history:
        recent_phq = sorted(req.phq_history, key=lambda x: x.get("date", ""), reverse=True)[:3]
        phq_info = [f"PHQ-9: {e.get('score')} ({e.get('date', '')[:10]})" for e in recent_phq]
        sections.append("ТЕСТЫ PHQ-9 (депрессия):\n  " + "\n  ".join(phq_info))

    if req.gad_history:
        recent_gad = sorted(req.gad_history, key=lambda x: x.get("date", ""), reverse=True)[:3]
        gad_info = [f"GAD-7: {e.get('score')} ({e.get('date', '')[:10]})" for e in recent_gad]
        sections.append("ТЕСТЫ GAD-7 (тревога):\n  " + "\n  ".join(gad_info))

    if req.thought_records:
        emotions = [t.get("emotion", "") for t in req.thought_records if t.get("emotion")]
        distortions = [t.get("distortion", "") for t in req.thought_records if t.get("distortion")]
        sections.append(
            f"КПТ-ДНЕВНИК МЫСЛЕЙ ({len(req.thought_records)} записей):\n"
            f"  Упомянутые эмоции: {', '.join(emotions[:8])}\n"
            f"  Когнитивные искажения: {', '.join(set(distortions[:6]))}"
        )

    if not sections:
        return None  # No data at all

    data_block = "\n\n".join(sections)

    return f"""Ты — заботливый ассистент, который помогает человеку лучше понять себя.
Ниже — данные из его личного дневника за последнее время. Это только то, что он сам заполнял.

ВАЖНЕЙШЕЕ ПРАВИЛО: Отсутствие данных в каком-либо разделе означает только то, что человек не заполнял этот раздел — это НЕ значит, что он плохо спал, не двигался или был в плохом настроении. Никогда не делай выводов об отсутствующих данных.

Данные:
{data_block}

Задача: Напиши 2–3 мягких наблюдения на русском языке, основанных ТОЛЬКО на том, что есть в данных выше.
Правила:
- Используй слова: «кажется», «возможно», «похоже», «интересно что», «заметно», «судя по записям»
- НЕ ставь диагнозов, НЕ делай однозначных выводов
- Можно задать мягкий вопрос в конце наблюдения
- Каждое наблюдение — отдельный абзац, 1–2 предложения
- Тон: тёплый, не как врач, а как внимательный друг
- Ответ только на русском, без заголовков, без списков с тире — просто абзацы

Если данных слишком мало для осмысленных наблюдений — напиши одну мягкую фразу об этом."""


@app.post("/api/insights")
async def generate_insights(req: InsightsRequest):
    """Generate soft AI observations based only on available user data."""
    prompt = _build_insights_prompt(req)

    if prompt is None:
        return {
            "insights": "Пока данных для наблюдений немного — чем больше ты заполняешь дневник, тем точнее я смогу замечать паттерны.",
            "has_data": False
        }

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "Напиши наблюдения."}
    ]

    try:
        resp = await llm_client.chat(
            messages,
            options={
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 800,
            }
        )
        text = resp.get("content", "").strip()
        if not text:
            text = "Пока сложно заметить что-то определённое — продолжай вести записи."
        return {"insights": text, "has_data": True}
    except Exception as e:
        return {"insights": "Не удалось получить наблюдения прямо сейчас.", "has_data": False, "error": str(e)}


@app.get("/api/knowledge/search")
async def search_knowledge(q: str, top_k: int = 3):
    results = await kb.search(q, top_k)
    return {
        "query": q,
        "results": [
            {
                "title": r["chunk"]["title"],
                "score": round(r["score"], 2),
                "preview": r["chunk"]["content"][:300],
            }
            for r in results
        ],
    }


@app.get("/api/health")
async def health():
    import httpx

    ollama_ok = False
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            ollama_ok = r.status_code == 200
    except Exception:
        pass

    return {
        "status": "ok",
        "version": __version__,
        "ollama_connected": ollama_ok,
        "ollama_url": OLLAMA_BASE_URL,
        "model": OLLAMA_MODEL,
        "knowledge_chunks": len(kb.chunks),
    }

@app.get("/api/report/{session_id}")
async def get_session_report(session_id: str):
    import datetime
    
    session = sessions.get_or_create(session_id)
    summary = session.get("summary", "Нет данных о сессии.")
    mood_log = session.get("mood_log", [])
    thought_records = session.get("thought_records", [])
    
    report_lines = []
    report_lines.append("КЛИНИЧЕСКАЯ ВЫПИСКА ПАЦИЕНТА")
    report_lines.append("=" * 40)
    report_lines.append(f"Дата выписки: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report_lines.append(f"Идентификатор сессии: {session_id}")
    report_lines.append("")
    report_lines.append("--- РЕЗЮМЕ ТЕРАПИИ (ДОЛГОСРОЧНАЯ ПАМЯТЬ) ---")
    report_lines.append(summary if summary else "Резюме еще не сформировано.")
    report_lines.append("")
    
    report_lines.append("--- ПОСЛЕДНИЕ ОЦЕНКИ НАСТРОЕНИЯ ---")
    if not mood_log:
        report_lines.append("Нет данных.")
    for m in mood_log[-10:]:
        report_lines.append(f"{m.get('timestamp')[:19]}: {m.get('score')}/10 - {m.get('note', '')}")
    report_lines.append("")
    
    report_lines.append("--- ДНЕВНИК МЫСЛЕЙ (ПОСЛЕДНИЕ ЗАПИСИ) ---")
    if not thought_records:
        report_lines.append("Нет данных.")
    for tr in thought_records[-5:]:
        report_lines.append(f"[{tr.get('timestamp')[:19]}]")
        report_lines.append(f"Ситуация: {tr.get('situation', '')}")
        report_lines.append(f"Мысль: {tr.get('thought', '')}")
        report_lines.append(f"Эмоция: {tr.get('emotion', '')} ({tr.get('intensity', '')}/10)")
        report_lines.append(f"Искажения: {tr.get('distortion', '')}")
        report_lines.append(f"Рациональный ответ: {tr.get('rational_response', '')}")
        report_lines.append("-" * 20)
    
    # Also grab recent psychological tests
    tests = sessions.get_tests(session_id)
    report_lines.append("")
    report_lines.append("--- ПСИХОЛОГИЧЕСКИЕ ТЕСТЫ ---")
    if not tests:
        report_lines.append("Нет данных.")
    for t in tests[:5]:
        report_lines.append(f"[{t.get('iso_date')[:10]}] {t.get('test_name')}: {t.get('score')} баллов ({t.get('level')})")
        
    report_content = "\n".join(report_lines)
    
    return PlainTextResponse(
        report_content, 
        headers={"Content-Disposition": f"attachment; filename=cbt_report_{session_id}.txt"}
    )



# ─── WebSocket ───────────────────────────────────────────────────


@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "message":
                user_msg = data["content"]

                context = await kb.search(user_msg, top_k=3)
                session = sessions.get_or_create(session_id)
                system_prompt = prompt_manager.build_system_prompt(
                    context, session.get("mood_log"), session.get("thought_records"), session.get("summary")
                )

                sessions.add_message(session_id, "user", user_msg)
                
                # Fetch recent history
                history = sessions.get_history(session_id)
                messages = [{"role": "system", "content": system_prompt}]
                for msg in history:
                    messages.append({"role": msg["role"], "content": msg["content"]})
                # The user message was already added to history, so no need to append again here.

                full_response = ""
                assistant_reply = ""
                try:
                    async for chunk in llm_client.chat_stream(
                        messages, options=LLM_OPTIONS
                    ):
                        token = chunk.get("message", {}).get("content", "")
                        if token:
                            full_response += token
                            assistant_reply += token # Accumulate for saving
                            await websocket.send_json(
                                {"type": "token", "content": token}
                            )
                        if chunk.get("done"):
                            clean = ContentCleaner.strip_think_tags(full_response)
                            # Save assistant response
                            sessions.add_message(session_id, "assistant", assistant_reply)
                            
                            # Trigger background memory summarization
                            await summarizer.maybe_summarize(session_id)
                            await websocket.send_json(
                                {"type": "done", "content": clean}
                            )
                except Exception as e:
                    await websocket.send_json({"type": "error", "content": str(e)})

            elif data.get("type") == "mood":
                sessions.add_mood(session_id, data["score"], data.get("note", ""))
                await websocket.send_json(
                    {
                        "type": "mood_logged",
                        "mood_log": sessions.get_or_create(session_id)["mood_log"],
                    }
                )
    except WebSocketDisconnect:
        sessions.save_session(session_id)


# Serve static frontend at the very end to catch all non-API paths
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

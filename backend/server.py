"""
CBT Depression AI Assistant — Backend Server
=============================================
FastAPI server integrating Modular genAI components.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager
import yaml
import sys

# Ensure src can be imported
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from fastapi.responses import PlainTextResponse, Response  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from src.llm.ollama_client import OllamaClient, ContentCleaner  # noqa: E402
from src.utils.db import SQLiteSessionManager  # noqa: E402
from src.rag.knowledge_base import SemanticRAG  # noqa: E402
from src.prompts.templates import PromptManager  # noqa: E402
from src.memory.summarizer import MemorySummarizer  # noqa: E402
from src.memory.profile import (  # noqa: E402
    extract_profile_updates,
    has_profile_updates,
    merge_profiles,
)
from src import __version__  # noqa: E402

# ─── Configuration ───────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

# Load configs
CONFIG_DIR = Path(__file__).parent.parent / "config"
with open(CONFIG_DIR / "model_config.yaml", "r", encoding="utf-8") as f:
    model_config = yaml.safe_load(f)["models"]

DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", model_config["qwen"]["model_name"])
EMBED_CONFIG = model_config.get("embeddings", {})
EMBED_MODEL = os.getenv(
    "RAG_EMBED_MODEL",
    EMBED_CONFIG.get(
        "model_name", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    ),
)
DEFAULT_SCORE_THRESHOLD = float(EMBED_CONFIG.get("score_threshold", 0.45))
SCORE_THRESHOLD = float(os.getenv("RAG_SCORE_THRESHOLD", str(DEFAULT_SCORE_THRESHOLD)))
LLM_OPTIONS = {
    "temperature": model_config["qwen"]["temperature"],
    "top_p": model_config["qwen"]["top_p"],
    "num_predict": model_config["qwen"]["max_tokens"],
}

KNOWLEDGE_BASE_DIR = Path(__file__).parent.parent / "knowledge_base"
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
MODEL_SETTINGS_PATH = DATA_DIR / "model_settings.json"


def load_selected_model() -> str:
    """Restore the model selected in the UI, falling back to startup config."""
    try:
        saved = json.loads(MODEL_SETTINGS_PATH.read_text(encoding="utf-8"))
        model = saved.get("chat_model")
        if isinstance(model, str) and model.strip():
            return model.strip()
    except (OSError, ValueError, TypeError):
        pass
    return DEFAULT_OLLAMA_MODEL


def persist_selected_model(model: str) -> None:
    """Persist a UI model choice without modifying repository configuration."""
    temporary_path = MODEL_SETTINGS_PATH.with_suffix(".tmp")
    temporary_path.write_text(
        json.dumps({"chat_model": model}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(MODEL_SETTINGS_PATH)


OLLAMA_MODEL = load_selected_model()

# ─── Component Initialization ─────────────────────────────────────
llm_client = OllamaClient(OLLAMA_BASE_URL, OLLAMA_MODEL)
kb = SemanticRAG(
    KNOWLEDGE_BASE_DIR,
    ollama_url=OLLAMA_BASE_URL,
    embed_model=EMBED_MODEL,
    cache_path=DATA_DIR / "rag_index.npz",
    trace_path=DATA_DIR / "rag_traces.jsonl",
    score_threshold=SCORE_THRESHOLD,
)
sessions = SQLiteSessionManager(DATA_DIR / "cbt_sessions.db")
prompt_manager = PromptManager(CONFIG_DIR / "prompts.yaml")
summarizer = MemorySummarizer(sessions, llm_client)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await kb.load_and_embed()
    try:
        yield
    finally:
        await summarizer.close()


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
    language: str = "en"


class MoodRequest(BaseModel):
    score: int
    note: str = ""
    session_id: str = "default"


class TTSRequest(BaseModel):
    text: str
    language: str = "en"
    voice: str | None = None


class ModelSelectionRequest(BaseModel):
    model: str


class ThoughtRecordRequest(BaseModel):
    session_id: str = "default"
    situation: str
    thought: str
    emotion: str
    intensity: int
    distortion: str
    rational_response: str


class ThoughtRecordUpdateRequest(BaseModel):
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


class ResourceRequest(BaseModel):
    session_id: str = "default"
    title: str
    category: str = "joy"
    description: str = ""


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
                "name": "start_sos_exercise",
                "description": (
                    "Сразу открыть на клиенте подходящую полноэкранную SOS-практику "
                    "с визуальной сценой, фоновым звуком и таймером. Используй только "
                    "когда пользователь согласен начать практику или прямо просит её запустить."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "technique": {
                            "type": "string",
                            "enum": ["breathing", "grounding", "pmr", "stop"],
                            "description": "Практика: дыхание, заземление 5-4-3-2-1, мышечная релаксация или СТОП.",
                        },
                        "scene": {
                            "type": "string",
                            "enum": ["air", "field", "sea", "night_forest"],
                            "description": "Атмосфера портала: воздух, поле, море или ночной лес.",
                        },
                        "duration": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10,
                            "description": "Продолжительность состояния в минутах, от 1 до 10.",
                        },
                    },
                    "required": ["technique", "scene", "duration"],
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
        {
            "type": "function",
            "function": {
                "name": "add_thought_record",
                "description": (
                    "Добавить новую запись в Дневник мыслей (Thought Diary) пользователя, "
                    "когда разобрали автоматическую мысль, эмоцию, искажение и сформулировали "
                    "рациональный ответ, либо по прямой просьбе пользователя."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "situation": {
                            "type": "string",
                            "description": "Ситуация или триггер, вызвавший переживание (например, 'Разговор с коллегами').",
                        },
                        "thought": {
                            "type": "string",
                            "description": "Автоматическая негативная мысль (например, 'Я точно всё испорчу').",
                        },
                        "emotion": {
                            "type": "string",
                            "description": "Основная эмоция (например, 'Тревога', 'Грусть', 'Стыд').",
                        },
                        "intensity": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10,
                            "description": "Интенсивность эмоции от 1 до 10 (по умолчанию 7).",
                        },
                        "distortion": {
                            "type": "string",
                            "description": "Когнитивное искажение (например, 'Катастрофизация', 'Черно-белое мышление', 'Чтение мыслей').",
                        },
                        "rational_response": {
                            "type": "string",
                            "description": "Рациональный ответ / адаптивная поддерживающая мысль.",
                        },
                    },
                    "required": [
                        "situation",
                        "thought",
                        "emotion",
                        "rational_response",
                    ],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "add_sleep_diary_record",
                "description": (
                    "Отдельно от Дневника мыслей добавить запись именно в Дневник сна "
                    "пользователя: время отхода ко сну, подъем, качество, пробуждения и "
                    "заметки. Используй этот инструмент, а не add_thought_record, когда "
                    "пользователь просит записать сон или сообщает данные для дневника сна."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "bed": {
                            "type": "string",
                            "description": "Время отхода ко сну в формате ЧЧ:ММ (например, '23:30').",
                        },
                        "wake": {
                            "type": "string",
                            "description": "Время подъема в формате ЧЧ:ММ (например, '07:30').",
                        },
                        "quality": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10,
                            "description": "Субъективное качество сна от 1 до 10 (по умолчанию 7).",
                        },
                        "awakenings": {
                            "type": "integer",
                            "minimum": 0,
                            "description": "Количество ночных пробуждений (по умолчанию 0).",
                        },
                        "notes": {
                            "type": "string",
                            "description": "Краткие заметки о сне или утреннем самочувствии.",
                        },
                        "date": {
                            "type": "string",
                            "description": "Дата сна в формате ГГГГ-ММ-ДД (опционально, по умолчанию текущий день).",
                        },
                    },
                    "required": ["bed", "wake"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_user_resources",
                "description": (
                    "Получить персональный список ресурсов/якорей пользователя (то, что радует, "
                    "успокаивает, дает силы и помогает в моменты апатии, стресса или грусти). "
                    "Используй, когда пользователю плохо, грустно, не хватает сил, чтобы мягко "
                    "напомнить о его проверенных источниках ресурса."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": [
                                "all",
                                "joy",
                                "body",
                                "people",
                                "places",
                                "creativity",
                            ],
                            "description": "Опциональный фильтр по категории ресурсов (по умолчанию 'all').",
                        }
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "add_user_resource",
                "description": (
                    "Добавить новый пункт в Точки опоры пользователя (любимое занятие, "
                    "успокаивающий ритуал, место, контакт или маленькую радость), когда в диалоге "
                    "обнаружили, что именно это помогает пользователю или приносит облегчение."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Краткое название ресурса (например, 'Зеленый чай с жасмином', 'Прогулка в парке', 'Звонок другу').",
                        },
                        "category": {
                            "type": "string",
                            "enum": ["joy", "body", "people", "places", "creativity"],
                            "description": "Категория: joy (радости), body (тело/сенсорика), people (люди), places (места), creativity (творчество/отвлечение). По умолчанию 'joy'.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Дополнительные детали или почему это помогает (опционально).",
                        },
                    },
                    "required": ["title"],
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


def serialize_rag_context(results: list[dict], trace: dict) -> list[dict]:
    return [
        {
            "chunk_id": item["chunk"]["chunk_id"],
            "document_id": item["chunk"]["document_id"],
            "source": item["chunk"]["source"],
            "title": item["chunk"]["title"],
            "section_path": item["chunk"]["section_path"],
            "score": round(item["score"], 4),
            "index_version": trace["index_version"],
        }
        for item in results
    ]


def requires_grounded_clinical_answer(message: str) -> bool:
    normalized = message.casefold()
    clinical_terms = (
        "тревог",
        "депресс",
        "бессон",
        "сон",
        "паник",
        "эмоц",
        "псих",
        "самоповреж",
        "суицид",
        "терап",
        "кпт",
        "cbt",
        "anxiety",
        "depression",
        "insomnia",
        "sleep",
        "panic",
        "mental health",
        "self-harm",
        "suicid",
    )
    advice_terms = (
        "что делать",
        "как ",
        "техника",
        "упражнен",
        "протокол",
        "совет",
        "леч",
        "поможет",
        "should i",
        "what should",
        "how ",
        "exercise",
        "protocol",
        "treat",
        "therapy",
        "help with",
    )
    return any(term in normalized for term in clinical_terms) and any(
        term in normalized for term in advice_terms
    )


def grounded_abstention(language: str) -> str:
    if language == "en":
        return (
            "I couldn't find sufficiently relevant support for a specific answer in the local "
            "CBT knowledge base, so I won't invent a technique or clinical recommendation. "
            "You can rephrase the question, or discuss it with a qualified professional."
        )
    return (
        "В локальной базе КПТ не нашлось достаточно релевантной опоры для конкретного ответа, "
        "поэтому я не буду придумывать технику или клиническую рекомендацию. Можно уточнить "
        "вопрос или обсудить его с квалифицированным специалистом."
    )


def ensure_rag_citations(content: str, context_used: list[dict], language: str) -> str:
    """Guarantee that a grounded answer exposes only citations from retrieved context."""
    if not context_used or any(
        f"[KB:{item['chunk_id']}]" in content for item in context_used
    ):
        return content
    label = "Retrieved evidence" if language == "en" else "Найденная опора"
    citations = ", ".join(
        f"[KB:{item['chunk_id']}] ({item['source']})" for item in context_used
    )
    return f"{content.rstrip()}\n\n{label}: {citations}"


async def prepare_chat_messages(
    message: str, session_id: str, language: str
) -> tuple[list[dict], list[dict], dict]:
    """The single retrieval and prompt-assembly path used by every chat transport."""
    profile_updates = extract_profile_updates(message)
    if has_profile_updates(profile_updates):
        current_profile = sessions.get_profile_memory(session_id)
        sessions.save_profile_memory(
            session_id, merge_profiles(current_profile, profile_updates)
        )
    retrieval = await kb.search_with_trace(message, top_k=3)
    context = retrieval["results"]
    trace = retrieval["trace"]
    trace["must_abstain"] = not context and requires_grounded_clinical_answer(message)
    session = sessions.get_or_create(session_id)
    system_prompt = prompt_manager.build_system_prompt(
        context,
        session.get("mood_log"),
        session.get("thought_records"),
        session.get("summary"),
        retrieval_status=trace["status"],
        profile_memory=session.get("profile_memory"),
        coping_resources=session.get("coping_resources"),
    )
    system_prompt = f"{system_prompt}\n\n{build_language_instruction(language)}"
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(
        {"role": msg["role"], "content": msg["content"]}
        for msg in sessions.get_history(session_id)
    )
    messages.append({"role": "user", "content": message})
    return messages, serialize_rag_context(context, trace), trace


def execute_app_tool(session_id: str, tool_call: dict) -> tuple[str, dict | None]:
    function = tool_call.get("function", {})
    name = function.get("name")
    args = function.get("arguments", {})
    if name == "get_user_sleep_history":
        return (
            json.dumps(
                sessions.get_sleep_logs(session_id, limit=args.get("days", 14)),
                ensure_ascii=False,
            ),
            None,
        )
    if name == "get_user_test_results":
        return json.dumps(sessions.get_tests(session_id), ensure_ascii=False), None
    if name == "get_user_activities":
        return (
            json.dumps(
                sessions.get_activities(session_id, limit=30), ensure_ascii=False
            ),
            None,
        )
    if name == "add_user_activity":
        text = args.get("activity_text", "")
        return f"Activity queued in the interface: {text}", {
            "type": "add_activity",
            "text": text,
        }
    if name in {"start_sos_exercise", "start_breathing"}:
        technique = args.get("technique", "breathing")
        if technique not in {"breathing", "grounding", "pmr", "stop"}:
            return f"Error: Unsupported SOS technique {technique}", None
        default_scenes = {
            "breathing": "air",
            "grounding": "field",
            "pmr": "sea",
            "stop": "night_forest",
        }
        scene = args.get("scene", default_scenes[technique])
        if scene not in {"air", "field", "sea", "night_forest"}:
            scene = default_scenes[technique]
        try:
            duration = int(args.get("duration", 2))
        except (TypeError, ValueError):
            duration = 2
        duration = max(1, min(duration, 10))
        return (
            f"SOS exercise opened: {technique}, scene {scene}, {duration} min.",
            {
                "type": "start_sos_exercise",
                "technique": technique,
                "scene": scene,
                "duration": duration,
            },
        )
    if name == "recommend_test":
        test_type = args.get("test_type", "PHQ-9")
        return f"The {test_type} test was opened in the interface.", {
            "type": "open_test",
            "test_type": test_type,
        }
    if name == "add_thought_record":
        situation = args.get("situation", "Диалог с ассистентом")
        thought = args.get("thought", "")
        emotion = args.get("emotion", "Тревога")
        try:
            intensity = int(args.get("intensity", 7))
        except (TypeError, ValueError):
            intensity = 7
        intensity = max(1, min(intensity, 10))
        distortion = args.get("distortion", "Автоматическая мысль")
        rational_response = args.get("rational_response", "")
        record_id = sessions.add_thought_record(
            session_id=session_id,
            situation=situation,
            thought=thought,
            emotion=emotion,
            intensity=intensity,
            distortion=distortion,
            rational_response=rational_response,
        )
        return f"Thought record #{record_id} saved to diary.", {
            "type": "add_thought_record",
            "record": {
                "id": record_id,
                "situation": situation,
                "thought": thought,
                "emotion": emotion,
                "intensity": intensity,
                "distortion": distortion,
                "rational_response": rational_response,
                "timestamp": datetime.now().isoformat(),
            },
        }
    if name in {"add_sleep_diary_record", "add_sleep_record", "add_sleep_log"}:
        bed = args.get("bed", "23:00")
        wake = args.get("wake", "07:00")
        try:
            quality = int(args.get("quality", 7))
        except (TypeError, ValueError):
            quality = 7
        quality = max(1, min(quality, 10))
        try:
            awakenings = int(args.get("awakenings", 0))
        except (TypeError, ValueError):
            awakenings = 0
        notes = args.get("notes", "")
        date_str = args.get("date")
        try:
            bed_time = datetime.strptime(bed.strip(), "%H:%M")
            wake_time = datetime.strptime(wake.strip(), "%H:%M")
            duration_hours = (wake_time - bed_time).total_seconds() / 3600.0
            if duration_hours < 0:
                duration_hours += 24.0
            duration_hours = round(duration_hours, 1)
        except (AttributeError, TypeError, ValueError):
            duration_hours = 8.0
        log_id = sessions.add_sleep_log(
            session_id=session_id,
            bed=bed,
            wake=wake,
            awk=awakenings,
            qual=quality,
            notes=notes,
            dur_hrs=duration_hours,
            iso_date=date_str,
        )
        return f"Sleep record #{log_id} saved to sleep diary.", {
            "type": "add_sleep_log",
            "log": {
                "id": log_id,
                "bed": bed,
                "wake": wake,
                "qual": quality,
                "awk": awakenings,
                "notes": notes,
                "durHrs": duration_hours,
                "isoDate": date_str or datetime.now().strftime("%Y-%m-%d"),
            },
        }
    if name == "get_user_resources":
        cat = args.get("category")
        if cat == "all":
            cat = None
        res_list = sessions.get_resources(session_id, category=cat)
        return (
            json.dumps(res_list, ensure_ascii=False),
            None,
        )
    if name == "add_user_resource":
        title = str(args.get("title", "")).strip()
        category = str(args.get("category", "joy")).strip() or "joy"
        description = str(args.get("description", "")).strip()
        if not title:
            return "Error: Resource title cannot be empty", None
        res_id = sessions.add_resource(
            session_id=session_id,
            title=title,
            category=category,
            description=description,
        )
        return f"Resource #{res_id} '{title}' saved to Resource Bank.", {
            "type": "add_resource",
            "resource": {
                "id": res_id,
                "title": title,
                "category": category,
                "description": description,
                "created_at": datetime.now().isoformat(),
            },
        }
    return f"Error: Unknown tool {name}", None


@app.post("/api/chat")
async def chat(req: ChatRequest):
    try:
        messages, context_used, rag_trace = await prepare_chat_messages(
            req.message, req.session_id, req.language
        )
        if rag_trace["must_abstain"]:
            content = grounded_abstention(req.language)
            sessions.add_message(req.session_id, "user", req.message)
            sessions.add_message(req.session_id, "assistant", content)
            await summarizer.maybe_summarize(req.session_id)
            return {
                "response": content,
                "context_used": [],
                "rag_trace": {
                    "trace_id": rag_trace["trace_id"],
                    "status": "abstained",
                    "latency_ms": rag_trace["latency_ms"],
                    "index_version": rag_trace["index_version"],
                },
                "session_id": req.session_id,
                "client_events": [],
            }
        client_events = []
        for _tool_round in range(4):
            resp = await llm_client.chat(
                messages, options=LLM_OPTIONS, tools=get_user_data_tools()
            )
            tool_calls = resp.get("tool_calls", [])
            content = resp.get("content", "")
            if tool_calls:
                messages.append(
                    {"role": "assistant", "content": content, "tool_calls": tool_calls}
                )
                for tc in tool_calls:
                    tool_content, event = execute_app_tool(req.session_id, tc)
                    if event:
                        client_events.append(event)
                    messages.append(
                        {
                            "role": "tool",
                            "content": tool_content,
                            "name": tc.get("function", {}).get("name"),
                        }
                    )
            else:
                content = ensure_rag_citations(content, context_used, req.language)
                sessions.add_message(req.session_id, "user", req.message)
                sessions.add_message(req.session_id, "assistant", content)
                await summarizer.maybe_summarize(req.session_id)
                return {
                    "response": content,
                    "context_used": context_used,
                    "rag_trace": {
                        "trace_id": rag_trace["trace_id"],
                        "status": rag_trace["status"],
                        "latency_ms": rag_trace["latency_ms"],
                        "index_version": rag_trace["index_version"],
                    },
                    "session_id": req.session_id,
                    "client_events": client_events,
                }
        raise RuntimeError("Model exceeded the maximum of 4 tool rounds")
    except Exception as e:
        raise HTTPException(500, f"Error communicating with model: {str(e)}")


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    from fastapi.responses import StreamingResponse

    try:
        messages, context_used, rag_trace = await prepare_chat_messages(
            req.message, req.session_id, req.language
        )
    except Exception as exc:
        raise HTTPException(503, f"RAG retrieval failed: {exc}") from exc

    async def generate():
        nonlocal messages
        yield f"data: {json.dumps({'context_used': context_used, 'rag_trace': rag_trace['trace_id']})}\n\n"
        if rag_trace["must_abstain"]:
            content = grounded_abstention(req.language)
            sessions.add_message(req.session_id, "user", req.message)
            sessions.add_message(req.session_id, "assistant", content)
            await summarizer.maybe_summarize(req.session_id)
            yield f"data: {json.dumps({'token': content})}\n\n"
            yield f"data: {json.dumps({'done': True, 'full_response': content, 'context_used': []})}\n\n"
            return
        for _tool_round in range(4):
            full_response = ""
            tool_calls = []
            try:
                async for chunk in llm_client.chat_stream(
                    messages, options=LLM_OPTIONS, tools=get_user_data_tools()
                ):
                    msg = chunk.get("message", {})
                    if msg.get("tool_calls"):
                        tool_calls = msg["tool_calls"]
                    token = msg.get("content", "")
                    if token:
                        full_response += token
                        if token.strip():
                            yield f"data: {json.dumps({'token': token})}\n\n"
                    if chunk.get("done"):
                        if tool_calls:
                            messages.append(
                                {
                                    "role": "assistant",
                                    "content": full_response,
                                    "tool_calls": tool_calls,
                                }
                            )
                            for tc in tool_calls:
                                fn_name = tc.get("function", {}).get("name")
                                tool_content, event = execute_app_tool(
                                    req.session_id, tc
                                )
                                payload = (
                                    {"client_event": event}
                                    if event
                                    else {"tool_call": fn_name}
                                )
                                yield f"data: {json.dumps(payload)}\n\n"
                                messages.append(
                                    {
                                        "role": "tool",
                                        "content": tool_content,
                                        "name": fn_name,
                                    }
                                )
                            break
                        else:
                            clean = ContentCleaner.strip_think_tags(full_response)
                            cited = ensure_rag_citations(
                                clean, context_used, req.language
                            )
                            citation_suffix = cited[len(clean) :]
                            if citation_suffix:
                                yield f"data: {json.dumps({'token': citation_suffix})}\n\n"
                            sessions.add_message(req.session_id, "user", req.message)
                            sessions.add_message(req.session_id, "assistant", cited)
                            await summarizer.maybe_summarize(req.session_id)
                            yield f"data: {json.dumps({'done': True, 'full_response': cited, 'context_used': context_used})}\n\n"
                            return
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                return
        yield f"data: {json.dumps({'error': 'Model exceeded the maximum of 4 tool rounds'})}\n\n"

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


@app.put("/api/thoughts/{thought_id}")
async def update_thought_record(thought_id: int, req: ThoughtRecordUpdateRequest):
    updated = sessions.update_thought_record(
        thought_id,
        req.session_id,
        req.situation,
        req.thought,
        req.emotion,
        req.intensity,
        req.distortion,
        req.rational_response,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Thought record not found")

    return {
        "status": "ok",
        "thought_records": sessions.get_or_create(req.session_id)["thought_records"],
    }


@app.post("/api/resources")
async def add_resource_item(req: ResourceRequest):
    if not req.title.strip():
        raise HTTPException(status_code=400, detail="Resource title is required")
    res_id = sessions.add_resource(
        session_id=req.session_id,
        title=req.title,
        category=req.category,
        description=req.description,
    )
    return {
        "status": "ok",
        "id": res_id,
        "resources": sessions.get_resources(req.session_id),
    }


@app.get("/api/resources/{session_id}")
async def get_resources_list(session_id: str, category: str | None = None):
    return {"resources": sessions.get_resources(session_id, category=category)}


@app.delete("/api/resources/{session_id}/{resource_id}")
async def delete_resource_item(session_id: str, resource_id: int):
    deleted = sessions.delete_resource(session_id, resource_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {
        "status": "ok",
        "resources": sessions.get_resources(session_id),
    }


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    return sessions.get_or_create(session_id)


@app.post("/api/session/{session_id}/save")
async def save_session(session_id: str):
    sessions.save_session(session_id)
    return {"status": "saved"}


@app.get("/api/memory/{session_id}")
async def get_memory(session_id: str):
    return {
        "session_id": session_id,
        "profile": sessions.get_profile_memory(session_id),
        "summary": sessions.get_session_summary(session_id),
    }


@app.delete("/api/memory/{session_id}")
async def clear_memory(session_id: str):
    sessions.clear_memory(session_id)
    return {"status": "cleared", "session_id": session_id}


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
    lang: str = "ru"
    mood_log: list[dict] = []
    sleep_log: list[dict] = []
    activities: list[dict] = []
    phq_history: list[dict] = []
    gad_history: list[dict] = []
    thought_records: list[dict] = []


def _build_insights_prompt(req: InsightsRequest) -> str:
    """Build a data summary for the LLM, only including sections that have real data."""
    en = req.lang == "en"
    sections = []

    # IMPORTANT: we only include a section if data actually exists.
    # Absence of data = not tracked, NOT a negative signal.

    if req.mood_log:
        recent = sorted(req.mood_log, key=lambda x: x.get("date", ""), reverse=True)[
            :14
        ]
        scores = [e.get("score") for e in recent if e.get("score") is not None]
        if scores:
            avg = round(sum(scores) / len(scores), 1)
            if en:
                sections.append(
                    f"MOOD (from mood journal — {len(scores)} entries over recent days):\n"
                    f"  Average score: {avg}/10. Scores: {scores[:10]}"
                )
            else:
                sections.append(
                    f"НАСТРОЕНИЕ (из записей дневника настроения — {len(scores)} оценок за последние дни):\n"
                    f"  Средняя оценка: {avg}/10. Оценки: {scores[:10]}"
                )

    if req.sleep_log:
        recent_sleep = sorted(
            req.sleep_log, key=lambda x: x.get("isoDate", ""), reverse=True
        )[:7]
        sleep_info = []
        for s in recent_sleep:
            hours = s.get("hours") or s.get("duration")
            quality = s.get("quality")
            if hours or quality:
                if en:
                    sleep_info.append(f"hours slept: {hours}, quality: {quality}")
                else:
                    sleep_info.append(f"часов сна: {hours}, качество: {quality}")
        if sleep_info:
            if en:
                sections.append(
                    f"SLEEP (sleep journal — {len(sleep_info)} days):\n  "
                    + "\n  ".join(sleep_info)
                )
            else:
                sections.append(
                    f"СОН (записи дневника сна — {len(sleep_info)} дней):\n  "
                    + "\n  ".join(sleep_info)
                )

    if req.activities:
        done = [a for a in req.activities if a.get("done")]
        pending = [a for a in req.activities if not a.get("done")]
        if en:
            sections.append(
                f"ACTIVITIES (planner): completed {len(done)}, pending/planned {len(pending)}"
            )
        else:
            sections.append(
                f"АКТИВНОСТИ (планировщик): выполнено {len(done)}, не выполнено/в плане {len(pending)}"
            )

    if req.phq_history:
        recent_phq = sorted(
            req.phq_history, key=lambda x: x.get("date", ""), reverse=True
        )[:3]
        phq_info = [
            f"PHQ-9: {e.get('score')} ({e.get('date', '')[:10]})" for e in recent_phq
        ]
        if en:
            sections.append("PHQ-9 TESTS (depression):\n  " + "\n  ".join(phq_info))
        else:
            sections.append("ТЕСТЫ PHQ-9 (депрессия):\n  " + "\n  ".join(phq_info))

    if req.gad_history:
        recent_gad = sorted(
            req.gad_history, key=lambda x: x.get("date", ""), reverse=True
        )[:3]
        gad_info = [
            f"GAD-7: {e.get('score')} ({e.get('date', '')[:10]})" for e in recent_gad
        ]
        if en:
            sections.append("GAD-7 TESTS (anxiety):\n  " + "\n  ".join(gad_info))
        else:
            sections.append("ТЕСТЫ GAD-7 (тревога):\n  " + "\n  ".join(gad_info))

    if req.thought_records:
        emotions = [
            t.get("emotion", "") for t in req.thought_records if t.get("emotion")
        ]
        distortions = [
            t.get("distortion", "") for t in req.thought_records if t.get("distortion")
        ]
        if en:
            sections.append(
                f"CBT THOUGHT JOURNAL ({len(req.thought_records)} entries):\n"
                f"  Emotions mentioned: {', '.join(emotions[:8])}\n"
                f"  Cognitive distortions: {', '.join(set(distortions[:6]))}"
            )
        else:
            sections.append(
                f"КПТ-ДНЕВНИК МЫСЛЕЙ ({len(req.thought_records)} записей):\n"
                f"  Упомянутые эмоции: {', '.join(emotions[:8])}\n"
                f"  Когнитивные искажения: {', '.join(set(distortions[:6]))}"
            )

    if not sections:
        return None  # No data at all

    data_block = "\n\n".join(sections)

    if en:
        return f"""You are a caring assistant helping a person better understand themselves.
Below is data from their personal journal over recent days. This is only what they have filled in themselves.

CRITICAL RULE: The absence of data in any section means only that the person did not fill in that section — it does NOT mean they slept poorly, were inactive, or were in a bad mood. Never draw conclusions from missing data.

Data:
{data_block}

Task: Write 2–3 gentle observations in English, based ONLY on what is present in the data above.
Rules:
- Use phrases like: "it seems", "possibly", "it looks like", "interestingly", "noticeably", "based on the entries"
- Do NOT make diagnoses or definitive conclusions
- You may end an observation with a gentle question
- Each observation is a separate paragraph, 1–2 sentences
- Tone: warm, like an attentive friend, not a doctor
- Reply only in English, no headings, no bullet lists — just paragraphs

If there is too little data for meaningful observations, write one gentle sentence about that."""
    else:
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
    en = req.lang == "en"
    prompt = _build_insights_prompt(req)

    if prompt is None:
        if en:
            no_data_msg = (
                "Not enough data for observations yet — "
                "the more you fill in your journal, the better I can notice patterns."
            )
        else:
            no_data_msg = (
                "Пока данных для наблюдений немного — чем больше ты заполняешь дневник, "
                "тем точнее я смогу замечать паттерны."
            )
        return {"insights": no_data_msg, "has_data": False}

    user_prompt = "Write the observations." if en else "Напиши наблюдения."
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_prompt},
    ]

    try:
        resp = await llm_client.chat(
            messages,
            options={
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 800,
            },
        )
        text = resp.get("content", "").strip()
        if not text:
            text = (
                "Nothing definitive to notice yet — keep filling in your journal."
                if en
                else "Пока сложно заметить что-то определённое — продолжай вести записи."
            )
        return {"insights": text, "has_data": True}
    except Exception as e:
        err_msg = (
            "Could not fetch insights right now."
            if en
            else "Не удалось получить наблюдения прямо сейчас."
        )
        return {"insights": err_msg, "has_data": False, "error": str(e)}


@app.get("/api/knowledge/search")
async def search_knowledge(q: str, top_k: int = 3):
    try:
        retrieval = await kb.search_with_trace(q, top_k)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(503, f"RAG retrieval failed: {exc}") from exc
    results = retrieval["results"]
    trace = retrieval["trace"]
    return {
        "query": q,
        "status": trace["status"],
        "trace_id": trace["trace_id"],
        "index_version": trace["index_version"],
        "embedding_model": trace["embedding_model"],
        "latency_ms": trace["latency_ms"],
        "results": [
            {
                "chunk_id": r["chunk"]["chunk_id"],
                "document_id": r["chunk"]["document_id"],
                "source": r["chunk"]["source"],
                "title": r["chunk"]["title"],
                "section_path": r["chunk"]["section_path"],
                "score": round(r["score"], 4),
                "preview": r["chunk"]["content"][:300],
            }
            for r in results
        ],
    }


@app.get("/api/knowledge/status")
async def knowledge_status():
    return kb.get_status()


async def fetch_ollama_models() -> list[dict]:
    """Return the models currently installed on the configured Ollama server."""
    import httpx

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(503, f"Ollama is unavailable: {exc}") from exc

    models = response.json().get("models", [])
    return sorted(
        [
            model
            for model in models
            if isinstance(model, dict) and isinstance(model.get("name"), str)
        ],
        key=lambda model: model["name"].lower(),
    )


def is_chat_model(model: dict) -> bool:
    """Treat legacy Ollama entries as chat-capable unless capabilities say otherwise."""
    capabilities = model.get("capabilities")
    return not isinstance(capabilities, list) or "completion" in capabilities


@app.get("/api/models")
async def get_ollama_models():
    models = await fetch_ollama_models()
    return {
        "models": models,
        "selected_model": llm_client.model,
        "ollama_url": OLLAMA_BASE_URL,
    }


@app.put("/api/settings/model")
async def select_ollama_model(request: ModelSelectionRequest):
    model_name = request.model.strip()
    if not model_name:
        raise HTTPException(422, "Model name cannot be empty")

    available_models = await fetch_ollama_models()
    selected_model = next(
        (model for model in available_models if model["name"] == model_name), None
    )
    if selected_model is None:
        raise HTTPException(
            400, "The selected model is not installed on this Ollama server"
        )
    if not is_chat_model(selected_model):
        raise HTTPException(400, "The selected Ollama model does not support chat")

    try:
        persist_selected_model(model_name)
    except OSError as exc:
        raise HTTPException(500, "Could not save the selected model") from exc

    llm_client.model = model_name
    return {"status": "ok", "selected_model": model_name}


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
        "status": "ok" if ollama_ok and kb.state == "ready" else "degraded",
        "version": __version__,
        "ollama_connected": ollama_ok,
        "ollama_url": OLLAMA_BASE_URL,
        "model": llm_client.model,
        "knowledge_chunks": len(kb.chunks),
        "rag": kb.get_status(),
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
    report_lines.append(
        f"Дата выписки: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    report_lines.append(f"Идентификатор сессии: {session_id}")
    report_lines.append("")
    report_lines.append("--- РЕЗЮМЕ ТЕРАПИИ (ДОЛГОСРОЧНАЯ ПАМЯТЬ) ---")
    report_lines.append(summary if summary else "Резюме еще не сформировано.")
    report_lines.append("")

    report_lines.append("--- ПОСЛЕДНИЕ ОЦЕНКИ НАСТРОЕНИЯ ---")
    if not mood_log:
        report_lines.append("Нет данных.")
    for m in mood_log[-10:]:
        report_lines.append(
            f"{m.get('timestamp')[:19]}: {m.get('score')}/10 - {m.get('note', '')}"
        )
    report_lines.append("")

    report_lines.append("--- ДНЕВНИК МЫСЛЕЙ (ПОСЛЕДНИЕ ЗАПИСИ) ---")
    if not thought_records:
        report_lines.append("Нет данных.")
    for tr in thought_records[-5:]:
        report_lines.append(f"[{tr.get('timestamp')[:19]}]")
        report_lines.append(f"Ситуация: {tr.get('situation', '')}")
        report_lines.append(f"Мысль: {tr.get('thought', '')}")
        report_lines.append(
            f"Эмоция: {tr.get('emotion', '')} ({tr.get('intensity', '')}/10)"
        )
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
        report_lines.append(
            f"[{t.get('iso_date')[:10]}] {t.get('test_name')}: {t.get('score')} баллов ({t.get('level')})"
        )

    report_content = "\n".join(report_lines)

    return PlainTextResponse(
        report_content,
        headers={
            "Content-Disposition": f"attachment; filename=cbt_report_{session_id}.txt"
        },
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

                try:
                    messages, context_used, rag_trace = await prepare_chat_messages(
                        user_msg, session_id, data.get("language", "en")
                    )
                except Exception as exc:
                    await websocket.send_json(
                        {"type": "error", "content": f"RAG retrieval failed: {exc}"}
                    )
                    continue

                await websocket.send_json(
                    {
                        "type": "context",
                        "context_used": context_used,
                        "rag_trace": rag_trace["trace_id"],
                    }
                )

                if rag_trace["must_abstain"]:
                    content = grounded_abstention(data.get("language", "en"))
                    sessions.add_message(session_id, "user", user_msg)
                    sessions.add_message(session_id, "assistant", content)
                    await summarizer.maybe_summarize(session_id)
                    await websocket.send_json(
                        {
                            "type": "done",
                            "content": content,
                            "context_used": [],
                            "rag_trace": rag_trace["trace_id"],
                            "status": "abstained",
                        }
                    )
                    continue

                full_response = ""
                try:
                    async for chunk in llm_client.chat_stream(
                        messages, options=LLM_OPTIONS
                    ):
                        token = chunk.get("message", {}).get("content", "")
                        if token:
                            full_response += token
                            await websocket.send_json(
                                {"type": "token", "content": token}
                            )
                        if chunk.get("done"):
                            clean = ContentCleaner.strip_think_tags(full_response)
                            cited = ensure_rag_citations(
                                clean, context_used, data.get("language", "en")
                            )
                            citation_suffix = cited[len(clean) :]
                            if citation_suffix:
                                await websocket.send_json(
                                    {"type": "token", "content": citation_suffix}
                                )
                            sessions.add_message(session_id, "user", user_msg)
                            sessions.add_message(session_id, "assistant", cited)
                            await summarizer.maybe_summarize(session_id)
                            await websocket.send_json(
                                {
                                    "type": "done",
                                    "content": cited,
                                    "context_used": context_used,
                                    "rag_trace": rag_trace["trace_id"],
                                }
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

    host = os.getenv("HOST", os.getenv("CBT_HOST", "127.0.0.1"))
    port = int(os.getenv("PORT", os.getenv("CBT_PORT", "8000")))
    uvicorn.run(app, host=host, port=port)

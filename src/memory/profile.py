"""Deterministic extraction and merging of durable personal memory."""

from __future__ import annotations

import re
from typing import Any


EMPTY_PROFILE: dict[str, Any] = {
    "user_name": None,
    "people": [],
    "pets": [],
    "preferences": [],
    "important_facts": [],
}

_NAME = r"([A-Za-zА-Яа-яЁё][A-Za-zА-Яа-яЁё'’-]{1,30}(?:\s+[A-Za-zА-Яа-яЁё][A-Za-zА-Яа-яЁё'’-]{1,30}){0,2})"
_CAPITALIZED_NAME = (
    r"([A-ZА-ЯЁ][A-Za-zА-Яа-яЁё'’-]{1,30}(?:\s+[A-ZА-ЯЁ][A-Za-zА-Яа-яЁё'’-]{1,30})?)"
)
_NAME_STOP_WORDS = {"and", "but", "i", "my", "и", "но", "я", "мой", "моя", "мне"}


def empty_profile() -> dict[str, Any]:
    return {
        "user_name": None,
        "people": [],
        "pets": [],
        "preferences": [],
        "important_facts": [],
    }


def _clean_name(value: str) -> str:
    words = []
    for word in value.strip(' .,!?:;"“”').split():
        if word.casefold() in _NAME_STOP_WORDS:
            break
        words.append(word)
    return " ".join(words)[:80]


def _first_match(patterns: list[str], text: str) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            value = _clean_name(match.group(1))
            if value:
                return value
    return None


def extract_profile_updates(text: str) -> dict[str, Any]:
    """Extract only explicit, user-stated personal facts without an LLM call."""
    updates = empty_profile()
    updates["user_name"] = _first_match(
        [
            rf"(?:меня\s+зовут|мо[её]\s+имя|зови\s+меня)\s+{_NAME}",
            rf"(?:my\s+name\s+is|call\s+me)\s+{_NAME}",
        ],
        text,
    )

    pet_kinds = {
        "собака": ("dog", r"собак(?:а|у|и|ой)?|п[её]с|пса|щенок"),
        "кошка": ("cat", r"кот(?:а|у|ом)?|кошк(?:а|у|и|ой)?|кот[её]нок"),
        "dog": ("dog", r"dog|puppy"),
        "cat": ("cat", r"cat|kitten"),
    }
    seen_pet_names: set[tuple[str, str]] = set()
    for _label, (kind, kind_pattern) in pet_kinds.items():
        patterns = [
            rf"(?:{kind_pattern})[^.!?\n]{{0,20}}?(?:зовут|по\s+имени|is\s+named|named)\s+{_NAME}",
            rf"(?:у\s+меня\s+(?:есть\s+)?)?(?:{kind_pattern})\s+{_CAPITALIZED_NAME}",
            rf"(?:my\s+)?(?:{kind_pattern})\s+(?:is\s+)?{_CAPITALIZED_NAME}",
        ]
        name = _first_match(patterns, text)
        key = (kind, (name or "").casefold())
        if name and key not in seen_pet_names:
            updates["pets"].append({"kind": kind, "name": name})
            seen_pet_names.add(key)

    relations = {
        "partner": r"мужа|муж|жену|жена|партн[её]ра|партн[её]рша|husband|wife|partner",
        "mother": r"маму|мама|мать|mother|mom",
        "father": r"папу|папа|отца|father|dad",
        "brother": r"брата|брат|brother",
        "sister": r"сестру|сестра|sister",
        "friend": r"друга|друг|подругу|подруга|friend",
    }
    for relation, relation_pattern in relations.items():
        name = _first_match(
            [
                rf"(?:мой|моя|моего|мою|my)?\s*(?:{relation_pattern})[^.!?\n]{{0,12}}?(?:зовут|is\s+named|named)\s+{_NAME}",
                rf"(?:мой|моя|моего|мою|my)\s+(?:{relation_pattern})\s*[-—:]?\s*{_CAPITALIZED_NAME}",
            ],
            text,
        )
        if name:
            updates["people"].append({"relation": relation, "name": name})

    preference_patterns = [
        r"(?:я\s+предпочитаю|мне\s+нравится|я\s+люблю)\s+([^.!?\n]{2,120})",
        r"(?:i\s+prefer|i\s+like|i\s+love)\s+([^.!?\n]{2,120})",
    ]
    for pattern in preference_patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            value = match.group(1).strip(" ,;:")
            if value:
                updates["preferences"].append(value)

    fact_patterns = [
        r"(?:я\s+живу\s+в|i\s+live\s+in)\s+([^.!?\n]{2,100})",
        r"(?:я\s+работаю|i\s+work)\s+([^.!?\n]{2,100})",
        r"(?:для\s+меня\s+важно|мне\s+важно|it\s+is\s+important\s+to\s+me)\s+([^.!?\n]{2,120})",
    ]
    for pattern in fact_patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            value = match.group(0).strip(" ,;:")
            if value:
                updates["important_facts"].append(value)
    return updates


def merge_profiles(
    current: dict[str, Any] | None, updates: dict[str, Any]
) -> dict[str, Any]:
    merged = empty_profile()
    if current:
        for key in merged:
            if key in current:
                merged[key] = current[key]
    if updates.get("user_name"):
        merged["user_name"] = updates["user_name"]

    for field, identity_fields in (
        ("people", ("relation", "name")),
        ("pets", ("kind", "name")),
    ):
        existing = {
            tuple(str(item.get(key, "")).casefold() for key in identity_fields)
            for item in merged[field]
        }
        for item in updates.get(field, []):
            identity = tuple(
                str(item.get(key, "")).casefold() for key in identity_fields
            )
            if identity not in existing:
                merged[field].append(item)
                existing.add(identity)
        merged[field] = merged[field][-20:]

    for field in ("preferences", "important_facts"):
        existing = {str(value).casefold() for value in merged[field]}
        for value in updates.get(field, []):
            if value.casefold() not in existing:
                merged[field].append(value)
                existing.add(value.casefold())
        merged[field] = merged[field][-20:]
    return merged


def has_profile_updates(updates: dict[str, Any]) -> bool:
    return bool(
        updates.get("user_name")
        or updates.get("people")
        or updates.get("pets")
        or updates.get("preferences")
        or updates.get("important_facts")
    )

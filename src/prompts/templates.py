import yaml
from pathlib import Path


class PromptManager:
    """Manages system prompts and context injection."""

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self._load_config()

    def _load_config(self):
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

    def build_system_prompt(
        self,
        context_chunks: list[dict],
        mood_history: list = None,
        thought_records: list = None,
        summary: str = None,
    ) -> str:
        base_prompt = self.config.get("system_prompts", {}).get(
            "default", "You are a helpful CBT assistant."
        )

        # Long-Term Memory (Summary) Context
        if summary:
            base_prompt += "\n--- ДОЛГОСРОЧНАЯ ПАМЯТЬ О ПАЦИЕНТЕ (РЕЗЮМЕ) ---\n"
            base_prompt += summary + "\n"
            base_prompt += "--- КОНЕЦ РЕЗЮМЕ ---\n"

        # RAG Context
        if context_chunks:
            base_prompt += "\n--- РЕЛЕВАНТНАЯ КЛИНИЧЕСКАЯ ИНФОРМАЦИЯ ---\n"
            for item in context_chunks:
                chunk = item["chunk"]
                base_prompt += f"\n[{chunk['title']}]\n{chunk['content'][:1500]}\n"
            base_prompt += "\n--- КОНЕЦ КЛИНИЧЕСКОЙ ИНФОРМАЦИИ ---\n"

        # Mood Context
        if mood_history:
            recent = mood_history[-5:]
            base_prompt += "\n--- ИСТОРИЯ НАСТРОЕНИЯ ПОЛЬЗОВАТЕЛЯ ---\n"
            for entry in recent:
                base_prompt += f"- {entry['timestamp']}: настроение {entry['score']}/10"
                if entry.get("note"):
                    base_prompt += f" ({entry['note']})"
                base_prompt += "\n"
            base_prompt += "--- КОНЕЦ ИСТОРИИ НАСТРОЕНИЯ ---\n"

        # Thought Records Context
        if thought_records:
            recent_thoughts = thought_records[-3:]
            base_prompt += "\n--- НЕДАВНИЕ ЗАПИСИ ДНЕВНИКА МЫСЛЕЙ ---\n"
            for entry in recent_thoughts:
                base_prompt += f"[{entry['timestamp']}]\n"
                base_prompt += f"Ситуация: {entry['situation']}\n"
                base_prompt += f"Мысль: {entry['thought']}\n"
                base_prompt += f"Эмоция: {entry['emotion']} ({entry['intensity']}/10)\n"
                base_prompt += f"Искажение: {entry['distortion']}\n"
                base_prompt += f"Рациональный ответ: {entry['rational_response']}\n\n"
            base_prompt += "--- КОНЕЦ ЗАПИСЕЙ ---\n"

        base_prompt += """
Помни: Твоя цель — оказать сочувственную поддержку, помогая развивать более здоровые мыслительные паттерны и стратегии совладания. Всегда ставь безопасность на первое место.
ВНИМАНИЕ: Если ты не уверен в точной технике, или хочешь дать совет, упражнение или протокол из КПТ — ты ОБЯЗАН сначала использовать инструмент `search_cbt_knowledge`, чтобы получить релевантные данные из базы исследований и практик. Опирайся только на данные, возвращенные этим инструментом.
"""
        return base_prompt

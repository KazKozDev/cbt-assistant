import asyncio
from typing import List, Dict
import logging

from src.llm.ollama_client import OllamaClient
from src.utils.db import SQLiteSessionManager

logger = logging.getLogger(__name__)

class MemorySummarizer:
    def __init__(self, db: SQLiteSessionManager, llm_client: OllamaClient):
        self.db = db
        self.llm_client = llm_client
        self.trigger_threshold = 15 # Summarize every 15 new messages

    async def _generate_summary(self, old_summary: str, recent_messages: List[Dict]) -> str:
        prompt = """
        Ты - эксперт-психолог, который ведет подробные клинические записи о пациенте.
        Твоя задача — обновить текущее резюме (саммари) пациента на основе новых сообщений из чата.

        ПРАВИЛА:
        1. Извлекай только ВАЖНЫЕ факты: триггеры, проблемы, применяемые методики, договоренности.
        2. Пиши кратко, емко, профессиональным языком.
        3. Сохраняй контекст из старого саммари, дополняя его новыми деталями. Убирай то, что стало неактуальным.
        4. Если старого саммари нет, просто создай новое.
        5. Не используй общие фразы вроде "пациент пишет" или "я ответил".

        --- СТАРОЕ РЕЗЮМЕ ---
        {old}
        
        --- НОВЫЕ СООБЩЕНИЯ ---
        {new}
        
        ОБНОВЛЕННОЕ РЕЗЮМЕ ПАЦИЕНТА:
        """

        formatted_msgs = "\n".join([f"{m['role']}: {m['content']}" for m in recent_messages])
        final_prompt = prompt.format(old=old_summary or "Нет данных", new=formatted_msgs)

        try:
            resp = await self.llm_client.chat([{"role": "user", "content": final_prompt}])
            return resp.get("content", "").strip()
        except Exception as e:
            logger.error(f"Failed to generate memory summary: {e}")
            return old_summary

    async def maybe_summarize(self, session_id: str):
        # Fire and forget wrapper for summarization logic
        asyncio.create_task(self._process_summarization(session_id))

    async def _process_summarization(self, session_id: str):
        try:
            # 1. Check if we need to summarize
            msg_count = self.db.get_message_count_since_last_summary(session_id)
            if msg_count < self.trigger_threshold:
                return

            # 2. Get old summary and un-summarized messages
            old_summary = self.db.get_session_summary(session_id)
            messages = self.db.get_unsummarized_messages(session_id)

            if not messages:
                return

            logger.info(f"Summarizing {len(messages)} messages for session {session_id}")

            # 3. Generate new summary
            new_summary = await self._generate_summary(old_summary, messages)

            if new_summary and new_summary != old_summary:
                # 4. Save to DB
                self.db.save_session_summary(session_id, new_summary)
                logger.info(f"Saved new summary for session {session_id}")

        except Exception as e:
            logger.error(f"Error in background summarization process: {e}")


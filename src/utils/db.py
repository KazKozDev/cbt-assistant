import sqlite3
from datetime import datetime
from pathlib import Path


class SQLiteSessionManager:
    """Manages SQLite database for sessions and mood logs."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    created_at TEXT
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TEXT,
                    FOREIGN KEY(session_id) REFERENCES sessions(id)
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS mood_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    score INTEGER,
                    note TEXT,
                    timestamp TEXT,
                    FOREIGN KEY(session_id) REFERENCES sessions(id)
                )
            """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_mood_session ON mood_logs(session_id)"
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS thought_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    situation TEXT,
                    thought TEXT,
                    emotion TEXT,
                    intensity INTEGER,
                    distortion TEXT,
                    rational_response TEXT,
                    timestamp TEXT,
                    FOREIGN KEY(session_id) REFERENCES sessions(id)
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sleep_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    bed TEXT,
                    wake TEXT,
                    awk INTEGER,
                    qual INTEGER,
                    notes TEXT,
                    dur_hrs REAL,
                    iso_date TEXT,
                    FOREIGN KEY(session_id) REFERENCES sessions(id)
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    test_name TEXT,
                    score INTEGER,
                    level TEXT,
                    iso_date TEXT,
                    FOREIGN KEY(session_id) REFERENCES sessions(id)
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    activity_text TEXT,
                    done INTEGER,
                    iso_date TEXT,
                    FOREIGN KEY(session_id) REFERENCES sessions(id)
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS session_summaries (
                    session_id TEXT PRIMARY KEY,
                    summary TEXT,
                    last_summarized_msg_id INTEGER,
                    updated_at TEXT,
                    FOREIGN KEY(session_id) REFERENCES sessions(id)
                )
            """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_thought_session ON thought_records(session_id)"
            )

    def get_or_create(self, session_id: str) -> dict:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
            session = cursor.fetchone()

            if not session:
                now = datetime.now().isoformat()
                cursor.execute(
                    "INSERT INTO sessions (id, created_at) VALUES (?, ?)",
                    (session_id, now),
                )
                conn.commit()

            cursor.execute(
                "SELECT role, content, timestamp FROM messages WHERE session_id = ? ORDER BY timestamp ASC",
                (session_id,),
            )
            messages = [dict(row) for row in cursor.fetchall()]

            cursor.execute(
                "SELECT score, note, timestamp FROM mood_logs WHERE session_id = ? ORDER BY timestamp ASC",
                (session_id,),
            )
            mood_log = [dict(row) for row in cursor.fetchall()]

            cursor.execute(
                "SELECT id, situation, thought, emotion, intensity, distortion, rational_response, timestamp FROM thought_records WHERE session_id = ? ORDER BY timestamp ASC",
                (session_id,),
            )
            thought_records = [dict(row) for row in cursor.fetchall()]

            cursor.execute(
                "SELECT summary FROM session_summaries WHERE session_id = ?",
                (session_id,),
            )
            sum_row = cursor.fetchone()
            summary = sum_row["summary"] if sum_row else None

            return {
                "id": session_id,
                "created_at": session["created_at"] if session else now,
                "messages": messages,
                "mood_log": mood_log,
                "thought_records": thought_records,
                "summary": summary,
            }

    def add_message(self, session_id: str, role: str, content: str):
        now = datetime.now().isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            # Ensure session exists
            cursor.execute(
                "INSERT OR IGNORE INTO sessions (id, created_at) VALUES (?, ?)",
                (session_id, now),
            )

            cursor.execute(
                "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (session_id, role, content, now),
            )
            conn.commit()
            return cursor.lastrowid

    def add_mood(self, session_id: str, score: int, note: str = ""):
        now = datetime.now().isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO sessions (id, created_at) VALUES (?, ?)",
                (session_id, now),
            )

            cursor.execute(
                "INSERT INTO mood_logs (session_id, score, note, timestamp) VALUES (?, ?, ?, ?)",
                (session_id, score, note, now),
            )
            conn.commit()

    def add_thought_record(
        self,
        session_id: str,
        situation: str,
        thought: str,
        emotion: str,
        intensity: int,
        distortion: str,
        rational_response: str,
    ):
        now = datetime.now().isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO sessions (id, created_at) VALUES (?, ?)",
                (session_id, now),
            )

            cursor.execute(
                "INSERT INTO thought_records (session_id, situation, thought, emotion, intensity, distortion, rational_response, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    session_id,
                    situation,
                    thought,
                    emotion,
                    intensity,
                    distortion,
                    rational_response,
                    now,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def update_thought_record(
        self,
        thought_id: int,
        session_id: str,
        situation: str,
        thought: str,
        emotion: str,
        intensity: int,
        distortion: str,
        rational_response: str,
    ) -> bool:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE thought_records
                SET situation = ?, thought = ?, emotion = ?, intensity = ?, distortion = ?, rational_response = ?
                WHERE id = ? AND session_id = ?
                """,
                (
                    situation,
                    thought,
                    emotion,
                    intensity,
                    distortion,
                    rational_response,
                    thought_id,
                    session_id,
                ),
            )
            conn.commit()
            return cursor.rowcount > 0

    def sync_sleep_logs(self, session_id: str, logs: list[dict]):
        with self._get_conn() as conn:
            conn.execute("DELETE FROM sleep_logs WHERE session_id = ?", (session_id,))
            for log in logs:
                conn.execute(
                    "INSERT INTO sleep_logs (session_id, bed, wake, awk, qual, notes, dur_hrs, iso_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        session_id,
                        log.get("bed"),
                        log.get("wake"),
                        log.get("awk"),
                        log.get("qual"),
                        log.get("notes"),
                        log.get("durHrs"),
                        log.get("isoDate"),
                    ),
                )
            conn.commit()

    def sync_test_results(self, session_id: str, tests: list[dict]):
        with self._get_conn() as conn:
            conn.execute("DELETE FROM tests WHERE session_id = ?", (session_id,))
            for test in tests:
                conn.execute(
                    "INSERT INTO tests (session_id, test_name, score, level, iso_date) VALUES (?, ?, ?, ?, ?)",
                    (
                        session_id,
                        test.get("name"),
                        test.get("score"),
                        test.get("level"),
                        test.get("date"),
                    ),
                )
            conn.commit()

    def sync_activities(self, session_id: str, activities: list[dict]):
        with self._get_conn() as conn:
            conn.execute("DELETE FROM activities WHERE session_id = ?", (session_id,))
            for act in activities:
                conn.execute(
                    "INSERT INTO activities (session_id, activity_text, done, iso_date) VALUES (?, ?, ?, ?)",
                    (
                        session_id,
                        act.get("text"),
                        1 if act.get("done") else 0,
                        act.get("isoDate"),
                    ),
                )
            conn.commit()

    def get_sleep_logs(self, session_id: str, limit: int = 14) -> list[dict]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM sleep_logs WHERE session_id = ? ORDER BY iso_date DESC LIMIT ?",
                (session_id, limit),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_tests(self, session_id: str) -> list[dict]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM tests WHERE session_id = ? ORDER BY iso_date DESC",
                (session_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_activities(self, session_id: str, limit: int = 30) -> list[dict]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM activities WHERE session_id = ? ORDER BY iso_date DESC LIMIT ?",
                (session_id, limit),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_history(self, session_id: str, limit: int = 20) -> list[dict]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content, timestamp FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (session_id, limit),
            )
            # Reverse to get chronological order from the last N entries
            msgs = [dict(row) for row in cursor.fetchall()]
            msgs.reverse()
            return msgs

    # --- MEMORY / SUMMARIZATION ---

    def get_session_summary(self, session_id: str) -> str:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT summary FROM session_summaries WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            return row["summary"] if row else ""

    def get_message_count_since_last_summary(self, session_id: str) -> int:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT last_summarized_msg_id FROM session_summaries WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            last_idx = row["last_summarized_msg_id"] if row else 0

            cursor.execute("SELECT COUNT(*) FROM messages WHERE session_id = ? AND id > ?", (session_id, last_idx))
            return cursor.fetchone()[0]

    def get_unsummarized_messages(self, session_id: str) -> list[dict]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT last_summarized_msg_id FROM session_summaries WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            last_idx = row["last_summarized_msg_id"] if row else 0

            cursor.execute(
                "SELECT id, role, content FROM messages WHERE session_id = ? AND id > ? ORDER BY id ASC",
                (session_id, last_idx)
            )
            return [dict(row) for row in cursor.fetchall()]

    def save_session_summary(self, session_id: str, new_summary: str):
        now = datetime.now().isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            # Get max msg ID to mark as summarized
            cursor.execute("SELECT MAX(id) FROM messages WHERE session_id = ?", (session_id,))
            max_id = cursor.fetchone()[0] or 0

            cursor.execute(
                """
                INSERT INTO session_summaries (session_id, summary, last_summarized_msg_id, updated_at) 
                VALUES (?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET 
                summary=excluded.summary, last_summarized_msg_id=excluded.last_summarized_msg_id, updated_at=excluded.updated_at
                """,
                (session_id, new_summary, max_id, now)
            )
            conn.commit()

    def save_session(self, session_id: str):
        # Database automatically persists on commit, so this is mostly a legacy stub for compatibility.
        pass

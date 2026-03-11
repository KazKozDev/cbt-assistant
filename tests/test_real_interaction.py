import asyncio
import httpx
import json

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = "real_user_session_123"

async def main():
    async with httpx.AsyncClient(timeout=300.0) as client:
        print(f"--- 1. Syncing User Data for {SESSION_ID} ---")
        
        # 1. Sync Tests
        tests_data = {
            "session_id": SESSION_ID,
            "items": [
                {"name": "GAD-7", "score": 15, "level": "Тяжелая тревога", "date": "2026-03-03"},
                {"name": "PHQ-9", "score": 12, "level": "Умеренная депрессия", "date": "2026-03-03"}
            ]
        }
        res = await client.post(f"{BASE_URL}/api/sync/tests", json=tests_data)
        print("Tests Sync:", res.json())

        # 2. Sync Sleep Logs
        sleep_data = {
            "session_id": SESSION_ID,
            "items": [
                {"bed": "02:00", "wake": "06:00", "awk": 3, "qual": 3, "notes": "Could not sleep", "durHrs": 4.0, "isoDate": "2026-03-02T20:00:00.000Z"},
                {"bed": "03:00", "wake": "07:00", "awk": 2, "qual": 4, "notes": "Anxiety at night", "durHrs": 4.0, "isoDate": "2026-03-03T20:00:00.000Z"}
            ]
        }
        res = await client.post(f"{BASE_URL}/api/sync/sleep", json=sleep_data)
        print("Sleep Sync:", res.json())

        # 3. Chat Request
        print("\n--- 2. Sending Chat Request ---")
        chat_msg = "Привет. Я почти не сплю последние дни, очень тревожно по ночам. Как мое состояние по последним тестам, и есть ли какие-то доказательные протоколы, которые мне помогут?"
        print(f"User: {chat_msg}")
        
        chat_data = {
            "session_id": SESSION_ID,
            "message": chat_msg
        }
        
        print("\nWaiting for AI response (this might take a minute as it searches KB and uses tools)...")
        res = await client.post(f"{BASE_URL}/api/chat", json=chat_data)
        
        if res.status_code == 200:
            print(f"\nAI Assistant:\n{res.json().get('response')}")
        else:
            print(f"Error: {res.status_code} - {res.text}")

if __name__ == "__main__":
    asyncio.run(main())

#!/bin/bash

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"
SERVER_FILE="$PROJECT_DIR/backend/server.py"
APP_URL="http://localhost:8000"
HEALTH_URL="$APP_URL/api/health"

if [ ! -x "$VENV_PYTHON" ]; then
    osascript -e 'display alert "CBT Assistant" message "Не найден .venv/bin/python. Сначала установите зависимости." as critical'
    exit 1
fi

if [ ! -f "$SERVER_FILE" ]; then
    osascript -e 'display alert "CBT Assistant" message "Не найден backend/server.py." as critical'
    exit 1
fi

TERMINAL_CMD="cd '$PROJECT_DIR'; if lsof -iTCP:8000 -sTCP:LISTEN >/dev/null 2>&1; then echo 'CBT Assistant уже запущен на $APP_URL'; else echo 'Запуск CBT Assistant...'; '$VENV_PYTHON' '$SERVER_FILE'; fi"
ESCAPED_TERMINAL_CMD="${TERMINAL_CMD//\\/\\\\}"
ESCAPED_TERMINAL_CMD="${ESCAPED_TERMINAL_CMD//\"/\\\"}"

osascript <<OSA
tell application "Terminal"
    activate
    do script "$ESCAPED_TERMINAL_CMD"
end tell
OSA

for _ in {1..60}; do
    if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
        open "$APP_URL"
        exit 0
    fi
    sleep 1
done

open "$APP_URL"

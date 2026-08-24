#!/bin/bash

set -Eeuo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BOOTSTRAP_BIN="$PROJECT_DIR/.bootstrap/bin"
VENV_DIR="$PROJECT_DIR/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"
SERVER_FILE="$PROJECT_DIR/backend/server.py"
REQUIREMENTS_FILE="$PROJECT_DIR/requirements.txt"
LOG_DIR="$PROJECT_DIR/logs"
APP_PORT="8000"
APP_URL="http://127.0.0.1:$APP_PORT"
HEALTH_URL="$APP_URL/api/health"
OLLAMA_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11434}"
CHAT_MODEL="${CBT_ASSISTANT_CHAT_MODEL:-qwen3:8b}"
EMBED_MODEL="qwen3-embedding:4b"
NO_PAUSE="${CBT_ASSISTANT_NO_PAUSE:-0}"

export PATH="$BOOTSTRAP_BIN:/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$PATH"

log() {
    printf '\n\033[1;35m[CBT Assistant]\033[0m %s\n' "$1"
}

fail() {
    printf '\n\033[1;31m[CBT Assistant] ERROR:\033[0m %s\n' "$1" >&2
    if command -v osascript >/dev/null 2>&1; then
        osascript -e "display alert \"CBT Assistant\" message \"${1//\"/\\\"}\" as critical" >/dev/null 2>&1 || true
    fi
    if [ -t 0 ] && [ "$NO_PAUSE" != "1" ]; then
        printf '\nPress Return to close...'
        read -r _
    fi
    exit 1
}

on_error() {
    local exit_code="$1"
    local line_number="$2"
    fail "Setup stopped at line $line_number (exit code $exit_code). See the terminal output above."
}

trap 'on_error $? $LINENO' ERR

find_ollama() {
    if command -v ollama >/dev/null 2>&1; then
        command -v ollama
        return 0
    fi

    local candidate
    for candidate in \
        "/Applications/Ollama.app/Contents/Resources/ollama" \
        "$HOME/Applications/Ollama.app/Contents/Resources/ollama" \
        "/opt/homebrew/bin/ollama" \
        "/usr/local/bin/ollama"; do
        if [ -x "$candidate" ]; then
            printf '%s\n' "$candidate"
            return 0
        fi
    done

    return 1
}

wait_for_url() {
    local url="$1"
    local attempts="$2"
    local attempt

    for ((attempt = 1; attempt <= attempts; attempt++)); do
        if curl -fsS --max-time 3 "$url" >/dev/null 2>&1; then
            return 0
        fi
        sleep 1
    done

    return 1
}

ensure_uv() {
    if command -v uv >/dev/null 2>&1; then
        UV_BIN="$(command -v uv)"
        return
    fi

    log "Installing the local Python bootstrap (uv)..."
    mkdir -p "$BOOTSTRAP_BIN"
    curl -LsSf https://astral.sh/uv/install.sh | env UV_UNMANAGED_INSTALL="$BOOTSTRAP_BIN" sh
    UV_BIN="$BOOTSTRAP_BIN/uv"
    [ -x "$UV_BIN" ] || fail "uv was downloaded but its executable was not found."
}

ensure_python_environment() {
    log "Preparing Python 3.12 and the virtual environment..."

    if [ ! -x "$VENV_PYTHON" ] || ! "$VENV_PYTHON" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
        "$UV_BIN" venv --clear --python 3.12 "$VENV_DIR"
    fi

    log "Installing or updating Python dependencies..."
    "$UV_BIN" pip install --python "$VENV_PYTHON" --requirements "$REQUIREMENTS_FILE"
}

ensure_ollama() {
    local ollama_bin

    if ! ollama_bin="$(find_ollama)"; then
        log "Ollama is not installed. Installing it from ollama.com..."
        curl -fsSL https://ollama.com/install.sh | sh
        ollama_bin="$(find_ollama)" || fail "Ollama installation finished, but the ollama command is unavailable."
    fi

    OLLAMA_BIN="$ollama_bin"

    if ! curl -fsS --max-time 3 "$OLLAMA_URL/api/version" >/dev/null 2>&1; then
        log "Starting Ollama..."
        mkdir -p "$LOG_DIR"

        if [ -d "/Applications/Ollama.app" ]; then
            open -gj -a Ollama || true
        elif [ -d "$HOME/Applications/Ollama.app" ]; then
            open -gj "$HOME/Applications/Ollama.app" || true
        fi

        if ! wait_for_url "$OLLAMA_URL/api/version" 15; then
            OLLAMA_HOST="${OLLAMA_URL#http://}" nohup "$OLLAMA_BIN" serve >"$LOG_DIR/ollama.log" 2>&1 &
        fi

        wait_for_url "$OLLAMA_URL/api/version" 90 || fail "Ollama did not become ready. Check $LOG_DIR/ollama.log."
    fi
}

ensure_model() {
    local model_name="$1"

    if "$OLLAMA_BIN" show "$model_name" >/dev/null 2>&1; then
        printf '[CBT Assistant] Model already installed: %s\n' "$model_name"
        return
    fi

    log "Downloading Ollama model: $model_name"
    "$OLLAMA_BIN" pull "$model_name"
}

release_app_port() {
    local listener_pids
    local listener_pid
    local remaining_pid
    local attempt

    listener_pids="$(lsof -tiTCP:"$APP_PORT" -sTCP:LISTEN 2>/dev/null || true)"
    [ -n "$listener_pids" ] || return

    log "Port $APP_PORT is busy. Stopping its current listener..."
    for listener_pid in $listener_pids; do
        case "$listener_pid" in
            *[!0-9]*|'') fail "Unexpected process identifier on port $APP_PORT: $listener_pid" ;;
        esac
        ps -p "$listener_pid" -o pid=,command= || true
        kill -TERM "$listener_pid" 2>/dev/null || fail "Cannot stop process $listener_pid on port $APP_PORT."
    done

    for ((attempt = 1; attempt <= 10; attempt++)); do
        if ! lsof -tiTCP:"$APP_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
            return
        fi
        sleep 1
    done

    listener_pids="$(lsof -tiTCP:"$APP_PORT" -sTCP:LISTEN 2>/dev/null || true)"
    for remaining_pid in $listener_pids; do
        case "$remaining_pid" in
            *[!0-9]*|'') fail "Unexpected process identifier on port $APP_PORT: $remaining_pid" ;;
        esac
        printf '[CBT Assistant] Process %s did not stop; forcing it to exit.\n' "$remaining_pid"
        kill -KILL "$remaining_pid" 2>/dev/null || fail "Cannot force-stop process $remaining_pid on port $APP_PORT."
    done

    if lsof -tiTCP:"$APP_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
        fail "Port $APP_PORT is still busy."
    fi
}

open_browser_when_ready() {
    if wait_for_url "$HEALTH_URL" 120; then
        log "CBT Assistant is ready at $APP_URL"
        open "$APP_URL"
        return
    fi

    printf '\n[CBT Assistant] The server did not pass its health check within 120 seconds.\n' >&2
    if command -v osascript >/dev/null 2>&1; then
        osascript -e 'display alert "CBT Assistant" message "Сервер не запустился за 120 секунд. Проверьте вывод Terminal." as critical' >/dev/null 2>&1 || true
    fi
}

main() {
    cd "$PROJECT_DIR"

    [ "$(uname -s)" = "Darwin" ] || fail "This .command launcher supports macOS only."
    [ -f "$SERVER_FILE" ] || fail "Missing backend/server.py in $PROJECT_DIR."
    [ -f "$REQUIREMENTS_FILE" ] || fail "Missing requirements.txt in $PROJECT_DIR."
    command -v curl >/dev/null 2>&1 || fail "curl is required for first-run downloads."
    command -v lsof >/dev/null 2>&1 || fail "lsof is required to manage port $APP_PORT."

    local macos_major
    macos_major="$(sw_vers -productVersion | cut -d. -f1)"
    case "$macos_major" in
        *[!0-9]*|'') fail "Could not determine the macOS version." ;;
    esac
    [ "$macos_major" -ge 14 ] || fail "Ollama requires macOS 14 Sonoma or newer."

    printf '\n\033[1;35mCBT ASSISTANT\033[0m\n'
    printf 'Local AI CBT companion · automatic macOS setup\n'

    ensure_uv
    ensure_python_environment
    ensure_ollama
    ensure_model "$CHAT_MODEL"
    ensure_model "$EMBED_MODEL"
    release_app_port

    export OLLAMA_BASE_URL="$OLLAMA_URL"
    export OLLAMA_MODEL="$CHAT_MODEL"

    log "Starting CBT Assistant..."
    open_browser_when_ready &
    exec "$VENV_PYTHON" "$SERVER_FILE"
}

main "$@"

#!/bin/bash -eu

# Runs the dev server (build + watch + serve on :6060) in the background, in a
# tmux window, writing output to a stable log file. Modeled on labs/lilac.

SOCKET=daemons
# tmux treats "." in a -t target as a window.pane separator, so replace it.
WINDOW="$(basename "$PWD" | tr . -)-dev"
LOG_DIR="$PWD/.logs"
LOG_FILE="$LOG_DIR/dev-server.log"
PORT=6060

mkdir -p "$LOG_DIR"
: > "$LOG_FILE"

# Ensure tmux server exists
if ! tmux -L "$SOCKET" has-session 2>/dev/null; then
    tmux -L "$SOCKET" new-session -d
fi

# Kill existing window if it exists
tmux -L "$SOCKET" kill-window -t "$WINDOW" 2>/dev/null || true

# Kill any other stale process still listening on the port.
# -sTCP:LISTEN ensures we only match the server, not clients.
lsof -tiTCP:$PORT -sTCP:LISTEN 2>/dev/null | xargs kill -9 2>/dev/null || true

# Start new window. Write server output to a stable log file so callers can
# tail it directly instead of reading tmux pane history.
tmux -L "$SOCKET" new-window -n "$WINDOW" -c "$PWD" "bash -lc '
exec uv run python -u build.py --serve --port $PORT > \"$LOG_FILE\" 2>&1
'"

printf 'dev server: http://127.0.0.1:%s\n' "$PORT"
printf 'dev server log: %s\n' "$LOG_FILE"

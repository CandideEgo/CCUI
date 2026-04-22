#!/bin/bash
#
# Claude Status Bar Installer (Unix/macOS/Linux)
# Installs the Claude Code status bar script and configures settings.json
#

set -e

CLAUDE_DIR="$HOME/.claude"
STATUSLINE_DIR="$CLAUDE_DIR/statusline"
SETTINGS_FILE="$CLAUDE_DIR/settings.json"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Installing Claude Status Bar..."

# Create directories
mkdir -p "$STATUSLINE_DIR"

# Copy scripts
cp "$PROJECT_DIR/status.py" "$STATUSLINE_DIR/"
cp "$PROJECT_DIR/debug.py" "$STATUSLINE_DIR/"

# Detect Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "Error: Python not found. Please install Python 3."
    exit 1
fi

# Get absolute path to status.py
STATUS_PY_PATH="$STATUSLINE_DIR/status.py"

# Configure settings.json
configure_settings() {
    if [ -f "$SETTINGS_FILE" ]; then
        # Check if statusLine already exists
        if grep -q '"statusLine"' "$SETTINGS_FILE"; then
            echo "statusLine already configured in $SETTINGS_FILE"
            echo "Please manually update the command path if needed:"
            echo "  $STATUS_PY_PATH"
        else
            # Add statusLine config using jq or python
            if command -v jq &> /dev/null; then
                tmp=$(mktemp)
                jq '.statusLine = {"type": "command", "command": "'"$PYTHON_CMD $STATUS_PY_PATH"'"}' "$SETTINGS_FILE" > "$tmp"
                mv "$tmp" "$SETTINGS_FILE"
                echo "Updated $SETTINGS_FILE"
            else
                echo "jq not found. Please manually add to $SETTINGS_FILE:"
                echo '  "statusLine": {"type": "command", "command": "'"$PYTHON_CMD $STATUS_PY_PATH"'"}'
            fi
        fi
    else
        # Create new settings.json
        mkdir -p "$CLAUDE_DIR"
        cat > "$SETTINGS_FILE" << EOF
{
  "statusLine": {
    "type": "command",
    "command": "$PYTHON_CMD $STATUS_PY_PATH"
  }
}
EOF
        echo "Created $SETTINGS_FILE"
    fi
}

configure_settings

echo ""
echo "Installation complete!"
echo "Restart Claude Code to see the status bar."
echo ""
echo "Debug: Logs are written to $STATUSLINE_DIR/debug.log"

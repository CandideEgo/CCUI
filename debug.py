#!/usr/bin/env python3
"""
Claude Code Status Bar Debug Script
Logs raw JSON input to a file for debugging purposes.
"""

import sys
from datetime import datetime
from pathlib import Path

# Windows UTF-8 support
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

LOG_FILE = Path.home() / ".claude" / "statusline" / "debug.log"


def write_log(message):
    """Write a message to the debug log."""
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(message)
    except Exception as e:
        print("Debug log error: {}".format(e), file=sys.stderr)


def main():
    """Main entry point."""
    try:
        data = sys.stdin.read()
        timestamp = datetime.now().isoformat()

        write_log("=== {} ===\n".format(timestamp))
        write_log(data)
        write_log("\n")

        # Print minimal output so status bar doesn't break
        print("debug mode")

    except Exception as e:
        write_log("ERROR: {}\n".format(e))
        print("Debug Error: {}".format(e))


if __name__ == "__main__":
    main()

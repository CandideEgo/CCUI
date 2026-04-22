#!/usr/bin/env python3
"""
Claude Code Custom Status Bar
Displays model, token usage with progress bar and color coding.
"""

import sys
import json
from pathlib import Path

VERSION = "1.1.0"

# Windows UTF-8 support
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

CACHE_FILE = Path.home() / ".claude" / "statusline" / ".cache.json"
BASELINE_FILE = Path.home() / ".claude" / "statusline" / "baseline.json"


def get_color(pct, thresholds=None):
    """Return ANSI color code based on percentage thresholds."""
    if thresholds is None:
        thresholds = {"green": 50, "yellow": 80}
    if pct < thresholds["green"]:
        return "\033[92m"  # Green
    elif pct < thresholds["yellow"]:
        return "\033[93m"  # Yellow
    else:
        return "\033[91m"  # Red


def format_tokens(n):
    """Format token count to K notation (decimal, 1K=1000)."""
    if n >= 1000:
        return f"{n/1000:.1f}K".replace(".0K", "K")
    return str(n)


def load_config():
    """Load configuration from config.json if it exists."""
    config_paths = [
        Path(__file__).parent / "config.json",
        Path.home() / ".claude" / "statusline" / "config.json",
    ]
    for path in config_paths:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return {}


def load_cache():
    """Load cached status data from previous run."""
    try:
        if CACHE_FILE.exists():
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return None


def save_cache(info):
    """Save status data to cache file."""
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(info, f)
    except Exception:
        pass


def load_baseline():
    """Load baseline data from baseline.json."""
    try:
        if BASELINE_FILE.exists():
            with open(BASELINE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return None


def parse_input(stdin_data, cache=None, baseline=None):
    """Parse Claude Code's JSON input and extract status info."""
    data = json.loads(stdin_data)

    session_id = data.get("session_id")
    model = data.get("model", {}).get("id", "unknown")
    cw = data.get("context_window", {})
    usage = cw.get("current_usage") or {}
    context_limit = cw.get("context_window_size", 200000)

    # Calculate usage based on percentage (syncs with /clear)
    used_pct = cw.get("used_percentage")

    # Normalize used_pct
    if used_pct is None:
        used_pct = 0
    # Use cache if available for same session
    elif used_pct == 0 and cache is not None:
        cached_session = cache.get("session_id")
        if cached_session == session_id:
            used_pct = cache.get("used_pct", 0)

    # Use baseline when used_pct is 0 (e.g., after /clear)
    if used_pct == 0 and baseline is not None:
        used_pct = baseline.get("baseline_pct", 0)

    total_tokens = round(context_limit * used_pct / 100)

    current_input = usage.get("input_tokens", 0) or 0
    current_output = usage.get("output_tokens", 0) or 0
    current_tokens = current_input + current_output

    return {
        "session_id": session_id,
        "model": model,
        "context_limit": context_limit,
        "used_pct": used_pct,
        "total_tokens": total_tokens,
        "current_tokens": current_tokens,
    }


def render_status(info, config=None):
    """Render status bar output."""
    if config is None:
        config = {}

    # Get thresholds from config or use defaults
    thresholds = config.get("thresholds", {"green": 50, "yellow": 80})

    # Progress bar
    filled = min(10, max(0, round(info["used_pct"] / 10)))
    bar = "\u2593" * filled + "\u2591" * (10 - filled)

    # Color
    color = get_color(info["used_pct"], thresholds)
    reset = "\033[0m"

    # Format output
    output = (
        f"{info['model']} \u2502 {format_tokens(info['total_tokens'])}"
        f"/{format_tokens(info['context_limit'])} \u2502 "
        f"{color}[{bar}] {info['used_pct']}%{reset}"
    )
    return output


def main():
    """Main entry point."""
    # Handle --help and --version
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Claude Code Status Bar v{}\n".format(VERSION))
        print("Usage: pipe Claude Code's JSON output to this script")
        print("  --help, -h     Show this help message")
        print("  --version      Show version")
        return

    if "--version" in sys.argv or "-v" in sys.argv:
        print("claude-statusline v{}".format(VERSION))
        return

    try:
        stdin_data = sys.stdin.read()
        if not stdin_data.strip():
            print("Waiting for input...")
            return

        config = load_config()
        cache = load_cache()
        baseline = load_baseline()
        info = parse_input(stdin_data, cache, baseline)
        output = render_status(info, config)
        print(output)
        save_cache(info)

    except json.JSONDecodeError as e:
        print("JSON parse error: {}".format(e))
    except Exception as e:
        print("StatusBar Error: {}".format(e))


if __name__ == "__main__":
    main()

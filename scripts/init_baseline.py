#!/usr/bin/env python3
"""
Claude Code Status Bar Baseline Initialization
Captures the baseline token usage (System prompt + System tools + Skills)
to be used as initial percentage after /clear resets usage to 0.
"""

import sys
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

# Windows UTF-8 support
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DEFAULT_CONTEXT_WINDOW = 200000  # Default context window
BASELINE_FILE = Path.home() / ".claude" / "statusline" / "baseline.json"


def capture_baseline():
    """Capture baseline by running /context in Claude Code."""
    claude_cmds = ["claude", "claude.cmd", "C:\\nvm4w\\nodejs\\claude.cmd"]
    last_error = None

    for cmd in claude_cmds:
        try:
            result = subprocess.run(
                [cmd, "--print"],
                input="/context\n",
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30
            )
            output = result.stdout + result.stderr
            if output:
                return output
        except FileNotFoundError:
            last_error = f"claude CLI not found (tried: {cmd})"
            continue
        except Exception as e:
            last_error = str(e)
            continue

    print(f"Error: {last_error}")
    return None


def parse_context_output(output):
    """Parse /context output to extract token values and context window."""
    if not output:
        return None

    system_prompt = 0
    system_tools = 0
    skills = 0
    free_space_pct = 0.0
    autocompact_pct = 0.0
    context_window = DEFAULT_CONTEXT_WINDOW

    # Parse context window from header like "**Tokens:** 22.5k / 200k"
    match = re.search(r'\*\*Tokens:\*\*\s*[\d.k]+\s*/\s*([\d.k]+)', output)
    if match:
        cw_text = match.group(1).strip()
        if 'k' in cw_text.lower():
            context_window = int(float(cw_text.lower().replace('k', '')) * 1000)
        else:
            try:
                context_window = int(cw_text)
            except ValueError:
                context_window = DEFAULT_CONTEXT_WINDOW

    # Parse table format: | System prompt | 5.9k | 3.0% |
    patterns = [
        (r'System prompt\s*\|\s*([\d.]+k)', 'system_prompt'),
        (r'System tools\s*\|\s*([\d.]+k)', 'system_tools'),
        (r'Skills\s*\|\s*([\d.]+k)', 'skills'),
        (r'Skills\s*\|\s*(\d+)', 'skills'),
    ]

    for pattern, field in patterns:
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            token_text = match.group(1).strip()
            value = 0
            if 'k' in token_text.lower():
                value = int(float(token_text.lower().replace('k', '')) * 1000)
            else:
                try:
                    value = int(token_text)
                except ValueError:
                    pass

            if field == 'system_prompt':
                system_prompt = value
            elif field == 'system_tools':
                system_tools = value
            elif field == 'skills':
                skills = value

    # Parse Free space and Autocompact buffer percentages
    # Format in table: "| Free space | 152.3k | 76.2% |"
    free_match = re.search(r'Free space\s*\|\s*[\d.k]+\s*\|\s*(\d+(?:\.\d+)?)%', output)
    if free_match:
        free_space_pct = float(free_match.group(1))

    # Format in table: "| Autocompact buffer | 33k | 16.5% |"
    auto_match = re.search(r'Autocompact buffer\s*\|\s*[\d.k]+\s*\|\s*(\d+(?:\.\d+)?)%', output)
    if auto_match:
        autocompact_pct = float(auto_match.group(1))

    return {
        "system_prompt_tokens": system_prompt,
        "system_tools_tokens": system_tools,
        "skills_tokens": skills,
        "free_space_pct": free_space_pct,
        "autocompact_pct": autocompact_pct,
        "context_window": context_window
    }


def calculate_baseline_pct(total_tokens, context_window=DEFAULT_CONTEXT_WINDOW):
    """Calculate baseline percentage from total tokens."""
    return round((total_tokens / context_window) * 100, 1)


def save_baseline(data):
    """Save baseline data to JSON file."""
    try:
        BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(BASELINE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving baseline: {e}")
        return False


def main():
    """Main entry point."""
    print("Capturing baseline token usage...")
    print()

    output = capture_baseline()
    if output is None:
        print("Failed to capture baseline.")
        sys.exit(1)

    parsed = parse_context_output(output)
    if parsed is None:
        print("Failed to parse /context output.")
        print("Raw output:")
        print(output)
        sys.exit(1)

    total_tokens = (
        parsed["system_prompt_tokens"] +
        parsed["system_tools_tokens"] +
        parsed["skills_tokens"]
    )
    context_window = parsed.get("context_window", DEFAULT_CONTEXT_WINDOW)

    # Baseline = 100% - free_space_pct - autocompact_pct
    baseline_pct = round(100.0 - parsed["free_space_pct"] - parsed["autocompact_pct"], 1)

    baseline_data = {
        "system_prompt_tokens": parsed["system_prompt_tokens"],
        "system_tools_tokens": parsed["system_tools_tokens"],
        "skills_tokens": parsed["skills_tokens"],
        "total_baseline_tokens": total_tokens,
        "baseline_pct": baseline_pct,
        "context_window": context_window,
        "captured_at": datetime.now().isoformat()
    }

    if save_baseline(baseline_data):
        print("Baseline captured successfully!")
        print()
        print(f"  System prompt:   {parsed['system_prompt_tokens']} tokens")
        print(f"  System tools:    {parsed['system_tools_tokens']} tokens")
        print(f"  Skills:         {parsed['skills_tokens']} tokens")
        print(f"  ─────────────────────────────")
        print(f"  Total:          {total_tokens} tokens")
        print(f"  Baseline:       {baseline_pct}%")
        print(f"  (Free: {parsed['free_space_pct']}% + Auto: {parsed['autocompact_pct']}%)")
        print()
        print(f"Saved to: {BASELINE_FILE}")
    else:
        print("Failed to save baseline.")
        sys.exit(1)


if __name__ == "__main__":
    main()

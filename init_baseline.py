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
from concurrent.futures import ThreadPoolExecutor, as_completed

# Windows UTF-8 support
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Shared constants with status.py
DEFAULT_CONTEXT_WINDOW = 200000
BASELINE_FILE = Path.home() / ".claude" / "statusline" / "baseline.json"

# Pre-compiled regex patterns
RE_CONTEXT_WINDOW = re.compile(r'\*\*Tokens:\*\*\s*[\d.k]+\s*/\s*([\d.k]+)')
RE_SYSTEM_PROMPT = re.compile(r'System prompt\s*\|\s*([\d.]+k)', re.IGNORECASE)
RE_SYSTEM_TOOLS = re.compile(r'System tools\s*\|\s*([\d.]+k)', re.IGNORECASE)
RE_SKILLS_K = re.compile(r'Skills\s*\|\s*([\d.]+k)', re.IGNORECASE)
RE_SKILLS_NUM = re.compile(r'Skills\s*\|\s*(\d+)', re.IGNORECASE)
RE_FREE_SPACE = re.compile(r'Free space\s*\|\s*[\d.k]+\s*\|\s*(\d+(?:\.\d+)?)%')
RE_AUTOCOMPACT = re.compile(r'Autocompact buffer\s*\|\s*[\d.k]+\s*\|\s*(\d+(?:\.\d+)?)%')


def capture_with_cmd(cmd):
    """Try to capture baseline with a single command."""
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
        return result.stdout + result.stderr
    except Exception:
        return None


def capture_baseline():
    """Capture baseline by running /context in Claude Code (races all candidates)."""
    claude_cmds = ["claude", "claude.cmd", "C:\\nvm4w\\nodejs\\claude.cmd"]

    with ThreadPoolExecutor(max_workers=len(claude_cmds)) as executor:
        futures = {executor.submit(capture_with_cmd, cmd): cmd for cmd in claude_cmds}
        for future in as_completed(futures):
            output = future.result()
            if output:
                # Cancel remaining futures and return
                for f in futures:
                    f.cancel()
                return output

    print("Error: claude CLI not found")
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

    match = RE_CONTEXT_WINDOW.search(output)
    if match:
        cw_text = match.group(1).strip()
        if 'k' in cw_text.lower():
            context_window = int(float(cw_text.lower().replace('k', '')) * 1000)
        else:
            try:
                context_window = int(cw_text)
            except ValueError:
                context_window = DEFAULT_CONTEXT_WINDOW

    for pattern, field in [(RE_SYSTEM_PROMPT, 'system_prompt'),
                            (RE_SYSTEM_TOOLS, 'system_tools'),
                            (RE_SKILLS_K, 'skills'),
                            (RE_SKILLS_NUM, 'skills')]:
        match = pattern.search(output)
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

    free_match = RE_FREE_SPACE.search(output)
    if free_match:
        free_space_pct = float(free_match.group(1))

    auto_match = RE_AUTOCOMPACT.search(output)
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

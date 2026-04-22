# Claude Code Custom Status Bar

> Display model name, token usage progress bar, and percentage in Claude Code's status bar

## Preview

```
MiniMax-M2.7 │ 48K/200K │ [▓▓░░░░░░░░] 24%
```

Color hints:
- Green: < 50%
- Yellow: 50% - 80%
- Red: > 80%

## Quick Start

### Windows

```powershell
.\scripts\install.ps1
```

### macOS / Linux / Git Bash

```bash
bash scripts/install.sh
```

The installer will automatically:
1. Copy scripts to `~/.claude/statusline/`
2. Configure `statusLine` in `settings.json`
3. Capture baseline token usage for accurate display after `/clear`
4. Restart Claude Code to see the status bar

For detailed instructions, see [Setup Guide](docs/setup-guide.md).

## Features

- Display current model name
- Token usage progress bar
- Color-coded percentage (green/yellow/red)
- Cross-platform (Windows/macOS/Linux)
- Customizable color thresholds
- Baseline token tracking (displays correct % after `/clear`)
- Debug script included for troubleshooting

## Project Structure

```
claude-statusline/
├── status.py              # Main status bar script
├── debug.py               # Debug script
├── scripts/
│   ├── install.sh         # Unix installer
│   ├── install.ps1        # Windows installer
│   └── init_baseline.py   # Baseline initialization script
└── docs/
    ├── setup-guide.md     # Setup guide
    ├── debug-method.md    # Debug method detailed
    ├── field-reference.md # Field reference
    └── troubleshooting.md # Troubleshooting
```

## Documentation

| Document | Description |
|----------|-------------|
| [Setup Guide](docs/setup-guide.md) | Complete setup instructions |
| [Debug Method](docs/debug-method.md) | How to debug unknown fields |
| [Field Reference](docs/field-reference.md) | Claude Code JSON fields |
| [Troubleshooting](docs/troubleshooting.md) | Common issues & solutions |

## How It Works

Claude Code periodically executes the configured shell command, passing JSON context data via stdin. The command's stdout text is displayed in the status bar.

This tool parses the JSON, extracts fields like `model.id` and `context_window.used_percentage`, and renders them as a progress bar with percentage.

## Alternative

For more complex features (Powerline style, multiple segments), see [CCometixLine](https://github.com/Haleclipse/CCometixLine), a Rust-based status bar tool.

## License

MIT

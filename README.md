# Claude Code 状态栏

> 显示模型、用量进度条、百分比的 Claude Code 状态栏工具

## 效果预览

```
MiniMax-M2.7 │ 48K/200K │ [▓▓░░░░░░░░] 24%
```

颜色提示：
- 绿色：< 50%
- 黄色：50% - 80%
- 红色：> 80%

## 快速开始

### Windows

```powershell
.\scripts\install.ps1
```

### macOS / Linux / Git Bash

```bash
bash scripts/install.sh
```

安装脚本会自动：
1. 复制脚本到 `~/.claude/statusline/` 目录
2. 配置 `settings.json` 中的 `statusLine` 选项
3. 重启 Claude Code 即可生效

**重要：安装后需要运行初始化脚本捕获基准值**（确保 `/clear` 后显示正确）：
```powershell
python .claude/statusline/init_baseline.py
```

详细安装说明请查看 [安装指南](docs/setup-guide.md)。

## 功能

- 显示当前模型名称
- 显示上下文用量进度条
- 百分比颜色提示（绿/黄/红）
- 跨平台支持（Windows/macOS/Linux）
- 支持自定义颜色阈值
- 基准值追踪（`/clear` 后仍显示正确百分比）
- 保留调试脚本，方便排查问题

## 项目结构

```
claude-statusline/
├── status.py              # 正式状态栏脚本
├── debug.py               # 调试脚本
├── scripts/
│   ├── install.sh         # Unix 安装脚本
│   ├── install.ps1        # Windows 安装脚本
│   └── init_baseline.py   # 基准值初始化脚本
└── docs/
    ├── setup-guide.md     # 安装配置指南
    ├── debug-method.md    # 日志调试法详解
    ├── field-reference.md # 字段速查表
    └── troubleshooting.md # 常见问题排查
```

## 文档

| 文档 | 说明 |
|------|------|
| [安装指南](docs/setup-guide.md) | 从零开始配置，包含各平台注意事项 |
| [调试方法详解](docs/debug-method.md) | 使用日志法调试未知字段 |
| [字段速查表](docs/field-reference.md) | Claude Code JSON 字段说明 |
| [常见问题排查](docs/troubleshooting.md) | 问题与解决方案 |

## 工作原理

Claude Code 定时执行配置的 shell 命令，通过 stdin 传入 JSON 格式的会话上下文，命令输出的文本即显示在状态栏。

本工具解析 JSON，提取 `model.id`、`context_window.used_percentage` 等字段，渲染为进度条和百分比显示。

## 替代方案

如果需要更复杂的功能（如 Powerline 风格、多 Segment 分离），可以参考 [CCometixLine](https://github.com/Haleclipse/CCometixLine)，一个 Rust 编写的状态栏工具。

## License

MIT

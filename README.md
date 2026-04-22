# Claude Code Status Bar

**一眼看清上下文余量，不再盲等 Claude 报 "context window" 错误。**

```
MiniMax-M2.7 │ 48K/200K │ [▓▓░░░░░░░░] 24%
```

视觉化显示 token 用量和进度条，**绿/黄/红三色**实时预警上下文消耗。

---

## 安装（30 秒）

**Windows:**
```powershell
.\scripts\install.ps1
```

**macOS / Linux:**
```bash
bash scripts/install.sh
```

安装后重启 Claude Code 即可看到状态栏。

---

## 解决什么问题

Claude Code 不显示上下文用量——你只能靠它报错才知道用完了。

本工具在状态栏实时展示：
- 当前模型
- 已用 / 总容量
- 进度条 + 百分比
- 用量颜色预警（绿 < 50% | 黄 50-80% | 红 > 80%）

---

## 技术细节

**架构**：Claude Code 定时执行 shell 命令，通过 stdin 传入 JSON 会话上下文，脚本解析后输出纯文本渲染到状态栏。

**三个核心文件**：
| 文件 | 作用 |
|------|------|
| `status.py` | 主脚本，解析 JSON → 输出进度条 |
| `debug.py` | 调试用，记录原始 JSON 方便排查 |
| `init_baseline.py` | 捕获基准值，用于 /clear 后正确显示 |

**基准值设计**：通过 `/context` 抓取 Free space% 和 Autocompact buffer%，计算 `baseline = 100% - free% - auto%`。这样 `/clear` 把用量重置为 0 时，状态栏仍显示准确的基准消耗。

**跨平台**：Windows (PowerShell) / macOS / Linux / Git Bash 均支持。

---

## 自定义

颜色阈值可在 `~/.claude/statusline/config.json` 配置：

```json
{
  "thresholds": {
    "green": 50,
    "yellow": 80
  }
}
```

---

## 项目结构

```
CCUI-master/
├── status.py              # 主脚本
├── debug.py               # 调试日志
├── scripts/
│   ├── install.ps1        # Windows 安装
│   ├── install.sh        # Unix 安装
│   └── init_baseline.py  # 基准值初始化
└── docs/
    ├── setup-guide.md     # 完整安装指南
    ├── debug-method.md    # 调试方法
    ├── field-reference.md # 字段参考
    └── troubleshooting.md # 常见问题
```

详细文档见 `docs/` 目录。
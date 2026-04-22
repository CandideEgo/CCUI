# Claude Code 状态栏字段速查表

> **版本**: Claude Code 2.1.92+
> **最后更新**: 2026-04-21

---

## Claude Code 传入的完整 JSON 结构

```json
{
  "session_id": "b705c2e9-4b68-4739-8c11-6d8821bd16ac",
  "transcript_path": "C:\\path\\to\\transcript.jsonl",
  "cwd": "C:\\Users\\Administrator",
  "model": {
    "id": "MiniMax-M2.7",
    "display_name": "MiniMax-M2.7"
  },
  "workspace": {
    "current_dir": "C:\\Users\\Administrator",
    "project_dir": "C:\\Users\\Administrator",
    "added_dirs": ["C:\\Users\\Administrator\\.claude\\scripts"]
  },
  "version": "2.1.92",
  "output_style": { "name": "default" },
  "cost": {
    "total_cost_usd": 7.28,
    "total_duration_ms": 14332431,
    "total_api_duration_ms": 1530118,
    "total_lines_added": 1209,
    "total_lines_removed": 88
  },
  "context_window": {
    "total_input_tokens": 732886,
    "total_output_tokens": 44422,
    "context_window_size": 200000,
    "current_usage": {
      "input_tokens": 108,
      "output_tokens": 280,
      "cache_creation_input_tokens": 0,
      "cache_read_input_tokens": 46976
    },
    "used_percentage": 24,
    "remaining_percentage": 76
  },
  "exceeds_200k_tokens": false
}
```

---

## 字段速查

| 想显示什么 | 字段路径 | 类型 | 示例值 | 备注 |
|-----------|----------|------|--------|------|
| 模型名称 | `model.id` | string | `"MiniMax-M2.7"` | |
| 模型显示名 | `model.display_name` | string | `"MiniMax-M2.7"` | |
| 上下文上限 | `context_window.context_window_size` | int | `200000` | 固定 200000 |
| 已用百分比 | `context_window.used_percentage` | int | `24` | `/clear` 后归零 |
| 剩余百分比 | `context_window.remaining_percentage` | int | `76` | |
| 输入 Token 总数 | `context_window.total_input_tokens` | int | `732886` | 累计值，不归零 |
| 输出 Token 总数 | `context_window.total_output_tokens` | int | `44422` | 累计值，不归零 |
| 当前请求输入 | `context_window.current_usage.input_tokens` | int | `108` | 可能为 null |
| 当前请求输出 | `context_window.current_usage.output_tokens` | int | `280` | 可能为 null |
| 缓存读取 Token | `context_window.current_usage.cache_read_input_tokens` | int | `46976` | |
| 会话成本 (USD) | `cost.total_cost_usd` | float | `7.28` | |
| 工作目录 | `workspace.current_dir` | string | `"C:\\..."` | |
| 项目目录 | `workspace.project_dir` | string | `"C:\\..."` | |

---

## 重要注意事项

### 1. `current_usage` 可能为 `null`

当没有活跃请求时，`current_usage` 字段为 `null`，访问其子字段会报错：

```python
# 错误方式
current_tokens = data["context_window"]["current_usage"]["input_tokens"]

# 正确方式
usage = data["context_window"].get("current_usage") or {}
current_tokens = usage.get("input_tokens", 0) or 0
```

### 2. 累计值 vs 会话值

| 字段 | 行为 |
|------|------|
| `used_percentage` | `/clear` 后归零 |
| `remaining_percentage` | `/clear` 后归零 |
| `total_input_tokens` | **不归零**，持续累计 |
| `total_output_tokens` | **不归零**，持续累计 |

如果需要显示随 `/clear` 重置的用量，应基于百分比计算：

```python
# 基于百分比计算（随 /clear 重置）
total_tokens = round(context_limit * used_pct / 100)

# 而非使用累计值（不随 /clear 重置）
total_tokens = total_input + total_output
```

### 3. `context_window_size` 固定值

文档可能记录为 `204800`，但实际固定为 `200000`（200K）。

---

## 示例：用这些字段构建状态栏

```python
import json

data = json.loads(sys.stdin.read())

# 基础信息
model = data["model"]["id"]
context_limit = data["context_window"]["context_window_size"]
used_pct = data["context_window"]["used_percentage"] or 0

# 基于百分比计算当前用量
total_tokens = round(context_limit * used_pct / 100)

# 进度条
filled = min(10, max(0, round(used_pct / 10)))
bar = "\u2593" * filled + "\u2591" * (10 - filled)

# 输出
print(f"{model} | {total_tokens}/{context_limit} | [{bar}] {used_pct}%")
```

输出示例：
```
MiniMax-M2.7 | 48000/200000 | [▓▓░░░░░░░░] 24%
```

---

## 相关文档

- [调试方法详解](debug-method.md) — 如何发现这些字段
- [完整安装指南](setup-guide.md) — 安装配置说明
- [常见问题排查](troubleshooting.md) — 问题与解决方案
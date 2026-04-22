# 日志调试法详解

## 背景

Claude Code 的官方文档可能存在字段名不准确的问题。通过直接观察 Claude Code 实际传出的 JSON 数据，可以绕过文档错误，快速定位正确字段。

这是一个通用的调试思路：**猜测之前先观察**。

---

## 调试流程

### 第一步：创建调试脚本

创建 `~/.claude/statusline/debug.py`：

```python
import sys
import json
from datetime import datetime

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

LOG_FILE = "/tmp/ccline_debug.log"  # 或 Windows: "C:/Users/YourName/debug.log"

try:
    data = sys.stdin.read()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"=== {datetime.now().isoformat()} ===\n")
        f.write(data)
        f.write("\n")
except Exception as e:
    with open(LOG_FILE, "a") as f:
        f.write(f"ERROR: {e}\n")

print("debug mode")  # 状态栏显示的文字
```

### 第二步：配置使用调试脚本

在 `settings.json` 中：

```json
"statusLine": {
  "type": "command",
  "command": "python /path/to/debug.py /path/to/debug.log"
}
```

### 第三步：触发并观察

1. 重启 Claude Code
2. 执行一些命令，触发状态栏更新（Claude Code 有 300ms 防抖）
3. 多触发几次，获取完整数据

### 第四步：分析日志

查看 `debug.log`，找到 Claude Code 传入的真实 JSON 结构。

---

## 为什么文档可能不准确

举几个实际例子：

| 问题 | 说明 |
|------|------|
| 字段名不符 | 文档说 `context_window_size` 是 204800，实际是 200000 |
| 缺少字段 | `current_usage` 在某些版本中可能为 `null` |
| 嵌套层级 | 文档可能缺少中间层级，如 `context_window.used_percentage` |

---

## 调试技巧

### 1. 多次触发

Claude Code 在不同状态下可能传入不同结构：
- 空闲状态（无活跃请求）
- 处理请求中
- `/clear` 之后

### 2. 对比差异

对比不同状态的 JSON，找出哪些字段是动态的，哪些是固定的。

### 3. 逐步解析

先用 `debug.py` 获取原始数据，再用 `jq` 或 Python 解析：

```bash
# 使用 jq 格式化
cat debug.log | jq '.context_window'

# 提取特定字段
cat debug.log | jq -r '.model.id'
```

---

## 从调试到正式脚本

获得真实 JSON 结构后，编写正式脚本：

```python
import json

data = json.loads(sys.stdin.read())

# 使用日志中发现的真实字段名
model = data["model"]["id"]
context_limit = data["context_window"]["context_window_size"]
used_pct = data["context_window"]["used_percentage"]
```

---

## 常见问题

### Q: 为什么 debug.log 是空的？

A: 检查以下几点：
1. Claude Code 是否重启
2. `settings.json` 中的路径是否正确
3. 是否有写入权限
4. 状态栏是否真正在更新（执行命令触发）

### Q: 如何看到完整的嵌套结构？

A: 使用 `jq` 的递归查询：
```bash
cat debug.log | jq '.. | objects | select(has("tokens"))'
```

---

## 相关文档

- [字段速查表](field-reference.md) — 已验证的字段说明
- [完整安装指南](setup-guide.md) — 安装配置说明
- [常见问题排查](troubleshooting.md) — 问题与解决方案
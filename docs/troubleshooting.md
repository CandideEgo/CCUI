# 常见问题排查

---

## 状态栏完全不显示

### 检查 1：配置是否正确

`settings.json` 中的配置格式：

```json
"statusLine": {
  "type": "command",
  "command": "python /path/to/status.py"
}
```

**常见错误**：
- 缺少 `"type": "command"`（会验证失败）
- 路径使用了反斜杠 `\`（Windows 应使用 `/`）
- 使用了 `python3` 但系统只有 `python`

### 检查 2：工作区是否被信任

状态栏命令需要工作区处于**信任状态**才能执行。

如果未信任，Claude Code 会显示警告通知。点击接受信任后即可。

### 检查 3：命令是否可执行

在终端手动测试：

```bash
# 测试脚本是否可以运行
python ~/.claude/statusline/status.py --help

# 测试空输入
echo '{}' | python ~/.claude/statusline/status.py
```

---

## 状态栏显示 "debug mode"

说明配置了调试脚本而非正式脚本。检查 `settings.json` 中的 command 是否指向 `status.py` 而非 `debug.py`。

---

## 显示 "StatusBar Error: ..."

脚本执行出错。可能原因：

### 1. JSON 解析失败

```error
JSON parse error: Expecting property name enclosed in double quotes
```

检查：输入数据是否为有效的 JSON。可能是脚本收到了空输入或损坏数据。

### 2. 字段访问错误

```error
StatusBar Error: 'NoneType' object is not subscriptable
```

检查：`current_usage` 可能为 `null`。使用 `.get()` 方法安全访问：

```python
usage = data.get("context_window", {}).get("current_usage") or {}
```

---

## 路径问题（Windows）

### 症状

```
python: can't open file 'C:\Users\...'
```

### 原因

使用了反斜杠 `\` 或路径格式不正确。

### 解决

在 `settings.json` 中使用正斜杠 `/`：

```json
"command": "python C:/Users/Administrator/.claude/statusline/status.py"
```

---

## Python 编码问题（Windows）

### 症状

状态栏显示乱码或空白，终端可能有编码警告。

### 原因

Windows 终端默认使用 GBK 编码，而非 UTF-8。

### 解决

`status.py` 已包含 Windows UTF-8 支持：

```python
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
```

如果仍有问题，确保 Claude Code 终端也使用 UTF-8 编码。

---

## 百分比不变（/clear 后）

### 症状

执行 `/clear` 后，`used_percentage` 归零了，但进度条显示的 token 总量没变。

### 原因

使用了累计 token 值而非基于百分比计算的值。

### 解决

使用百分比计算当前用量：

```python
# 正确方式
total_tokens = round(context_limit * used_pct / 100)

# 错误方式
total_tokens = total_input + total_output  # 这是累计值
```

---

## 颜色不显示

### 症状

进度条颜色是代码而非实际颜色（如 `[ 92m▓▓░░░░░░░░ 0m`）。

### 原因

Claude Code 的状态栏可能不支持 ANSI 颜色代码。

### 解决

检查 Claude Code 版本是否支持。对于不支持的情况，可以移除颜色代码：

```python
# 移除颜色相关代码
output = f"{model} │ {format_tokens(total_tokens)}/{format_tokens(context_limit)} │ [{bar}] {used_pct}%"
print(output)
```

---

## Python not found

### 症状

```
'python' is not recognized as an internal or external command
```

### 解决

1. 确认 Python 已安装
2. 添加 Python 到 PATH 环境变量
3. 或使用完整路径：`"C:/Python/python.exe ..."`

---

## 更多帮助

如果问题仍未解决：

1. 使用 `debug.py` 捕获原始 JSON 数据
2. 检查 [字段速查表](field-reference.md) 确认字段名正确
3. 查阅 [调试方法详解](debug-method.md) 了解如何排查

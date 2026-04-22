# Claude Code 状态栏配置指南

## 效果预览

```
MiniMax-M2.7 │ 48K/200K │ [▓▓░░░░░░░░] 24%
```

颜色：
- 绿色 (`<50%`)
- 黄色 (`50%-80%`)
- 红色 (`>80%`)

---

## 安装方式

### 方式一：一键安装（推荐）

#### Windows (PowerShell)

```powershell
.\scripts\install.ps1
```

如果遇到执行策略错误：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\scripts\install.ps1
```

#### macOS / Linux / Git Bash

```bash
bash scripts/install.sh
```

---

### 方式二：手动安装

#### 1. 复制脚本文件

将 `status.py` 和 `debug.py` 复制到 `~/.claude/statusline/` 目录：

```bash
mkdir -p ~/.claude/statusline
cp status.py debug.py ~/.claude/statusline/
```

#### 2. 配置 settings.json

在 `~/.claude/settings.json` 中添加：

```json
{
  "statusLine": {
    "type": "command",
    "command": "python /path/to/status.py"
  }
}
```

**Windows 示例**：
```json
"command": "python C:/Users/YourName/.claude/statusline/status.py"
```

**macOS/Linux 示例**：
```json
"command": "python3 /Users/YourName/.claude/statusline/status.py"
```

#### 3. 重启 Claude Code

完成配置后，**重启 Claude Code** 使配置生效。

---

## 平台注意事项

### Windows

- 使用 `python` 而非 `python3`（后者是快捷方式，可能不可用）
- 路径使用正斜杠 `/` 而非反斜杠 `\`
- 确保 Python 已添加到 PATH 环境变量

### macOS

- 通常使用 `python3` 命令
- 如遇权限问题：`chmod +x scripts/install.sh`

### Linux

- 确认已安装 Python 3
- 可能需要安装 tkinter：`sudo apt install python3-tk`（用于某些系统）

---

## 验证安装

### 1. 测试脚本语法

```bash
python ~/.claude/statusline/status.py --help
```

### 2. 测试空输入

```bash
echo '{}' | python ~/.claude/statusline/status.py
```

### 3. 使用调试脚本查看真实数据

在 `settings.json` 中临时替换为调试脚本：

```json
"command": "python C:/Users/YourName/.claude/statusline/debug.py C:/Users/YourName/debug.log"
```

重启 Claude Code 后，日志会写入 `debug.log`。

---

## 配置文件（可选）

可以在 `~/.claude/statusline/config.json` 创建配置文件来自定义颜色阈值：

```json
{
  "thresholds": {
    "green": 50,
    "yellow": 80
  }
}
```

---

## 卸载

从 `settings.json` 中删除 `statusLine` 配置块，然后重启 Claude Code。

---

## 相关文档

- [调试方法详解](debug-method.md) — 使用日志法调试未知字段
- [字段速查表](field-reference.md) — Claude Code JSON 字段说明
- [常见问题排查](troubleshooting.md) — 问题与解决方案

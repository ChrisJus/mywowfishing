# Audio Detection Tool / 音频检测工具

> 中文说明在前，English documentation follows below.

## 中文说明

### 免责声明

本工具仅用于个人学习、技术研究与代码示例展示，不得用于任何实际游戏场景或其他不当用途。使用者应自行承担由使用本工具所产生的一切风险、后果与责任。

### 项目简介

这是一个 macOS 下的音频检测工具示例。它会监听指定目标的音频流，并在检测到音量峰值超过阈值时触发后续动作。

当前版本具备以下流程：

1. 打开图形窗口并点击「启动」。
2. 脚本等待一段时间后开始运行。
3. 优先捕获目标进程音频；如果找不到目标音频进程，则回退为系统音频监听。
4. 持续打印当前音量和最近一段时间的音量峰值，便于调试。
5. 当最近峰值超过阈值时，执行预设动作。
6. 点击「停止」可中断监听和循环。

### 主要功能

- Tkinter 图形窗口：包含「启动」「停止」按钮。
- 可在窗口中配置音量阈值。
- 使用 `catap` 捕获目标进程音频。
- 目标音频进程找不到时，自动回退到系统音频捕获。
- 日志会打印当前音量和最近一段音量峰值，便于调试。

### 当前默认配置

配置位于 `fishing.py` 顶部：

```python
TIMEOUT = 120
START_DELAY = 2
KEY_TO_PRESS = '0'
THRESHOLD_DEFAULT = 0.05
RECENT_PEAK_WINDOW = 12
TARGET_APP_HINTS = ['Wow', 'World of Warcraft', 'Warcraft', '魔兽世界']
TARGET_AUDIO_HINTS = ['Wow', 'World of Warcraft', 'Warcraft', 'Battle.net', 'wxplayer', '魔兽世界']
```

你可以根据自己的目标程序，修改 `TARGET_APP_HINTS` 和 `TARGET_AUDIO_HINTS`。

### 环境要求

- macOS
- Python 3.14 当前已验证
- Homebrew
- macOS 14.2 或更新版本：`catap` 进程音频捕获需要 macOS 14.2+
- 系统权限：
  - 辅助功能权限：用于发送按键
  - 系统音频录制权限：用于捕获应用或系统音频

### 安装

进入项目目录：

```bash
cd /Users/justin/Desktop/wa/fish/mywowfishing
```

创建虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

安装依赖：

```bash
python -m pip install --upgrade pip
python -m pip install numpy catap pyobjc-framework-ApplicationServices
```

如果你的 Python 缺少 Tkinter，需要安装：

```bash
brew install python-tk@3.14
```

### macOS 权限设置

请到：

```text
系统设置 -> 隐私与安全性
```

打开以下权限：

1. **辅助功能**
   - 允许 Terminal / 终端
   - 或允许你实际运行脚本的宿主应用

2. **屏幕与系统音频录制 / 系统音频录制**
   - 允许 Terminal / 终端
   - 或允许你实际运行脚本的宿主应用

授权后建议重启终端或重新启动脚本。

### 运行

```bash
cd /Users/justin/Desktop/wa/fish/mywowfishing
source .venv/bin/activate
python fishing.py
```

窗口出现后点击「启动」。

### 使用建议

- 确认目标程序已经启动，并且窗口/进程名能被 `TARGET_APP_HINTS` 匹配。
- 确认目标程序正在产生音频。
- 如果音频进程无法匹配，脚本会自动回退到系统音频捕获。
- 如果检测太敏感，调高阈值，例如 `0.08`、`0.10`。
- 如果检测不到声音，调低阈值，例如 `0.03`、`0.02`。
- 查看终端日志中的：
  - `Volume`
  - `Recent peak`
  - `I heard something!`

### 常见问题

#### 1. `Target audio process not found`

说明 `catap` 没找到匹配的目标音频进程。当前脚本会自动回退到系统音频捕获。你也可以根据日志中的音频进程列表，修改：

```python
TARGET_AUDIO_HINTS
```

#### 2. `output_path must be provided unless on_buffer is set for streaming mode`

说明启动到了旧代码或旧进程。请确认当前文件已保存，并停止旧进程后重新运行：

```bash
source .venv/bin/activate
python fishing.py
```

#### 3. 能发送按键，但目标程序没有反应

请检查 macOS「辅助功能」权限是否已给 Terminal / 宿主应用。

#### 4. 没有检测到声音

先看日志中的 `Volume` 和 `Recent peak`：

- 如果一直是 `0.0000`，说明当前捕获源没有收到声音。
- 如果有数值但不触发，说明阈值过高，可以降低阈值。

### 许可说明

本项目基于原始项目进行修改，遵循 MIT License。

原始来源：

```text
https://github.com/codingories/mywowfishing
```

---

## English Documentation

### Disclaimer

This tool is for personal learning, technical research, and code demonstration only. Do not use it in any actual game scenario or for any other improper purpose. You are solely responsible for any risks, consequences, or liabilities resulting from its use.

### Project Overview

This is a macOS audio detection tool example. It listens to a selected audio source and triggers a predefined action when the recent volume peak exceeds the configured threshold.

Current workflow:

1. Open the GUI and click `Start`.
2. The script waits for a short delay before running.
3. It tries to capture audio from the target process first; if no target audio process is found, it falls back to system audio capture.
4. It prints live volume and recent peak values for debugging.
5. When the recent peak exceeds the threshold, it performs the preset action.
6. Click `Stop` to interrupt the loop.

### Features

- Tkinter GUI with `Start` and `Stop` buttons.
- Configurable audio threshold in the GUI.
- Uses `catap` to capture target process audio.
- Falls back to system audio capture if the target audio process is not found.
- Prints live volume and recent peak values for debugging.

### Default Configuration

Configuration is near the top of `fishing.py`:

```python
TIMEOUT = 120
START_DELAY = 2
KEY_TO_PRESS = '0'
THRESHOLD_DEFAULT = 0.05
RECENT_PEAK_WINDOW = 12
TARGET_APP_HINTS = ['Wow', 'World of Warcraft', 'Warcraft', '魔兽世界']
TARGET_AUDIO_HINTS = ['Wow', 'World of Warcraft', 'Warcraft', 'Battle.net', 'wxplayer', '魔兽世界']
```

You can change `TARGET_APP_HINTS` and `TARGET_AUDIO_HINTS` to match your own target application.

### Requirements

- macOS
- Python 3.14 tested
- Homebrew
- macOS 14.2 or later: required by `catap` for process audio capture
- macOS permissions:
  - Accessibility: required for sending key events
  - System audio recording: required for capturing application or system audio

### Installation

Go to the project directory:

```bash
cd /Users/justin/Desktop/wa/fish/mywowfishing
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install numpy catap pyobjc-framework-ApplicationServices
```

If your Python installation does not include Tkinter, install it with:

```bash
brew install python-tk@3.14
```

### macOS Permissions

Open:

```text
System Settings -> Privacy & Security
```

Enable permissions for Terminal or whichever host application runs the script:

1. **Accessibility**
   - Required for sending key events.

2. **Screen & System Audio Recording / System Audio Recording**
   - Required for capturing application or system audio.

After granting permissions, restart the terminal or relaunch the script.

### Run

```bash
cd /Users/justin/Desktop/wa/fish/mywowfishing
source .venv/bin/activate
python fishing.py
```

When the window appears, click `Start`.

### Usage Tips

- Make sure the target application is running and its process name matches `TARGET_APP_HINTS`.
- Make sure the target application is producing audio.
- If the audio process cannot be matched, the script falls back to system audio capture.
- If detection is too sensitive, raise the threshold, for example `0.08` or `0.10`.
- If detection misses sounds, lower the threshold, for example `0.03` or `0.02`.
- Watch terminal logs for:
  - `Volume`
  - `Recent peak`
  - `I heard something!`

### Troubleshooting

#### 1. `Target audio process not found`

`catap` could not find a matching target audio process. The script will fall back to system audio capture. You can also update:

```python
TARGET_AUDIO_HINTS
```

based on the printed audio process list.

#### 2. `output_path must be provided unless on_buffer is set for streaming mode`

You are likely running old code or an old process. Stop existing processes and restart:

```bash
source .venv/bin/activate
python fishing.py
```

#### 3. Key events are printed but the target application does not respond

Check that Accessibility permission is granted to Terminal or the host application.

#### 4. No audio is detected

Check `Volume` and `Recent peak` in the terminal logs:

- If they stay at `0.0000`, the selected capture source is silent.
- If they have values but do not trigger, lower the threshold.

### License Notes

This project is modified from the original project and follows the MIT License.

Original source:

```text
https://github.com/codingories/mywowfishing
```

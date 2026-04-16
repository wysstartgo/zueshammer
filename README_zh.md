# ZuesHammer - 宙斯之锤

<div align="center">

![版本](https://img.shields.io/badge/Version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10+-green.svg)
![许可证](https://img.shields.io/badge/License-MIT-yellow.svg)

**超级AI智能体 - Claude + Hermes + OpenClaw**

融合 ClaudeCode 工具编排、Hermes MCP 协议栈、OpenClaw 安全控制

</div>

---

## 特性

### 核心能力
- **智能对话**: 支持 Claude、OpenAI、本地模型
- **工具执行**: 安全的文件操作、终端命令、代码执行
- **记忆系统**: 三层架构（短期、长期、工作记忆）
- **技能系统**: 可扩展的技能工作流引擎

### 安全架构
- **权限分级**: safe / semi_open / full_open
- **危险检测**: 实时凭证泄露、恶意软件检测
- **配置保护**: 敏感配置防篡改
- **断路器**: 防止异常操作

### 集成能力
- **MCP协议**: Model Context Protocol 服务器支持
- **浏览器自动化**: Playwright 驱动的网页操作
- **语音交互**: 唤醒词检测、语音合成
- **多平台**: Telegram、企业微信等

---

## 快速开始

### 一键安装

```bash
# 克隆仓库
git clone https://github.com/zueshammer/zueshammer.git
cd zueshammer

# 一键安装
python3 install.py

# 或使用 pip
pip install -r requirements.txt
```

### 配置

编辑 `~/.zueshammer/.env`:

```bash
# API密钥 (必填)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# 权限级别
PERMISSION_LEVEL=semi_open
```

### 运行

```bash
# 命令行模式
python3 -m src.main --mode cli

# Web界面
python3 -m src.main --mode web

# 语音模式
python3 -m src.main --mode voice
```

---

## 安装选项

| 命令 | 说明 |
|------|------|
| `python3 install.py` | 交互式安装 |
| `python3 install.py --auto` | 自动安装（默认选项） |
| `python3 install.py --minimal` | 最小安装（仅核心） |
| `python3 install.py --update` | 更新依赖 |

---

## 项目结构

```
ZuesHammer/
├── src/                    # 源代码
│   ├── main.py             # 主入口
│   ├── zueshammer.py      # 核心类
│   ├── brain/              # 本地大脑
│   ├── tools/              # 工具系统
│   ├── memory/             # 记忆系统
│   ├── mcp/                # MCP协议
│   ├── voice/              # 语音系统
│   ├── browser/            # 浏览器自动化
│   ├── security/           # 安全模块
│   ├── llm/                # LLM客户端
│   ├── core/               # 核心系统
│   ├── chat/               # 聊天端口
│   ├── tui/                # 终端UI
│   ├── skills/             # 技能系统
│   ├── gateway/            # WebSocket网关
│   ├── config/             # 配置保护
│   └── utils/              # 工具函数
│
├── tests/                  # 测试
├── docs/                   # 文档
├── scripts/                # 脚本
├── config/                 # 默认配置
│
├── install.py              # 安装脚本
├── setup.py                # 包配置
├── main.py                 # 命令行快捷入口
├── requirements.txt         # 依赖
├── README.md               # 英文文档
├── README_zh.md            # 中文文档
├── LICENSE                 # MIT许可证
└── CONTRIBUTING.md         # 贡献指南
```

---

## API配置

### Anthropic (推荐)

```bash
ANTHROPIC_API_KEY=sk-ant-your-key
API_PROVIDER=anthropic
MODEL=claude-3-5-sonnet-20241022
```

### OpenAI

```bash
OPENAI_API_KEY=sk-your-key
API_PROVIDER=openai
MODEL=gpt-4o
```

### 本地模型

```bash
API_PROVIDER=local
API_BASE=http://localhost:11434
MODEL=llama3
```

---

## 权限级别

| 级别 | 说明 |
|------|------|
| `safe` | 所有操作需确认 |
| `semi_open` | 安全操作自动执行，危险操作警告 |
| `full_open` | 无限制（野兽模式） |

---

## 开发

### 运行测试

```bash
pytest
pytest tests/test_core.py
pytest --cov=src tests/
```

### 代码格式化

```bash
black src/
ruff check src/
```

---

## 常见问题

### Q: 报 "Module not found" 错误

```bash
pip install -r requirements.txt
```

### Q: 语音功能不工作

```bash
# macOS
brew install portaudio

# Ubuntu/Debian
sudo apt install portaudio19-dev
```

### Q: Playwright 报错

```bash
python -m playwright install --with-deps
```

---

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License - 详见 [LICENSE](./LICENSE)

---

<div align="center">

**用 ❤️ 为 AI 社区打造**

</div>

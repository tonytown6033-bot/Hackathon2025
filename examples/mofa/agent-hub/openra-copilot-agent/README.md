# OpenRA Copilot Agent

OpenRA 游戏 AI 助手代理，基于 MoFA 框架实现的单节点游戏控制系统。

## 功能特性

- 使用 OpenAI Function Calling 解析自然语言指令
- 直接调用 OpenRA 游戏 API 执行游戏操作
- 支持单位生产、移动、攻击、建造等完整游戏控制
- 集成 40+ 个游戏控制工具函数

## 安装使用

```bash
pip install -e .
```

## 环境变量

- `OPENAI_API_KEY`: OpenAI API 密钥
- `OPENAI_BASE_URL`: OpenAI API 基础URL
- `OPENAI_MODEL`: 使用的模型名称
- `OPENRA_PATH`: OpenRA AI 库路径
- `OPENRA_LIBRARY_PATH`: OpenRA Copilot 库路径
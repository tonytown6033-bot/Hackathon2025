# OpenRA AI Web控制器 - 精简版

## 概述
这是一个精简版的OpenRA AI Web控制系统，提供简洁的Web界面来控制游戏AI。

## 文件结构
```
web_ai/
├── start_web.py              # 启动脚本
├── web_chat_controller.py    # Web控制器主逻辑
├── battlefield_reader.py     # 战场状态读取
├── ai_analyzer.py           # AI分析模块
├── game_executor.py         # 游戏执行模块
├── requirements.txt         # 依赖包
└── templates/
    └── chat.html           # Web界面
```

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动Web界面
```bash
python start_web.py
```

### 3. 访问界面
打开浏览器访问：http://127.0.0.1:5000

## 功能特点
- 实时Web聊天界面
- 智能意图分析
- 自动战场状态读取
- AI策略推荐
- 游戏指令执行
- 实时反馈

## 示例指令
- "多多生产战车！"
- "专注防御建设"
- "疯狂造兵"
- "攻击敌人基地"

## 注意事项
- 需要OpenRA游戏运行并启动Copilot服务器
- 需要配置OpenAI API密钥
- 确保网络连接正常
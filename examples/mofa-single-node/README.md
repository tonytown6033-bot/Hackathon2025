# MoFA 单节点 OpenRA Copilot

基于 MoFA 框架的单节点 OpenRA 游戏控制系统，使用与 MCP 版本完全相同的底层逻辑。

## 🎯 项目特点

- **单节点架构**：将复杂的多节点数据流简化为单个 Agent
- **MCP 逻辑复用**：完全移植 MCP 版本的游戏工具集
- **智能命令解析**：支持自然语言游戏控制
- **简化部署**：相比原版 MoFA 实现更简洁

## 🏗️ 项目结构

```
mofa-single-node/
├── agent-hub/
│   └── openra-copilot-agent/        # 单节点 Agent
│       ├── openra_copilot_agent/
│       │   ├── main.py              # Agent 主逻辑
│       │   ├── openra_tools.py      # 游戏工具集（移植自 MCP）
│       │   └── __init__.py
│       ├── pyproject.toml
│       └── README.md
├── examples/
│   └── openra-single-controller/    # 运行示例
│       └── openra-single-controller.yml  # 数据流配置
└── README.md                        # 本文件
```

## 📋 环境要求

- Python >= 3.10
- Rust 环境（用于 Dora 运行时）
- OpenRA 游戏客户端
- MoFA 框架

## 🚀 快速开始

### 1. 安装依赖环境

```bash
# 安装 Rust 环境
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 安装 Dora 运行时
cargo install dora-cli

# 验证安装
dora --version
```

### 2. 安装 MoFA 框架

```bash
# 进入 mofa 根目录
cd ~/mofa

# 安装 MoFA 框架
pip install -e .
```

### 3. 安装项目依赖

```bash
# 进入项目目录
cd mofa-single-node

# 安装 Agent
pip install -e ./agent-hub/openra-copilot-agent

# 安装终端输入节点（复用原有的）
pip install -e ../mofa/node-hub/terminal-input
```

### 4. 配置环境变量

创建 `.env.secret` 文件：

```bash
# OpenRA 游戏路径
OPENRA_PATH=/path/to/your/OpenRA/Copilot/openra_ai

# 游戏连接配置
GAME_IP=localhost
GAME_PORT=7445
```

### 5. 启动系统

```bash
# 启动 OpenRA 游戏（确保 API 服务可用）

# 进入运行目录
cd examples/openra-single-controller

# 启动 Dora 服务
dora up

# 构建数据流
dora build openra-single-controller.yml

# 运行数据流
dora start openra-single-controller.yml
```

### 6. 开始游戏控制

在新终端中运行：

```bash
terminal-input
```

## 🎮 使用示例

支持智能自然语言命令：

```bash
# 生产单位
>>> 生产 5 个步兵
✅ 开始生产 5 个 步兵，任务ID: 12345

# 建造建筑
>>> 造电厂
✅ 开始生产 1 个 电厂，任务ID: 12346

# 查询信息
>>> 查询游戏状态
✅ 执行结果:
{
  "cash": 3000,
  "resources": 120,
  "power": 25,
  "visible_units": [...]
}

# 查看帮助
>>> help
🎮 OpenRA Copilot Agent 可用命令:
...
```

## 🔧 与其他版本对比

| 特性 | MCP 版本 | 原版 MoFA | 单节点 MoFA |
|------|----------|-----------|-------------|
| **架构复杂度** | ⭐⭐ 简单 | ⭐⭐⭐⭐⭐ 复杂 | ⭐⭐⭐ 中等 |
| **部署便利性** | ⭐⭐⭐⭐⭐ 最好 | ⭐⭐ 一般 | ⭐⭐⭐ 较好 |
| **功能完整性** | ⭐⭐⭐⭐⭐ 完整 | ⭐⭐⭐ 基础 | ⭐⭐⭐⭐⭐ 完整 |
| **扩展性** | ⭐⭐⭐⭐ 很好 | ⭐⭐⭐⭐ 很好 | ⭐⭐⭐⭐ 很好 |
| **维护成本** | ⭐⭐⭐⭐⭐ 最低 | ⭐⭐ 高 | ⭐⭐⭐ 中等 |

## 🎯 设计优势

### 相比原版 MoFA 实现

1. **简化架构**：从 4 个节点简化为 2 个节点（终端输入 + 单个 Agent）
2. **减少依赖**：不需要复杂的意图解析、战场读取、AI 分析等多个组件
3. **统一逻辑**：所有游戏控制逻辑集中在一个 Agent 中，便于维护
4. **完整功能**：复用 MCP 版本的完整工具集，功能更丰富

### 相比 MCP 版本

1. **框架优势**：利用 MoFA 的数据流管理和 Agent 生命周期
2. **扩展性**：更容易添加新的数据流节点和 Agent 间通信
3. **标准化**：符合 MoFA 框架的开发规范

## 🐛 故障排除

### OpenRA 连接问题
```bash
# 检查游戏是否运行
netstat -an | grep 7445

# 检查 OPENRA_PATH 环境变量
echo $OPENRA_PATH
```

### Dora 相关问题
```bash
# 重新启动 Dora 服务
dora down && dora up

# 查看日志
dora logs
```

### Agent 运行问题
```bash
# 查看 Agent 日志
tail -f logs/agent.log

# 重新安装 Agent
pip uninstall openra-copilot-agent
pip install -e ./agent-hub/openra-copilot-agent
```

## 💡 开发说明

### 添加新功能
修改 `openra_copilot_agent/openra_tools.py` 添加新的游戏 API 封装

### 修改命令解析
修改 `openra_copilot_agent/main.py` 中的智能命令解析逻辑

### 扩展数据流
修改 `openra-single-controller.yml` 添加新的节点或连接
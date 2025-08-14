# OpenRA MCP DataFlow

基于 MoFA 框架的 OpenRA MCP 数据流示例，整合了 MCP 服务器和游戏控制功能。

## 📦 项目结构

```
openra-mcp-dataflow/
├── openra-mcp-dataflow.yml    # Dora 数据流配置
├── run_mofa.sh                # 启动脚本
├── README.md                  # 使用说明
└── logs/                      # 运行日志目录
```

## ⚙️ 环境要求

- Python 3.10+
- Dora 数据流框架
- OpenRA 游戏和游戏服务器

## 🔐 配置说明

确保以下环境变量正确设置：
- `OPENRA_PATH`: OpenRA AI 库路径
- `MCP_SERVER_PORT`: MCP 服务器端口（默认 38721）  
- `GAME_API_PORT`: 游戏 API 端口（默认 7445）

## 🚀 启动方式

### 方式 1：使用启动脚本

```bash
./run_mofa.sh
```

### 方式 2：手动启动

```bash
# 1. 启动 Dora 服务
dora up

# 2. 构建数据流
dora build openra-mcp-dataflow.yml

# 3. 启动数据流
dora start openra-mcp-dataflow.yml --attach
```

## 🛠 数据流说明

该数据流包含两个主要节点：

1. **terminal-input**: 终端交互节点
   - 接收用户输入
   - 显示处理结果

2. **openra-mcp-agent-node**: MCP 游戏控制节点
   - 启动 MCP 服务器
   - 处理游戏控制逻辑
   - 与 OpenRA 游戏交互

## 📋 使用示例

启动后，你可以在终端中输入游戏指令：

```
>>> 查询当前游戏状态
>>> 生产一个电厂  
>>> 展开基地车
>>> 移动单位到 (100, 100)
```

## 🧼 停止和清理

- 按 `Ctrl+C` 停止数据流
- 使用 `dora destroy` 清理 Dora 服务

## 🔧 端口配置

- MCP 服务器: 端口 38721
- 游戏 API: 端口 7445

如需修改端口，请更新 `.yml` 文件中的环境变量。
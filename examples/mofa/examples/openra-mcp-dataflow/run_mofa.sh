#!/bin/bash

# OpenRA MCP DataFlow 启动脚本
# 基于 MoFA 框架，集成 MCP 服务器和游戏控制

cd /Users/liyao/Code/mofa/mofa_old/mofa/python/examples/openra-mcp-dataflow

echo "========================================="
echo "Starting OpenRA MCP DataFlow"
echo "========================================="

# 检查和设置环境变量
if [ -z "$OPENRA_PATH" ]; then
    export OPENRA_PATH="/Users/liyao/Code/mofa/OpenCodeAlert/Copilot/openra_ai"
    echo "设置默认 OPENRA_PATH: $OPENRA_PATH"
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  错误: 请设置 OPENAI_API_KEY 环境变量"
    echo "export OPENAI_API_KEY='your-api-key'"
    exit 1
fi

if [ -z "$OPENAI_BASE_URL" ]; then
    export OPENAI_BASE_URL="https://api.openai.com/v1"
fi

if [ -z "$OPENAI_MODEL" ]; then
    export OPENAI_MODEL="gpt-4o"
fi

# 检查 OpenRA 游戏服务器是否运行
echo -e "\n检查 OpenRA 游戏服务器状态..."
if ! nc -z localhost 7445 2>/dev/null; then
    echo "⚠️  警告: OpenRA 游戏服务器 (端口 7445) 未运行"
    echo "请先启动 OpenRA 游戏服务器后再运行此脚本"
    echo "----------------------------------------"
fi

# 1. 启动 Dora 服务
echo -e "\n1. Starting Dora service..."
dora up

# 2. 清理旧的安装和停止占用端口
echo -e "\n2. Cleaning up old installations and stopping services..."
pip uninstall -y openra-copilot-agent terminal-input 2>/dev/null || true

# 停止可能占用端口的进程
for port in 38721 7445 8000; do
    pid=$(lsof -t -i:$port 2>/dev/null)
    if [ -n "$pid" ]; then
        kill -9 $pid 2>/dev/null || true
        echo "释放了端口 $port"
    fi
done

# 3. 构建数据流
echo -e "\n3. Building dataflow..."
dora build openra-mcp-dataflow.yml

# 4. 启动数据流
echo -e "\n4. Starting dataflow (press Ctrl+C to stop)..."
echo "========================================="
echo "🎮 OpenRA MCP DataFlow 已启动"
echo "📊 MCP 服务器端口: 38721"
echo "🎯 游戏 API 端口: 7445"
echo ""
echo "💡 你现在可以输入游戏指令："
echo "   >>> 查询当前游戏状态"
echo "   >>> 生产一个电厂"
echo "   >>> 展开基地车"
echo "========================================="
dora start openra-mcp-dataflow.yml --attach
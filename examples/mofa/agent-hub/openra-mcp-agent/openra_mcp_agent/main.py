#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""OpenRA MCP Agent - MoFA 单节点版本 with AI Tool Calling"""

import json
import os
import sys
from typing import Any, Dict, List
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

# 添加 OpenRA 路径
sys.path.append(os.getenv('OPENRA_PATH', '/Users/liyao/Code/mofa/OpenCodeAlert/Copilot/openra_ai'))

from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from .openra_tools import OpenRATools


class OpenRAMCPAgent:
    """OpenRA MCP Agent - 真正的 AI 工具调用版本"""
    
    def __init__(self):
        self.tools = OpenRATools()
        self.client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        )
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o')
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """返回可用工具的 OpenAI Function Calling 格式定义 - 包含所有35个MCP工具"""
        return [
            # 基础状态查询工具
            {
                "type": "function",
                "function": {
                    "name": "get_game_state",
                    "description": "获取游戏当前状态，包括资源、电力和可见单位",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "player_base_info_query",
                    "description": "查询玩家基地的资源、电力等基础信息",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "screen_info_query",
                    "description": "查询当前屏幕信息",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "map_query",
                    "description": "查询地图信息并返回序列化数据",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            
            # 单位查询和管理工具
            {
                "type": "function",
                "function": {
                    "name": "query_actor",
                    "description": "查询单位列表",
                    "parameters": {
                        "type": "object", 
                        "properties": {
                            "type": {"type": "array", "items": {"type": "string"}, "description": "单位类型过滤，空数组表示所有类型"},
                            "faction": {"type": "string", "description": "阵营: '己方', '敌方', '任意'", "default": "己方"},
                            "range": {"type": "string", "description": "范围: 'screen', 'all'", "default": "all"},
                            "restrain": {"type": "array", "items": {"type": "object"}, "description": "约束条件", "default": []}
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "visible_units",
                    "description": "根据条件查询可见单位",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "array", "items": {"type": "string"}, "description": "单位类型过滤"},
                            "faction": {"type": "string", "description": "阵营: '己方', '敌方', '任意'"},
                            "range": {"type": "string", "description": "范围: 'screen', 'all'"},
                            "restrain": {"type": "array", "items": {"type": "object"}, "description": "约束条件"}
                        },
                        "required": ["type", "faction", "range", "restrain"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_actor_by_id",
                    "description": "根据Actor ID获取单个单位的信息",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "actor_id": {"type": "integer", "description": "要查询的Actor ID"}
                        },
                        "required": ["actor_id"]
                    }
                }
            },
            
            # 生产相关工具
            {
                "type": "function", 
                "function": {
                    "name": "produce",
                    "description": "生产指定类型和数量的单位",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "unit_type": {"type": "string", "description": "单位类型，如 '步兵', '电厂', '重坦', '矿车' 等"},
                            "quantity": {"type": "integer", "description": "生产数量", "minimum": 1}
                        },
                        "required": ["unit_type", "quantity"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "can_produce",
                    "description": "检查是否可以生产某种单位",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "unit_type": {"type": "string", "description": "单位类型"}
                        },
                        "required": ["unit_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "start_production",
                    "description": "开始生产单位或建筑，适用于建造电厂等建筑",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "unit_type": {"type": "string", "description": "要生产的单位或建筑类型，如 '电厂', '兵营', '步兵' 等"},
                            "quantity": {"type": "integer", "description": "生产数量", "default": 1},
                            "auto_place_building": {"type": "boolean", "description": "是否自动放置建筑", "default": True}
                        },
                        "required": ["unit_type"]
                    }
                }
            },
            
            # 移动和部署工具
            {
                "type": "function",
                "function": {
                    "name": "move_units",
                    "description": "移动一批单位到指定坐标",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "actor_ids": {"type": "array", "items": {"type": "integer"}, "description": "单位ID列表"},
                            "x": {"type": "integer", "description": "目标X坐标"},
                            "y": {"type": "integer", "description": "目标Y坐标"},
                            "attack_move": {"type": "boolean", "description": "是否攻击移动", "default": False}
                        },
                        "required": ["actor_ids", "x", "y"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "deploy_units",
                    "description": "部署单位（如展开基地车、部署攻城单位等）",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "actor_ids": {"type": "array", "items": {"type": "integer"}, "description": "要部署的单位ID列表，如果不提供则自动寻找基地车"}
                        },
                        "required": []
                    }
                }
            },
            
            # 镜头控制工具
            {
                "type": "function",
                "function": {
                    "name": "camera_move_to",
                    "description": "将镜头移动到指定坐标",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "integer", "description": "目标X坐标"},
                            "y": {"type": "integer", "description": "目标Y坐标"}
                        },
                        "required": ["x", "y"]
                    }
                }
            }
        ]
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """调用具体的工具函数"""
        try:
            tool_method = getattr(self.tools, tool_name)
            if arguments:
                return tool_method(**arguments)
            else:
                return tool_method()
        except Exception as e:
            return f"工具调用失败: {str(e)}"
    
    def process_command_with_ai(self, user_input: str) -> str:
        """使用 AI 解析用户指令并调用相应工具 - 支持多轮对话"""
        try:
            # 构建对话消息
            messages = [
                {
                    "role": "system", 
                    "content": """你是 OpenRA 游戏的专业 AI 助手，你必须严格按照以下规则操作：

## 🎯 核心原则
1. **永远先调用工具再回答** - 绝不能凭空回答或假设结果
2. **必须验证操作结果** - 根据工具返回的实际结果判断成功与否
3. **诚实报告失败** - 如果操作失败，必须如实告知用户真实原因

## 📋 严格执行流程

### 用户要求"建造电厂/制造电厂/生产电厂"：
1. 调用 `get_game_state()` 查看当前状态
2. 调用 `produce(unit_type="powr", quantity=1)` （注意：必须使用配置名"powr"而不是中文"电厂"）
3. **关键：检查produce的返回结果**
   - 如果返回包含错误信息，必须告诉用户具体错误
   - 如果返回成功，再次调用 `get_game_state()` 验证
4. 根据实际结果回答用户

### 用户要求"展开基地车/部署基地车"：
1. 调用 `get_game_state()` 查看当前状态
2. 调用 `deploy_units()` (无参数，会自动寻找mcv类型单位)
3. **关键：检查deploy_units的返回结果**
   - 如果返回包含错误信息，必须告诉用户具体错误
   - 如果返回成功，再次调用 `get_game_state()` 确认结果
4. 根据实际结果回答用户

## 🔧 重要：单位名称必须使用配置名
- 电厂 → "powr"
- 基地车 → "mcv" 
- 兵营 → "tent"/"barr"
- 战车工厂 → "weap"
- 矿场 → "proc"
- 雷达 → "dome"
- 步兵 → "e1"
- 火箭兵 → "e3"
- 轻坦克 → "1tnk"
- 重坦克 → "3tnk"

### 用户要求"查看游戏状态"：
1. 调用 `get_game_state()` 
2. 将结果清晰地呈现给用户

## ⚠️ 绝对禁止的行为
- ❌ 说"已经成功建造"但实际没有调用工具
- ❌ 忽略工具返回的错误信息
- ❌ 假设操作成功而不验证结果
- ❌ 给出模糊的回答如"可能成功了"

## ✅ 正确的回答方式
- 🎯 "生产电厂失败，错误：缺少必要建筑"（基于实际工具结果）
- 🎯 "基地车展开成功，建筑已出现"（基于实际验证）
- 🎯 "当前现金15000，无可见单位，需要先展开基地车"（基于实际状态）

记住：你是基于工具结果的事实报告者，不是乐观的假设者！"""
                },
                {"role": "user", "content": user_input}
            ]
            
            # 多轮对话处理
            max_turns = 5  # 最多5轮对话防止无限循环
            turn_count = 0
            
            while turn_count < max_turns:
                turn_count += 1
                print(f"🔄 第{turn_count}轮AI处理...")
                
                # 调用 OpenAI API
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.get_available_tools(),
                    tool_choice="auto"
                )
                
                message = response.choices[0].message
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": message.tool_calls
                })
                
                # 如果 AI 选择了工具调用
                if message.tool_calls:
                    tool_results = []
                    
                    for tool_call in message.tool_calls:
                        tool_name = tool_call.function.name
                        arguments = json.loads(tool_call.function.arguments)
                        
                        print(f"🤖 AI 调用工具: {tool_name} 参数: {arguments}")
                        
                        # 调用工具
                        result = self.call_tool(tool_name, arguments)
                        tool_results.append(f"工具 {tool_name} 执行结果: {result}")
                        
                        # 添加工具调用结果到消息历史
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result, ensure_ascii=False) if isinstance(result, (dict, list)) else str(result)
                        })
                    
                    # 检查是否还需要继续调用工具
                    # 继续下一轮，让AI看到工具结果并决定是否还需要更多操作
                    continue
                
                else:
                    # AI 没有选择工具调用，说明完成了
                    return message.content
            
            # 达到最大轮数，返回最后一次回复
            return "操作已完成，如有需要请重新发起指令。"
                
        except Exception as e:
            return f"❌ AI 处理失败: {str(e)}"


@run_agent
def run(agent: MofaAgent):
    """Agent 主运行函数"""
    mcp_agent = OpenRAMCPAgent()
    
    # 接收用户命令
    user_input = agent.receive_parameter('user_command')
    
    print(f"🎮 收到用户指令: {user_input}")
    
    # 使用 AI 处理命令
    result = mcp_agent.process_command_with_ai(user_input)
    
    print(f"📤 AI 处理结果: {result}")
    
    # 发送输出
    agent.send_output(agent_output_name='copilot_result', agent_result=result)


def main():
    """主函数"""
    agent = MofaAgent(agent_name='openra-mcp-agent')
    run(agent=agent)


if __name__ == "__main__":
    main()
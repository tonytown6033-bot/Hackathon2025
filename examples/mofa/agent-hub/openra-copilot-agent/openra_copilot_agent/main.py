#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""OpenRA Copilot Agent - MoFA 单节点版本 with AI Tool Calling"""

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


class OpenRACopilotAgent:
    """OpenRA Copilot Agent - 真正的 MCP 风格 AI 工具调用"""
    
    def __init__(self):
        self.tools = OpenRATools()
        self.client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        )
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """返回可用工具的 OpenAI Function Calling 格式定义"""
        return [
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
                    "name": "attack_target", 
                    "description": "命令单位攻击目标",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "attacker_id": {"type": "integer", "description": "攻击者单位ID"},
                            "target_id": {"type": "integer", "description": "目标单位ID"}
                        },
                        "required": ["attacker_id", "target_id"]
                    }
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
                    "name": "ensure_can_produce_unit",
                    "description": "确保能生产指定单位（会自动补齐依赖建筑并等待完成）",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "unit_name": {"type": "string", "description": "单位名称"}
                        },
                        "required": ["unit_name"]
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
        """使用 AI 解析用户指令并调用相应工具"""
        try:
            # 构建对话消息
            messages = [
                {
                    "role": "system", 
                    "content": """你是 OpenRA 游戏的 AI 助手。用户会用自然语言描述他们想要执行的游戏操作，你需要：

1. 理解用户意图
2. 调用相应的工具函数来执行操作
3. 返回操作结果

可用的主要操作：
- 生产单位：步兵、电厂、重坦、矿车、兵营等
- 查询状态：游戏状态、单位信息、资源信息
- 单位控制：移动、攻击等

请根据用户指令调用合适的工具。"""
                },
                {"role": "user", "content": user_input}
            ]
            
            # 调用 OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.get_available_tools(),
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            
            # 如果 AI 选择了工具调用
            if message.tool_calls:
                results = []
                
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    print(f"🤖 AI 调用工具: {tool_name} 参数: {arguments}")
                    
                    # 调用工具
                    result = self.call_tool(tool_name, arguments)
                    results.append({
                        "tool": tool_name,
                        "arguments": arguments, 
                        "result": result
                    })
                
                # 让 AI 总结结果
                summary_messages = messages + [
                    message,
                    {
                        "role": "user",
                        "content": f"工具执行结果：{json.dumps(results, ensure_ascii=False)}。请用简洁的中文总结执行情况。"
                    }
                ]
                
                summary_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=summary_messages
                )
                
                return summary_response.choices[0].message.content
            
            else:
                # AI 没有选择工具调用，直接返回回答
                return message.content
                
        except Exception as e:
            return f"❌ AI 处理失败: {str(e)}"


@run_agent
def run(agent: MofaAgent):
    """Agent 主运行函数"""
    copilot = OpenRACopilotAgent()
    
    # 接收用户命令
    user_input = agent.receive_parameter('user_command')
    
    print(f"🎮 收到用户指令: {user_input}")
    
    # 使用 AI 处理命令
    result = copilot.process_command_with_ai(user_input)
    
    print(f"📤 AI 处理结果: {result}")
    
    # 发送输出
    agent.send_output(agent_output_name='copilot_result', agent_result=result)


def main():
    """主函数"""
    agent = MofaAgent(agent_name='openra-copilot-agent')
    run(agent=agent)


if __name__ == "__main__":
    main()
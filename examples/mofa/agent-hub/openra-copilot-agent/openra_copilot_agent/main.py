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
            {
                "type": "function",
                "function": {
                    "name": "update_actor",
                    "description": "根据actor_id更新该单位的信息",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "actor_id": {"type": "integer", "description": "要更新的Actor ID"}
                        },
                        "required": ["actor_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "unit_attribute_query",
                    "description": "查询指定单位的属性及其攻击范围内的目标",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "actor_ids": {"type": "array", "items": {"type": "integer"}, "description": "要查询的单位ID列表"}
                        },
                        "required": ["actor_ids"]
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
            {
                "type": "function",
                "function": {
                    "name": "query_production_queue",
                    "description": "查询指定类型的生产队列",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "queue_type": {"type": "string", "description": "队列类型: 'Building', 'Defense', 'Infantry', 'Vehicle', 'Aircraft', 'Naval'"}
                        },
                        "required": ["queue_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "manage_production",
                    "description": "管理生产队列中的项目（暂停、取消或继续）",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "queue_type": {"type": "string", "description": "队列类型"},
                            "action": {"type": "string", "description": "操作类型: 'pause', 'cancel', 'resume'"}
                        },
                        "required": ["queue_type", "action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "place_building",
                    "description": "放置已生产完成的建筑",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "queue_type": {"type": "string", "description": "生产队列类型: 'Building', 'Defense', 'Infantry', 'Vehicle', 'Aircraft', 'Naval'"},
                            "x": {"type": "integer", "description": "放置X坐标（可选，不指定则自动选址）"},
                            "y": {"type": "integer", "description": "放置Y坐标（可选，不指定则自动选址）"}
                        },
                        "required": ["queue_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "ensure_can_build_wait",
                    "description": "确保指定建筑已存在，若不存在则递归建造其所有依赖并等待完成",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "building_name": {"type": "string", "description": "建筑名称（中文）"}
                        },
                        "required": ["building_name"]
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
                    "name": "move_units_by_location",
                    "description": "把一批单位移动到指定坐标",
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
                    "name": "move_units_by_direction",
                    "description": "按方向移动一批单位",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "actor_ids": {"type": "array", "items": {"type": "integer"}, "description": "单位ID列表"},
                            "direction": {"type": "string", "description": "移动方向"},
                            "distance": {"type": "integer", "description": "移动距离"}
                        },
                        "required": ["actor_ids", "direction", "distance"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "move_units_by_path",
                    "description": "沿指定路径移动一批单位",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "actor_ids": {"type": "array", "items": {"type": "integer"}, "description": "单位ID列表"},
                            "path": {"type": "array", "items": {"type": "object"}, "description": "路径点列表，每个点为 {x: int, y: int} 形式"}
                        },
                        "required": ["actor_ids", "path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "move_units_and_wait",
                    "description": "移动一批单位到指定位置并等待到达或超时",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "actor_ids": {"type": "array", "items": {"type": "integer"}, "description": "单位ID列表"},
                            "x": {"type": "integer", "description": "目标X坐标"},
                            "y": {"type": "integer", "description": "目标Y坐标"},
                            "max_wait_time": {"type": "number", "description": "最大等待时间（秒）", "default": 10.0},
                            "tolerance_dis": {"type": "integer", "description": "到达判定的曼哈顿距离容差", "default": 1}
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
            
            # 选择和编组工具
            {
                "type": "function",
                "function": {
                    "name": "select_units",
                    "description": "选中符合条件的单位",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "array", "items": {"type": "string"}, "description": "单位类型过滤"},
                            "faction": {"type": "string", "description": "阵营"},
                            "range": {"type": "string", "description": "范围"},
                            "restrain": {"type": "array", "items": {"type": "object"}, "description": "约束条件"}
                        },
                        "required": ["type", "faction", "range", "restrain"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "form_group",
                    "description": "为一批单位编组",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "actor_ids": {"type": "array", "items": {"type": "integer"}, "description": "要编组的单位ID列表"},
                            "group_id": {"type": "integer", "description": "编组ID"}
                        },
                        "required": ["actor_ids", "group_id"]
                    }
                }
            },
            
            # 攻击和占领工具
            {
                "type": "function",
                "function": {
                    "name": "attack_target", 
                    "description": "由指定单位发起对目标单位的攻击",
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
                    "name": "attack",
                    "description": "发起一次攻击",
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
                    "name": "can_attack_target",
                    "description": "检查指定单位是否可以攻击目标单位",
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
                    "name": "occupy",
                    "description": "占领目标",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "occupiers": {"type": "array", "items": {"type": "integer"}, "description": "执行占领的单位ID列表"},
                            "targets": {"type": "array", "items": {"type": "integer"}, "description": "被占领的目标单位ID列表"}
                        },
                        "required": ["occupiers", "targets"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "occupy_units",
                    "description": "占领指定目标单位",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "occupier_ids": {"type": "array", "items": {"type": "integer"}, "description": "发起占领的单位ID列表"},
                            "target_ids": {"type": "array", "items": {"type": "integer"}, "description": "被占领的目标单位ID列表"}
                        },
                        "required": ["occupier_ids", "target_ids"]
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
            },
            {
                "type": "function",
                "function": {
                    "name": "camera_move_dir",
                    "description": "按方向移动镜头",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "direction": {"type": "string", "description": "移动方向"},
                            "distance": {"type": "integer", "description": "移动距离"}
                        },
                        "required": ["direction", "distance"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "move_camera_to_actor",
                    "description": "将镜头移动到指定Actor的位置",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "actor_id": {"type": "integer", "description": "目标Actor的ID"}
                        },
                        "required": ["actor_id"]
                    }
                }
            },
            
            # 其他工具
            {
                "type": "function",
                "function": {
                    "name": "find_path",
                    "description": "为单位寻找路径",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "actor_ids": {"type": "array", "items": {"type": "integer"}, "description": "要移动的单位ID列表"},
                            "dest_x": {"type": "integer", "description": "目标X坐标"},
                            "dest_y": {"type": "integer", "description": "目标Y坐标"},
                            "method": {"type": "string", "description": "寻路方法: '最短路', '左路', '右路'"}
                        },
                        "required": ["actor_ids", "dest_x", "dest_y", "method"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "repair_units",
                    "description": "修复一批单位",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "actor_ids": {"type": "array", "items": {"type": "integer"}, "description": "要修复的单位ID列表"}
                        },
                        "required": ["actor_ids"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "stop_units",
                    "description": "停止一批单位当前行动",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "actor_ids": {"type": "array", "items": {"type": "integer"}, "description": "要停止的单位ID列表"}
                        },
                        "required": ["actor_ids"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "set_rally_point",
                    "description": "为指定建筑设置集结点",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "actor_ids": {"type": "array", "items": {"type": "integer"}, "description": "要设置集结点的建筑ID列表"},
                            "x": {"type": "integer", "description": "集结点X坐标"},
                            "y": {"type": "integer", "description": "集结点Y坐标"}
                        },
                        "required": ["actor_ids", "x", "y"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "visible_query",
                    "description": "查询指定坐标是否在视野中",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "integer", "description": "地图坐标X"},
                            "y": {"type": "integer", "description": "地图坐标Y"}
                        },
                        "required": ["x", "y"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "explorer_query",
                    "description": "查询指定坐标是否已探索",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "integer", "description": "地图坐标X"},
                            "y": {"type": "integer", "description": "地图坐标Y"}
                        },
                        "required": ["x", "y"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_unexplored_nearby_positions",
                    "description": "获取当前位置附近尚未探索的坐标列表",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "map_result": {"type": "object", "description": "map_query返回的地图信息字典"},
                            "current_x": {"type": "integer", "description": "当前X坐标"},
                            "current_y": {"type": "integer", "description": "当前Y坐标"},
                            "max_distance": {"type": "integer", "description": "曼哈顿距离范围"}
                        },
                        "required": ["map_result", "current_x", "current_y", "max_distance"]
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
2. 调用 `produce(unit_type="电厂", quantity=1)` 
3. **关键：检查produce的返回结果**
   - 如果返回 `{"success": false, "error": "..."}`，必须告诉用户具体错误
   - 如果返回 `{"success": true}`，再调用 `query_production_queue("Building")` 验证
4. 根据实际结果回答用户

### 用户要求"展开基地车/部署基地车"：
1. 调用 `get_game_state()` 查看当前状态
2. 调用 `deploy_units()` (无参数)
3. **关键：检查deploy_units的返回结果**
   - 如果返回 `{"success": false, "error": "..."}`，必须告诉用户具体错误
   - 如果返回 `{"success": true}`，再调用 `get_game_state()` 确认是否有新建筑
4. 根据实际结果回答用户

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
- 🎯 "基地车展开成功，建筑已出现在坐标(x,y)"（基于实际验证）
- 🎯 "当前现金15000，无可见单位，需要先展开基地车"（基于实际状态）

## 🔧 工具使用示例
```
用户："建造电厂"
1. get_game_state() → 现金15000，无建筑
2. produce("电厂", 1) → {"success": false, "error": "缺少建造场"}
3. 回答："无法建造电厂，错误：缺少建造场。需要先展开基地车创建建造场。"
```

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
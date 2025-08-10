#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""OpenRA Copilot Agent - MoFA 单节点版本"""

import json
import os
import sys
from typing import Any, Dict

# 添加 OpenRA 路径
sys.path.append(os.getenv('OPENRA_PATH', '/Users/liyao/Code/mofa/OpenCodeAlert/Copilot/openra_ai'))

from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from openra_tools import OpenRATools


class OpenRACopilotAgent:
    """OpenRA Copilot Agent，集成所有游戏控制功能"""
    
    def __init__(self):
        self.tools = OpenRATools()
        self.available_commands = self._get_available_commands()
    
    def _get_available_commands(self) -> Dict[str, str]:
        """获取所有可用命令的映射"""
        return {
            "get_game_state": "获取游戏状态（资源、电力、可见单位）",
            "produce": "生产单位 - produce <单位类型> <数量>",
            "move_units": "移动单位 - move_units <单位ID列表> <x> <y> [是否攻击移动]",
            "camera_move_to": "移动镜头到坐标 - camera_move_to <x> <y>",
            "camera_move_dir": "按方向移动镜头 - camera_move_dir <方向> <距离>",
            "can_produce": "检查是否可生产 - can_produce <单位类型>",
            "query_actor": "查询单位 - query_actor <类型列表> <阵营> <范围> <约束>",
            "select_units": "选择单位 - select_units <类型列表> <阵营> <范围> <约束>",
            "attack_target": "攻击目标 - attack_target <攻击者ID> <目标ID>",
            "deploy_units": "部署单位 - deploy_units <单位ID列表>",
            "repair_units": "修理单位 - repair_units <单位ID列表>",
            "stop_units": "停止单位 - stop_units <单位ID列表>",
            "map_query": "查询地图信息",
            "player_base_info_query": "查询玩家基地信息",
            "screen_info_query": "查询屏幕信息",
            "ensure_can_produce_unit": "确保可以生产单位 - ensure_can_produce_unit <单位名称>",
            "help": "显示帮助信息"
        }
    
    def process_command(self, command_text: str) -> Dict[str, Any]:
        """处理命令并返回结果"""
        try:
            # 解析命令
            parts = command_text.strip().split()
            if not parts:
                return {"error": "空命令"}
            
            command = parts[0]
            args = parts[1:]
            
            # 处理特殊命令
            if command == "help":
                return {"result": self._format_help()}
            
            # 智能命令解析
            result = self._execute_smart_command(command_text)
            return {"result": result}
            
        except Exception as e:
            return {"error": f"命令执行失败: {str(e)}"}
    
    def _execute_smart_command(self, command_text: str) -> Any:
        """智能解析并执行命令"""
        text = command_text.lower()
        
        # 生产相关
        if any(word in text for word in ['生产', '造', '建造']):
            return self._handle_production_command(command_text)
        
        # 移动相关
        elif any(word in text for word in ['移动', '去', '到']):
            return self._handle_move_command(command_text)
        
        # 查询相关
        elif any(word in text for word in ['查询', '看', '状态', '信息']):
            return self._handle_query_command(command_text)
        
        # 攻击相关
        elif any(word in text for word in ['攻击', '打击', '消灭']):
            return self._handle_attack_command(command_text)
        
        # 直接命令匹配
        else:
            return self._handle_direct_command(command_text)
    
    def _handle_production_command(self, command_text: str) -> Any:
        """处理生产命令"""
        text = command_text.lower()
        
        # 提取单位类型
        unit_type = None
        quantity = 1
        
        if '步兵' in text:
            unit_type = '步兵'
        elif '电厂' in text:
            unit_type = '电厂'
        elif '兵营' in text:
            unit_type = '兵营'
        elif '坦克' in text or '重坦' in text:
            unit_type = '重坦'
        elif '矿车' in text:
            unit_type = '矿车'
        elif '基地车' in text or 'mcv' in text:
            unit_type = 'mcv'
        
        # 提取数量
        import re
        numbers = re.findall(r'\d+', command_text)
        if numbers:
            quantity = int(numbers[0])
        
        if unit_type:
            # 先检查是否可以生产
            if self.tools.can_produce(unit_type):
                wait_id = self.tools.produce(unit_type, quantity)
                return f"✅ 开始生产 {quantity} 个 {unit_type}，任务ID: {wait_id}"
            else:
                # 尝试确保依赖
                if self.tools.ensure_can_produce_unit(unit_type):
                    wait_id = self.tools.produce(unit_type, quantity)
                    return f"✅ 依赖已满足，开始生产 {quantity} 个 {unit_type}，任务ID: {wait_id}"
                else:
                    return f"❌ 无法生产 {unit_type}，缺少必要建筑或资源"
        
        return "❌ 无法识别要生产的单位类型"
    
    def _handle_move_command(self, command_text: str) -> Any:
        """处理移动命令"""
        # 简单的移动逻辑，这里可以扩展更复杂的解析
        return "移动命令需要指定具体的单位ID和目标坐标"
    
    def _handle_query_command(self, command_text: str) -> Any:
        """处理查询命令"""
        text = command_text.lower()
        
        if any(word in text for word in ['游戏状态', '当前状态', '状态']):
            return self.tools.get_game_state()
        elif any(word in text for word in ['地图', '地图信息']):
            return self.tools.map_query()
        elif any(word in text for word in ['基地', '基地信息', '资源']):
            return self.tools.player_base_info_query()
        elif any(word in text for word in ['屏幕', '屏幕信息']):
            return self.tools.screen_info_query()
        elif any(word in text for word in ['单位', '部队']):
            # 查询己方单位
            return self.tools.query_actor([], "己方", "all", [])
        
        return "请指定要查询的内容（游戏状态/地图/基地/屏幕/单位）"
    
    def _handle_attack_command(self, command_text: str) -> Any:
        """处理攻击命令"""
        return "攻击命令需要指定攻击者ID和目标ID"
    
    def _handle_direct_command(self, command_text: str) -> Any:
        """处理直接命令"""
        parts = command_text.strip().split()
        command = parts[0] if parts else ""
        
        if command in self.available_commands:
            # 这里可以添加参数解析逻辑
            return f"命令 {command} 需要正确的参数"
        
        return f"未知命令: {command_text}。输入 'help' 查看可用命令。"
    
    def _format_help(self) -> str:
        """格式化帮助信息"""
        help_text = "🎮 OpenRA Copilot Agent 可用命令:\n\n"
        
        help_text += "📝 智能命令（推荐使用）:\n"
        help_text += "  • 生产 X 个步兵\n"
        help_text += "  • 造电厂\n"
        help_text += "  • 查询游戏状态\n"
        help_text += "  • 查询地图信息\n"
        help_text += "  • 查询基地信息\n\n"
        
        help_text += "⚙️ 直接命令:\n"
        for cmd, desc in self.available_commands.items():
            if cmd != "help":
                help_text += f"  • {cmd}: {desc}\n"
        
        return help_text


@run_agent
def run(agent: MofaAgent):
    """Agent 主运行函数"""
    copilot = OpenRACopilotAgent()
    
    # 接收用户命令
    user_input = agent.receive_parameter('user_command')
    
    print(f"🎮 收到命令: {user_input}")
    
    # 处理命令
    result = copilot.process_command(user_input)
    
    # 格式化输出
    if "error" in result:
        output = f"❌ 错误: {result['error']}"
    else:
        if isinstance(result['result'], str):
            output = result['result']
        else:
            output = f"✅ 执行结果:\n{json.dumps(result['result'], ensure_ascii=False, indent=2)}"
    
    print(f"📤 输出结果: {output}")
    
    # 发送输出
    agent.send_output(agent_output_name='copilot_result', agent_result=output)


def main():
    """主函数"""
    agent = MofaAgent(agent_name='openra-copilot-agent')
    run(agent=agent)


if __name__ == "__main__":
    main()
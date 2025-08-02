import os
import sys
sys.path.append(os.getenv('OPENRA_PATH','/Users/chenzi/chenzi/project/github/OpenRA/Copilot/openra_ai'))
from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from OpenRA_Copilot_Library import GameAPI, Location, TargetsQueryParam
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
from dotenv import load_dotenv
from game_executor import GameExecutor
@run_agent
def run(agent: MofaAgent):
    # 0. 等待遥控器发送使能信号
    start_signal = agent.receive_parameter('battlefield-execute-signal')
    load_dotenv('.env')
    if os.getenv('LLM_API_KEY',None) is not None:
        os.environ['OPENAI_API_KEY'] = os.getenv('LLM_API_KEY')

    game_executor = GameExecutor()
    execution_results = game_executor.execute_ai_decisions()
    total_success = 0
    total_attempts = 0
    for category, results in execution_results.get('production_results', {}).items():
        success_count = sum(1 for r in results if r['success'])
        total_count = len(results)
        total_success += success_count
        total_attempts += total_count
    if not execution_results:
        agent.send_output(agent_output_name='battlefield_execute_result', agent_result='❌ 游戏执行失败')
    else:
        agent.send_output(agent_output_name='battlefield_execute_result', agent_result=f"✅ 执行完成！成功率：{total_success}/{total_attempts}")



def main():
    # 创建 agent 实例
    agent = MofaAgent(agent_name='openra-battlefield-execute')
    run(agent=agent)

if __name__ == "__main__":
    main()

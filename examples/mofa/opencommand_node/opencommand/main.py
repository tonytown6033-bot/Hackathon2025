from mofa.agent_build.base.base_agent import MofaAgent, run_agent
import subprocess
import os
import threading

@run_agent
def run(agent: MofaAgent):
    user_query = agent.receive_parameter('query')
    
    # 异步启动OpenRA AI Web界面
    web_ai_path = os.path.join(os.path.dirname(__file__), 'web_ai', 'run.py')
    
    def start_web_server():
        subprocess.run(['python', web_ai_path])
    
    # 在后台线程中启动web服务器
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()
    
    agent.send_output(agent_output_name='hello_world_result', agent_result=f"OpenRA AI Web界面正在后台启动: {user_query}\n访问地址: http://127.0.0.1:5000")

def main():
    agent = MofaAgent(agent_name='opencommand')
    run(agent=agent)

if __name__ == "__main__":
    main()

from game_api import GameAPI, GameAPIError
from models import TargetsQueryParam, Actor
from common.fog_explorer import FogExplorer
import time

def is_actor_alive(api: GameAPI, actor_id: int) -> bool:
    try:
        return api.get_actor_by_id(actor_id) is not None
    except GameAPIError:
        return False

def execute_exploration_phase(api: GameAPI, explorer_yak: Actor):
    print("\n----- 阶段一：开始地图探索（FogExplorer） -----")
    try:
        fog_explorer = FogExplorer()
        unit_query = TargetsQueryParam(type=[explorer_yak.type], faction="friend")
        fog_explorer.explore_map(unit_query, padding=5)
        print(f"已向侦察兵 (ID: {explorer_yak.actor_id}) 下达探索指令，探索开始！")
    except Exception as e:
        print(f"探索阶段发生错误: {e}")
        raise

def execute_attack_phase(api: GameAPI, attack_squad: list[Actor], targets: list[Actor]):
    print("\n----- 阶段二：开始执行精确打击 -----")
    for target in targets:
        print(f"锁定目标：{target.type} (ID: {target.actor_id})")
        can_attack = False
        for yak in attack_squad:
            try:
                if api.can_attack_target(yak, target):
                    api.attack_target(yak, target)
                    can_attack = True
                else:
                    print(f"{yak.actor_id} 无法攻击目标 {target.type} (ID: {target.actor_id})，跳过。")
            except GameAPIError as e:
                print(f"攻击指令失败: {e}")
        if not can_attack:
            print(f"目标 {target.type} (ID: {target.actor_id}) 无法被任何己方单位攻击，跳过。")
            continue
        while is_actor_alive(api, target.actor_id):
            time.sleep(1)
        print(f"目标 {target.type} (ID: {target.actor_id}) 已被摧毁。")

def solve_mission_4(api: GameAPI):
    try:
        all_yaks_query = TargetsQueryParam(type=["yak", "雅克战机"], faction="friend")
        all_yaks = api.query_actor(all_yaks_query)
        # 排除残骸和无效单位
        all_yaks = [u for u in all_yaks if u.type and not u.type.endswith(".husk") and u.type not in ["fenc"]]
        if not all_yaks:
            print("没有可用的雅克战机，任务无法执行。")
            return
        explorer_yak = all_yaks[0]

        # 阶段一：探索
        execute_exploration_phase(api, explorer_yak)

        # 等待侦察结果
        print("正在等待侦察结果...将每5秒检查一次是否发现敌方建筑。")
        enemy_targets = []
        while True:
            all_actors = api.query_actor(TargetsQueryParam())
            # 打印所有单位信息，便于调试
            for a in all_actors:
                print(f"actor_id={a.actor_id}, type={a.type}, faction={getattr(a, 'faction', None)}")
            # 只保留敌方地面目标
            ground_enemies = [
                e for e in all_actors
                if getattr(e, 'faction', None) in ("enemy", "敌方")
                and e.type
                and not e.type.endswith(".husk")
                and e.type not in ["战斗机", "轰炸机"]
            ]
            if ground_enemies:
                print(f"侦察成功！发现 {len(ground_enemies)} 个敌方地面目标。")
                enemy_targets = ground_enemies
                break
            time.sleep(5)

        print("侦察任务完成，命令侦察兵停止当前行动，准备总攻！")
        api.stop([explorer_yak])

        # 阶段二：总攻
        print("集结所有兵力，准备发起总攻...")
        all_yaks = api.query_actor(all_yaks_query)
        if all_yaks:
            execute_attack_phase(api, all_yaks, enemy_targets)
        else:
            print("没有存活的雅克战机，无法发起总攻。")

    except GameAPIError as e:
        print(f"任务执行期间发生致命API错误: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")

if __name__ == '__main__':
    try:
        game_api = GameAPI("localhost")
        print("已连接到游戏服务器，开始执行任务4：空中打击。")
        solve_mission_4(game_api)
    except ConnectionError as e:
        print(f"连接游戏服务器失败: {e}")

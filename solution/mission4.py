from game_api import GameAPI, GameAPIError
from models import TargetsQueryParam, Actor
from common.fog_explorer import FogExplorer
import time

# 定义高威胁单位类型
HIGH_THREAT_TYPES = ["防空车", "防空导弹", "高射炮", "重坦克", "火箭车"]

def is_actor_alive(api: GameAPI, actor_id: int) -> bool:
    try:
        return api.get_actor_by_id(actor_id) is not None
    except GameAPIError:
        return False

def is_map_fully_explored(api: GameAPI) -> bool:
    # 假设有API返回地图探索状态
    map_info = api.query_map()
    return all(row for row in getattr(map_info, "IsExplored", []))

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

def target_priority(actor):
    # 高威胁优先，血量低优先
    threat_score = 1 if actor.type in HIGH_THREAT_TYPES else 0
    hp_score = getattr(actor, "hppercent", 100)
    return (-threat_score, hp_score)  # 高威胁且血量低的排前面

def execute_attack_phase(api: GameAPI, attack_squad: list[Actor]):
    print("\n----- 阶段二：开始执行精确打击 -----")
    while True:
        # 实时刷新敌方单位
        all_actors = api.query_actor(TargetsQueryParam())
        ground_enemies = [
            e for e in all_actors
            if getattr(e, 'faction', None) in ("enemy", "敌方")
            and e.type
            and not e.type.endswith(".husk")
            and e.type not in ["战斗机", "轰炸机"]
            and getattr(e, "hppercent", 1) > 0
        ]
        if not ground_enemies:
            # 只有地图完全探索后才认为敌人被消灭
            if is_map_fully_explored(api):
                print("所有敌方地面目标已被消灭！")
                break
            else:
                print("未发现敌人，可能被战争迷雾遮挡，继续侦查...")
                # 可选：让侦查兵继续巡逻
                time.sleep(2)
                continue

        # 优先级排序
        ground_enemies.sort(key=target_priority)
        # 为每架飞机分配不同目标
        for idx, yak in enumerate(attack_squad):
            if idx >= len(ground_enemies):
                break
            target = ground_enemies[idx]
            try:
                if api.can_attack_target(yak, target):
                    api.attack_target(yak, target)
                    print(f"{yak.actor_id} 攻击 {target.type} (ID: {target.actor_id}, HP: {getattr(target, 'hppercent', '?')})")
                else:
                    print(f"{yak.actor_id} 无法攻击 {target.type} (ID: {target.actor_id})，跳过。")
            except GameAPIError as e:
                print(f"攻击指令失败: {e}")
        time.sleep(2)  # 每2秒刷新一次目标

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
            execute_attack_phase(api, all_yaks)
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

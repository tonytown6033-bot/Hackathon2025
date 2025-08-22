from common.build_system import BuildSystem
from game_api import GameAPI
## 任务目标

if __name__ == "__main__":
    api = GameAPI("localhost", 7445, "zh")
    builder = BuildSystem(api)

    # 任务需求（建筑/单位/是否为建筑）
    mission_steps = [
        ("电厂", 1, True),
        ("战车工厂", 1, True),
        ("步兵", 10, False),
        ("炮兵", 10, False),
        ("矿车", 1, False),
        ("移动防空车", 1, False)
    ]

    builder.run_mission(mission_steps)
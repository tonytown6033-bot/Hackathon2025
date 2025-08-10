from common.build_system import BuildSystem
from game_api import GameAPI

if __name__ == "__main__":
    api = GameAPI("localhost", 7445, "zh")
    builder = BuildSystem(api)

    # 任务需求（建筑/单位/是否为建筑）
    mission_steps = [
        ("电厂", 2, True),
        ("矿场", 1, True),
        ("兵营", 1, True),
        ("步兵", 3, False),
        ("战车工厂", 1, True),
        ("雷达站", 1, True),
        ("防空车", 2, False),
        ("核电厂", 1, True)
    ]

    builder.run_mission(mission_steps)
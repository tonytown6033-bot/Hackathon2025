from game_api import GameAPI
from common.build_system import BuildSystem

if __name__ == "__main__":
    api = GameAPI("localhost", 7445, "zh")
    builder = BuildSystem(api)

    mission_steps = [
        ("电厂", 1, True),
        ("矿场", 1, True),
        ("步兵", 3, False),
        ("战车工厂", 1, True),
        ("防空车", 2, False),
        ("雷达站", 1, True),
        ("核电厂", 1, True)
    ]

    if builder.run_mission(mission_steps):
        print("🎯 Mission 1 完成！")
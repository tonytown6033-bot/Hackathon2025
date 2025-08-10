# mission1_auto_seq.py
import time
from game_api import GameAPI
from models import TargetsQueryParam

# 单位的依赖关系（可根据游戏内容补充）
UNIT_DEPENDENCIES = {
    "步兵": ["兵营"],
    "防空车": ["战车工厂"]
}

def wait_until_can_produce(api: GameAPI, unit_type: str, timeout: float = 30.0) -> bool:
    """循环等待直到可以生产目标单位/建筑"""
    elapsed = 0
    interval = 1.0
    while elapsed < timeout:
        if api.can_produce(unit_type):
            return True
        time.sleep(interval)
        elapsed += interval
    return False

def produce_and_wait(api: GameAPI, unit_type: str, quantity=1, is_building=True):
    """生产并等待完成（自动放置建筑）"""
    print(f"➡️ 尝试生产 {unit_type} x{quantity}")
    if not wait_until_can_produce(api, unit_type):
        print(f"❌ {unit_type} 在限定时间内依然无法生产")
        return False
    api.produce_wait(unit_type, quantity, auto_place_building=is_building)
    print(f"✅ {unit_type} 完成")
    return True

def produce_and_wait_with_deps(api: GameAPI, unit_type: str, quantity=1, is_building=True):
    """带依赖检查的生产函数"""
    # 如果是建筑，先查看前置依赖
    if is_building and unit_type in GameAPI.BUILDING_DEPENDENCIES:
        for dep in GameAPI.BUILDING_DEPENDENCIES[unit_type]:
            exist = api.query_actor(TargetsQueryParam(type=[dep], faction="己方"))
            if not exist:
                print(f"🔍 {unit_type} 需要先建造 {dep}")
                if not produce_and_wait_with_deps(api, dep, 1, is_building=True):
                    return False

    # 如果是单位，检查单位依赖的建筑
    if not is_building and unit_type in UNIT_DEPENDENCIES:
        for dep in UNIT_DEPENDENCIES[unit_type]:
            exist = api.query_actor(TargetsQueryParam(type=[dep], faction="己方"))
            if not exist:
                print(f"🔍 {unit_type} 需要先建造 {dep}")
                if not produce_and_wait_with_deps(api, dep, 1, is_building=True):
                    return False

    return produce_and_wait(api, unit_type, quantity, is_building)

def complete_mission1():
    api = GameAPI("localhost", 7445, "zh")

    # 1. 查找己方基地车并部署
    mcv_list = api.query_actor(TargetsQueryParam(type=["基地车"], faction="己方"))
    if not mcv_list:
        print("❌ 未找到基地车！")
        return
    print("🚚 部署基地车")
    api.deploy_units(mcv_list)

    # 2. 按顺序执行任务目标（会自动补依赖）
    steps = [
        ("电厂", 1, True),
        ("矿场", 1, True),
        ("步兵", 3, False),
        ("战车工厂", 1, True),
        ("防空车", 2, False),
        ("雷达站", 1, True),
        ("核电厂", 1, True)
    ]

    for unit_type, qty, is_building in steps:
        if not produce_and_wait_with_deps(api, unit_type, qty, is_building):
            print(f"⚠️ Mission 1 卡在 {unit_type}，任务无法继续")
            return

    print("🎯 Mission 1 完成！")

if __name__ == "__main__":
    complete_mission1()
import time
from game_api import GameAPI
from models import TargetsQueryParam

# 建筑依赖表
BUILDING_DEPENDENCIES = {
    "电厂": [],
    "兵营": ["电厂"],
    "矿场": ["电厂"],
    "战车工厂": ["矿场"],
    "雷达站": ["矿场"],
    "维修中心": ["战车工厂"],
    "核电厂": ["雷达站"],
    "科技中心": ["战车工厂", "雷达站"],
    "机场": ["雷达站"],
    "防御塔": ["电厂"],
    "防空塔": ["雷达站"]
}

# 单位依赖表
UNIT_DEPENDENCIES = {
    "步兵": ["兵营"],
    "防空车": ["战车工厂"],
}

class BuildSystem:
    def __init__(self, api: GameAPI):
        self.api = api
        self.base_deployed = False
        self.current_have = {}  # type: dict[str, int]

    def log(self, msg: str):
        print(f"[BuildSystem] {msg}")

    def wait_until_can_produce(self, unit_type: str, timeout: float = 30.0) -> bool:
        elapsed = 0
        while elapsed < timeout:
            if self.api.can_produce(unit_type):
                return True
            time.sleep(1.0)
            elapsed += 1.0
        return False

    def queue_build_order(self, unit_type: str, quantity=1, is_building=True):
        """先只下单，不等待完成"""
        if not self.wait_until_can_produce(unit_type):
            self.log(f"❌ {unit_type} 超时未能进入队列")
            return False
        self.api.produce(unit_type, quantity, auto_place_building=is_building)
        self.log(f"⏳ {unit_type} x{quantity} 已加入 {'建筑' if is_building else '单位'} 队列")
        return True

    def wait_for_completion(self):
        """等待生产队列清空（建筑 + 单位）"""
        while True:
            building_queue = self.api.query_production_queue("建筑")
            unit_queue = self.api.query_production_queue("单位")
            if not building_queue and not unit_queue:
                break
            time.sleep(1.0)
        self.log(f"✅ 本轮生产全部完成")

    def ensure_base_deployed(self):
        if self.base_deployed:
            return True

        base_exist = self.api.query_actor(TargetsQueryParam(type=["基地"], faction="己方"))
        if base_exist:
            self.base_deployed = True
            return True

        mcv_list = self.api.query_actor(TargetsQueryParam(type=["基地车"], faction="己方"))
        if not mcv_list:
            self.log("❌ 没有基地车，先造一个")
            if not self.queue_build_order("基地车", 1, is_building=False):
                return False
            self.wait_for_completion()
            mcv_list = self.api.query_actor(TargetsQueryParam(type=["基地车"], faction="己方"))

        self.log("🚚 部署基地车")
        self.api.deploy_units(mcv_list)
        self.base_deployed = True
        return True

    def check_and_prepare_deps(self, unit_type: str, is_building: bool):
        """递归确保依赖存在"""
        if is_building:
            if not self.ensure_base_deployed():
                return False
            for dep in BUILDING_DEPENDENCIES.get(unit_type, []):
                if not self.check_and_prepare_deps(dep, True):
                    return False
                if self.current_have.get(dep, 0) < 1:
                    # 没有依赖建筑，造一个
                    if not self.queue_build_order(dep, 1, True):
                        return False
                    self.current_have[dep] = 1
        else:
            for dep in UNIT_DEPENDENCIES.get(unit_type, []):
                if not self.check_and_prepare_deps(dep, True):
                    return False
                if self.current_have.get(dep, 0) < 1:
                    if not self.queue_build_order(dep, 1, True):
                        return False
                    self.current_have[dep] = 1
        return True

    def init_current_assets(self, steps):
        """查询现有数量"""
        for unit_type, _, _ in steps:
            exist = self.api.query_actor(TargetsQueryParam(type=[unit_type], faction="己方"))
            count = len(exist) if exist else 0
            self.current_have[unit_type] = count
            self.log(f"ℹ️ 已有 {unit_type} x {count}")

    def run_mission(self, steps):
        """并行执行建筑和单位生产"""
        self.init_current_assets(steps)

        for unit_type, qty, is_building in steps:
            have_qty = self.current_have.get(unit_type, 0)
            if have_qty >= qty:
                self.log(f"✅ {unit_type} 已满足 (已有 {have_qty}, 目标 {qty})")
                continue

            if not self.check_and_prepare_deps(unit_type, is_building):
                self.log(f"❌ 依赖准备失败：{unit_type}")
                return False

            need_qty = qty - have_qty
            if self.queue_build_order(unit_type, need_qty, is_building):
                self.current_have[unit_type] = qty  # 预占数量，防止重复下单
            else:
                return False

        # 一次性等待所有建筑与单位完成
        self.wait_for_completion()
        self.log("🎯 所有目标已生产完成")
        return True
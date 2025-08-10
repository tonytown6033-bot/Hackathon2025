# build_system.py
import time
from game_api import GameAPI
from models import TargetsQueryParam

# 单位的额外依赖表（只补单位→建筑关系）
UNIT_DEPENDENCIES = {
    "步兵": ["兵营"],
    "防空车": ["战车工厂"],
    # 这里可继续扩展
}

class BuildSystem:
    def __init__(self, api: GameAPI):
        self.api = api
        self.base_deployed = False

    def log(self, msg: str):
        print(f"[BuildSystem] {msg}")

    def wait_until_can_produce(self, unit_type: str, timeout: float = 30.0) -> bool:
        """循环等待直到可以生产目标单位/建筑"""
        elapsed = 0
        interval = 1.0
        while elapsed < timeout:
            if self.api.can_produce(unit_type):
                return True
            time.sleep(interval)
            elapsed += interval
        return False

    def produce_and_wait(self, unit_type: str, quantity=1, is_building=True):
        """生产并等待完成"""
        self.log(f"➡️ 尝试生产 {unit_type} x{quantity}")
        if not self.wait_until_can_produce(unit_type):
            self.log(f"❌ {unit_type} 在限定时间内仍无法生产")
            return False
        self.api.produce_wait(unit_type, quantity, auto_place_building=is_building)
        self.log(f"✅ {unit_type} 完成")
        return True

    def ensure_base_deployed(self):
        """确保基地车已展开"""
        if self.base_deployed:
            return True

        # 检查有无己方基地
        base_exist = self.api.query_actor(TargetsQueryParam(type=["基地"], faction="己方"))
        if base_exist:
            self.base_deployed = True
            return True

        # 查找己方基地车
        mcv_list = self.api.query_actor(TargetsQueryParam(type=["基地车"], faction="己方"))
        if not mcv_list:
            self.log("❌ 未找到基地车，需要先建造一个")
            if not self.produce_and_wait("基地车", 1, is_building=False):
                return False
            mcv_list = self.api.query_actor(TargetsQueryParam(type=["基地车"], faction="己方"))

        self.log("🚚 部署基地车")
        self.api.deploy_units(mcv_list)
        self.base_deployed = True
        return True

    def produce_with_deps(self, unit_type: str, quantity=1, is_building=True):
        """带依赖检查的生产函数（包括展开基地车）"""
        # 任何建筑都要先展开基地车
        if is_building:
            if not self.ensure_base_deployed():
                return False
            # 检查建筑依赖
            if unit_type in GameAPI.BUILDING_DEPENDENCIES:
                for dep in GameAPI.BUILDING_DEPENDENCIES[unit_type]:
                    exist = self.api.query_actor(TargetsQueryParam(type=[dep], faction="己方"))
                    if not exist:
                        self.log(f"🔍 {unit_type} 需要先建造 {dep}")
                        if not self.produce_with_deps(dep, 1, is_building=True):
                            return False

        # 检查单位依赖的建筑
        if not is_building and unit_type in UNIT_DEPENDENCIES:
            for dep in UNIT_DEPENDENCIES[unit_type]:
                exist = self.api.query_actor(TargetsQueryParam(type=[dep], faction="己方"))
                if not exist:
                    self.log(f"🔍 {unit_type} 需要先建造 {dep}")
                    if not self.produce_with_deps(dep, 1, is_building=True):
                        return False

        return self.produce_and_wait(unit_type, quantity, is_building)

    def run_mission(self, steps):
        """执行任务步骤列表"""
        for unit_type, qty, is_building in steps:
            if not self.produce_with_deps(unit_type, qty, is_building):
                self.log(f"⚠️ 任务卡在 {unit_type}，无法继续")
                return False
        return True
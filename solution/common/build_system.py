import time
from game_api import GameAPI, GameAPIError
from models import TargetsQueryParam

# 建筑依赖表 (Building Dependencies)
# 描述了建造一个新建筑需要预先拥有哪些建筑。
BUILDING_DEPENDENCIES = {
    # --- 基础建筑 (Tier 1) ---
    "电厂": [],              # Power Plant: 基础，无依赖
    "兵营": ["电厂"],          # Barracks: 需要电力
    "矿场": ["电厂"],          # Ore Refinery: 需要电力
    "防御塔": ["电厂"],        # Defensive Turret: 需要电力

    # --- 进阶建筑 (Tier 2) ---
    "战车工厂": ["矿场"],      # War Factory: 需要矿场支持 (通常代表经济基础)
    "雷达站": ["矿场"],        # Radar Station: 需要矿场支持
    "船坞": ["矿场"],          # Shipyard: 新增，需要经济基础才能发展海军

    # --- 高级建筑 (Tier 3) ---
    "维修中心": ["战车工厂"],  # Repair Bay: 需要有车辆单位才能维修
    "科技中心": ["战车工厂", "雷达站"], # Tech Center: 解锁高科技单位的关键
    "机场": ["雷达站"],        # Airfield: 需要雷达支持
    "防空塔": ["雷达站"],      # Anti-Air Turret: 需要雷达来探测空中单位

    # --- 顶级建筑 (Tier 4 / Superweapons) ---
    "核电厂": ["科技中心"],    # Nuclear Power Plant: 作为高级能源，需要科技中心解锁
    "高级防御塔": ["科技中心"],# Advanced Turret: 新增，更强的防御需要科技支持
    "超级武器": ["科技中心", "雷达站"] # Superweapon: 新增，终极武器需要最高科技和雷达定位
}

# 单位依赖表 (Unit Dependencies)
# 描述了训练/制造一个单位需要哪些建筑。
UNIT_DEPENDENCIES = {
    # --- 兵营单位 ---
    "步兵": ["兵营"],          # Infantry
    "工程师": ["兵营"],        # Engineer: 新增，用于占领建筑
    "警犬": ["兵营"],          # Attack Dog: 新增，快速的侦察和反步兵单位
    "火箭兵": ["兵营", "雷达站"], # Rocket Soldier: 新增，需要雷达支持才能生产的反坦克步兵

    # --- 战车工厂单位 ---
    "采矿车": ["战车工厂", "矿场"], # Ore Miner: 新增，需要矿场配合才能生产
    "轻型坦克": ["战车工厂"],      # Light Tank: 新增，基础作战车辆
    "重型坦克": ["战车工厂", "科技中心"], # Heavy Tank: 新增，需要科技中心解锁的强大单位
    "防空车": ["战车工厂"],      # Anti-Air Vehicle
    "自行火炮": ["战车工厂", "雷达站"], # Artillery: 新增，需要雷达提供远程坐标

    # --- 机场单位 ---
    "战斗机": ["机场"],        # Fighter Jet: 新增，用于夺取制空权
    "轰炸机": ["机场", "科技中心"], # Bomber: 新增，需要科技中心解锁的对地攻击机

    # --- 船坞单位 ---
    "驱逐舰": ["船坞"],        # Destroyer: 新增，标准的海上作战单位
    "潜艇": ["船坞", "雷达站"]  # Submarine: 新增，需要雷达站（声纳）技术支持
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
            # 建筑队列
            building_queue = self.api.query_production_queue("Building")

            # 尝试查询所有单位队列，如果失败则视为空列表
            unit_queues = []
            for unit_type in ["Infantry", "Vehicle", "Aircraft", "Naval"]:
                try:
                    queue = self.api.query_production_queue(unit_type)
                    if queue:
                        unit_queues.append(queue)
                except GameAPIError as e:
                    if e.code == "COMMAND_EXECUTION_ERROR":
                        self.log(f"⚠️ {unit_type} 生产队列查询失败，可能不存在。")
                        # 忽略此错误并继续
                        continue
                    else:
                        # 重新抛出其他类型的错误
                        raise e

            # 检查所有队列是否都已清空
            if not building_queue and not unit_queues:
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
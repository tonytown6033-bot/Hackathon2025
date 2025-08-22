import time
from game_api import GameAPI, GameAPIError
from models import Location, TargetsQueryParam, MapQueryResult, Actor

# 全局变量，用于存储扫描到的敌方单位
discovered_enemy_units: list[Actor] = []

class FogExplorer:
    """
    一个用于探索游戏地图战争迷雾的通用类。

    该类封装了连接游戏、查找探索单位、生成系统性探索路径
    以及命令单位执行探索任务的逻辑。
    """

    def __init__(self, host: str = "localhost"):
        """
        初始化FogExplorer并连接到游戏服务器。

        Args:
            host (str): 游戏服务器的主机地址。

        Raises:
            ConnectionError: 如果无法连接到游戏服务器。
        """
        print("正在初始化 FogExplorer...")
        if not GameAPI.is_server_running():
            raise ConnectionError("错误: 游戏服务器未运行。请启动游戏和任务。")
        
        self.api = GameAPI(host)
        self.instance_enemy_units: list[Actor] = []
        print("成功连接到游戏服务器。")

    def get_enemy_units(self) -> list[Actor]:
        """
        查询所有可见的敌方单位，并更新全局和实例的单位列表。

        Returns:
            list[Actor]: 当前可见的敌方单位列表。
        
        Raises:
            GameAPIError: 如果在API调用期间发生错误。
        """
        global discovered_enemy_units
        print("正在查询所有可见的敌方单位...")
        try:
            enemy_query = TargetsQueryParam(faction="enemy")
            enemies = self.api.query_actor(enemy_query)
            
            discovered_enemy_units = enemies
            self.instance_enemy_units = enemies
            
            print(f"查询完成，发现了 {len(enemies)} 个敌方单位。")
            return enemies
        except GameAPIError as e:
            print(f"查询敌方单位时发生错误: {e}")
            raise

    def _generate_serpentine_path(self, map_width: int, map_height: int, padding: int, vertical_step: int) -> list[Location]:
        """
        生成一个蛇形的路径点列表以覆盖整个地图。
        """
        path_waypoints = []
        is_moving_right = True

        for y in range(padding, map_height - padding, vertical_step):
            if is_moving_right:
                path_waypoints.append(Location(padding, y))
                path_waypoints.append(Location(map_width - padding, y))
            else:
                path_waypoints.append(Location(map_width - padding, y))
                path_waypoints.append(Location(padding, y))
            
            is_moving_right = not is_moving_right
        
        print(f"已生成包含 {len(path_waypoints)} 个航点的探索路径。")
        return path_waypoints

    def explore_map(self, unit_query: TargetsQueryParam, padding: int = 15, vertical_step: int = 15):
        """
        使用指定的单位开始探索地图。

        Args:
            unit_query (TargetsQueryParam): 用于查询探索单位的参数。
            padding (int, optional): 路径与地图边缘的距离。默认为 15。
            vertical_step (int, optional): 每个水平通道之间的垂直距离。默认为 15。

        Raises:
            ValueError: 如果根据查询参数找不到指定的单位。
            GameAPIError: 如果在API调用期间发生错误。
        """
        # 1. 查找探索单位
        print(f"正在搜索探索单位 (查询条件: {unit_query})...")
        explorer_units = self.api.query_actor(unit_query)

        if not explorer_units:
            raise ValueError(f"错误: 未找到与查询匹配的单位 {unit_query}。")
        
        explorer_unit = explorer_units[0]
        # 根据 models.py 中 Actor 的定义，其ID属性为 'id'
        print(f"找到探索单位 '{explorer_unit.type}' (ID: {explorer_unit.actor_id})。")

        # 2. 获取地图尺寸
        print("正在查询地图尺寸...")
        map_info: MapQueryResult = self.api.map_query()
        print(f"地图尺寸为 {map_info.MapWidth}x{map_info.MapHeight}。")

        # 3. 生成探索路径
        path = self._generate_serpentine_path(map_info.MapWidth, map_info.MapHeight, padding, vertical_step)

        # 4. 命令单位移动
        print(f"向单位 {explorer_unit.actor_id} 发出移动指令...")
        # 使用正确的 API 函数 move_units_by_path，并传递一个包含 Actor 对象的列表
        self.api.move_units_by_path([explorer_unit], path)
        print("指令已成功发出。单位现在将开始探索地图。")   
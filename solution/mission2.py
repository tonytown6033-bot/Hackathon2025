from common.fog_explorer import FogExplorer
from game_api import GameAPI, GameAPIError
from models import Location, TargetsQueryParam, MapQueryResult, Actor


def main():
    """主函数，演示如何使用 FogExplorer 类。"""
    try:
        # 初始化探索器
        explorer = FogExplorer()

        # 定义要用于探索的单位类型（例如，雅克战机）
        yak_query = TargetsQueryParam(type=['雅克战机'], faction='自己')

        # 开始探索 - 【关键改动】
        # 我们在此处明确传入原始脚本中验证过的参数值，
        # 而不是使用类中的默认值。
        print("使用原版脚本验证过的参数 (padding=5) 来规划路径...")
        explorer.explore_map(yak_query, padding=5, vertical_step=15)

        print("\n脚本任务已分派。请在游戏中监控探索进程。")

    except (ConnectionError, ValueError, GameAPIError) as e:
        print(f"\n操作失败: {e}")
    except Exception as e:
        print(f"\n发生意外错误: {e}")


if __name__ == "__main__":
    main()
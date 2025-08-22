import time
from game_api import GameAPI, GameAPIError
from models import Location, TargetsQueryParam, MapQueryResult

def solve_mission_02():
    """
    Solves Mission 02: Fog of War.

    Strategy:
    1. Find the player's Yak fighter.
    2. Query the map dimensions.
    3. Generate a serpentine path with waypoints to cover the entire map.
    4. Command the Yak to follow this path using `move_units_by_path`.
    """
    try:
        # 1. Initialize the API
        # Check if the server is running before attempting to connect.
        if not GameAPI.is_server_running():
            print("Error: Game server is not running. Please start the game and the mission.")
            return

        api = GameAPI("localhost")
        print("Successfully connected to the game server.")

        # 2. Find the Yak fighter
        print("Searching for the Yak fighter...")
        yak_actors = api.query_actor(TargetsQueryParam(type=['雅克战机'], faction='自己'))

        if not yak_actors:
            print("Error: Yak fighter ('雅克战机') not found. Make sure the mission is active.")
            return
        
        yak = yak_actors[0]
        print(f"Yak fighter found with ID {yak.actor_id} at position ({yak.position.x}, {yak.position.y}).")

        # 3. Get map dimensions to plan the exploration path
        print("Querying map dimensions...")
        map_info: MapQueryResult = api.map_query()
        map_width = map_info.MapWidth
        map_height = map_info.MapHeight
        print(f"Map dimensions are {map_width}x{map_height}.")

        # 4. Generate a serpentine path to efficiently explore the map
        path_waypoints = []
        padding = 5  # Distance to keep from the map edges
        vertical_step = 15 # The vertical distance between each horizontal pass
        is_moving_right = True

        for y in range(padding, map_height - padding, vertical_step):
            if is_moving_right:
                # Add waypoints for a left-to-right pass
                path_waypoints.append(Location(padding, y))
                path_waypoints.append(Location(map_width - padding, y))
            else:
                # Add waypoints for a right-to-left pass
                path_waypoints.append(Location(map_width - padding, y))
                path_waypoints.append(Location(padding, y))
            
            # Reverse direction for the next pass
            is_moving_right = not is_moving_right
        
        print(f"Generated an exploration path with {len(path_waypoints)} waypoints.")

        # 5. Command the Yak to move along the generated path
        print("Issuing move command to the Yak to begin exploration...")
        api.move_units_by_path([yak], path_waypoints)
        print("Command issued successfully. The Yak will now explore the map.")
        print("The script has completed its task. Monitor the game to see the result.")

    except GameAPIError as e:
        print(f"A Game API error occurred: [{e.code}] {e.message}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    solve_mission_02()
import time
from game_api import GameAPI, GameAPIError
from models import Location, TargetsQueryParam

def solve_mission_03():
    """
    Solves Mission 03: Advanced Building.

    Strategy:
    1. Deploy the initial MCV to start the base.
    2. Use the 'ensure_can_build_wait' helper function to automatically build
       the required structures (Power Plant, Barracks, Ore Refinery, War Factory)
       by handling all dependencies.
    3. Once buildings are complete, queue all required units using the non-blocking
       'produce' command to build them in parallel.
    """
    try:
        # Initialize the API connection
        api = GameAPI("localhost")
        print("Successfully connected to the game server.")

        # 1. Deploy the MCV to create the Construction Yard
        print("Deploying MCV...")
        api.deploy_mcv_and_wait() # This helper function finds and deploys the player's MCV
        print("MCV deployed successfully.")

        # 2. Build the Barracks. The helper function will automatically build
        # the required Power Plant first.
        print("Constructing Barracks (and its dependency, the Power Plant)...")
        # ensure_can_build_wait checks for dependencies and builds them if missing
        api.ensure_can_build_wait("兵营") 
        print("Barracks and Power Plant are complete.")

        # 3. Build the War Factory. The helper function will automatically build
        # the required Ore Refinery first.
        print("Constructing War Factory (and its dependency, the Ore Refinery)...")
        api.ensure_can_build_wait("车间")
        print("War Factory and Ore Refinery are complete.")

        # 4. All necessary buildings are up. Start queuing all required units.
        # We use the non-blocking 'produce' function to start production in parallel.
        print("All buildings constructed. Starting unit production...")
        
        # Queue units from the Barracks
        api.produce("步兵", 10)
        print("Queued 10 Infantry.")
        
        # "Artillery" (炮兵) is not in the dependency list; "火箭兵" (Rocket Soldier) is the closest equivalent.
        api.produce("火箭兵", 10)
        print("Queued 10 Rocket Soldiers (as Artillery).")
        
        # Queue units from the War Factory
        api.produce("矿车", 1)
        print("Queued 1 Ore Truck.")
        
        api.produce("防空车", 1)
        print("Queued 1 Mobile Flak.")
        
        print("\nAll production commands have been issued.")
        print("The mission will be completed once all units are produced.")

    except GameAPIError as e:
        print(f"A Game API error occurred: [{e.code}] {e.message}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Check if the server is running before starting the script
    if GameAPI.is_server_running():
        solve_mission_03()
    else:
        print("Error: Game server is not running. Please start the game and Mission 3.")
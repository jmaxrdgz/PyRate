import requests
import time
import random
import math

API_URL = "http://127.0.0.1:8000"
ACTIONS = ["accelerate", "decelerate", "turn_left", "turn_right", "fire"]


def get_player_status():
    """
    Retrieve the player's status from the API.
    Returns a dictionary with player data, or an empty dict on error.
    """
    try:
        response = requests.get(f"{API_URL}/player/status")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error retrieving player status: {e}")
        return {}


def get_enemies_status():
    """
    Retrieve the list of enemies' statuses from the API.
    Returns a list of enemy dicts, or an empty list on error.
    """
    try:
        response = requests.get(f"{API_URL}/enemies/status")
        response.raise_for_status()
        return response.json().get("enemies", [])
    except Exception as e:
        print(f"Error retrieving enemies status: {e}")
        return []


def send_command(action, side="left"):
    """
    Send a control command for the player to the API.
    action: one of ACTIONS, side: 'left' or 'right'.
    Returns the API response JSON, or a dict with status 'error'.
    """
    payload = {"action": action, "side": side}
    try:
        response = requests.post(f"{API_URL}/player/command", json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error sending command '{action}': {e}")
        return {"status": "error"}


def update_game():
    """
    Trigger a game update on the server.
    """
    try:
        response = requests.post(f"{API_URL}/game/update")
        response.raise_for_status()
    except Exception as e:
        print(f"Error updating game: {e}")


def set_control_mode(mode):
    """
    Set the control mode (e.g., 'api') on the server.
    Returns the API response JSON, or a dict with status 'error'.
    """
    payload = {"mode": mode}
    try:
        response = requests.post(f"{API_URL}/game/control", json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error setting control mode to '{mode}': {e}")
        return {"status": "error"}


def dummy_decision():
    """
    Return a random action; fires if any enemy is within 200 units.
    """
    enemies = get_enemies_status()
    player = get_player_status()

    if not player:
        return random.choice(ACTIONS)

    player_x = player.get('x')
    player_y = player.get('y')
    for enemy in enemies:
        dx = enemy.get('x', 0) - player_x
        dy = enemy.get('y', 0) - player_y
        dist = math.hypot(dx, dy)
        if dist < 200:
            return "fire"

    return random.choice(["turn_left", "turn_right", "accelerate", "decelerate"])


def run():
    """
    Main loop: set control mode to 'api' and repeatedly choose and send commands.
    """
    set_control_mode("api")
    while True:
        action = dummy_decision()
        print(f"Sending action: {action}")
        send_command(action)
        update_game()
        time.sleep(0.2)


if __name__ == "__main__":
    run()

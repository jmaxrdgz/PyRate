import requests
import time
import random

API_URL = "http://127.0.0.1:8000"
ACTIONS = ["accelerate", "decelerate", "turn_left", "turn_right", "fire"]

def get_player_status():
    try:
        response = requests.get(f"{API_URL}/player/status")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erreur lors de la récupération du statut joueur: {e}")
        return {}

def get_enemies_status():
    try:
        response = requests.get(f"{API_URL}/enemies/status")
        response.raise_for_status()
        return response.json().get("enemies", [])
    except Exception as e:
        print(f"Erreur lors de la récupération des ennemis: {e}")
        return []

def send_command(action, side="left"):
    payload = {"action": action, "side": side}
    try:
        response = requests.post(f"{API_URL}/player/command", json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erreur lors de l'envoi de la commande '{action}': {e}")
        return {"status": "error"}

def update_game():
    try:
        response = requests.post(f"{API_URL}/game/update")
        response.raise_for_status()
    except Exception as e:
        print(f"Erreur lors de la mise à jour du jeu: {e}")

def set_control_mode(mode):
    payload = {"mode": mode}
    try:
        response = requests.post(f"{API_URL}/game/control", json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erreur lors du changement de mode de contrôle: {e}")
        return {"status": "error"}

def dummy_decision():
    """Renvoie une action aléatoire, tire si un ennemi est proche."""
    enemies = get_enemies_status()
    player = get_player_status()

    if not player:
        return random.choice(ACTIONS)

    for enemy in enemies:
        dx = enemy['x'] - player['x']
        dy = enemy['y'] - player['y']
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < 200:
            return "fire"

    return random.choice(["turn_left", "turn_right", "accelerate", "decelerate"])

def run():
    set_control_mode("api")
    while True:
        action = dummy_decision()
        print(f"Sending action: {action}")
        send_command(action)
        update_game()
        time.sleep(0.2)

if __name__ == "__main__":
    run()
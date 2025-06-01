import requests
import random
import math
import time

API_URL = "http://127.0.0.1:8000"
PLAYER_ID = 0  # indice du vaisseau que cet agent contrôle

def set_control_mode(mode):
    resp = requests.post(f"{API_URL}/game/control", json={"mode": mode})
    resp.raise_for_status()

def get_player_status():
    url = f"{API_URL}/players/{PLAYER_ID}/status"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def get_sensor_status():
    resp = requests.get(f"{API_URL}/players/{PLAYER_ID}/sensor")
    resp.raise_for_status()
    return resp.json().get("nearby_ships", [])

def send_command(action, side="left"):
    url = f"{API_URL}/players/{PLAYER_ID}/command"
    # Pydantic Command model always requires "side", so we include it even if not firing.
    if action == "fire":
        payload = {"action": action, "side": side}
    else:
        payload = {"action": action, "side": "left"}
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    return resp.json()

def update_game():
    # avance d'un tick ; le serveur gère le clock.tick(FPS)
    resp = requests.post(f"{API_URL}/game/update")
    resp.raise_for_status()

def dummy_decision():
    player = get_player_status()
    enemies = get_sensor_status()
    speed = player["speed"]

    # Tir si un ennemi non-friendly est très proche (< 200)
    for e in enemies:
        if e["entity"] != "friendly" and e["distance"] < 200:
            return ("fire", random.choice(["left", "right"]))

    # Si on est quasiment arrêté, accélère
    if speed <= 0.1:
        return ("accelerate", None)

    # Sinon choix aléatoire :
    #  - 50% accelerate
    #  - 20% tourner (turn_left ou turn_right)
    #  - 10% décélérer
    #  - 20% aucun ordre
    r = random.random()
    if r < 0.5:
        return ("accelerate", None)
    elif r < 0.7:
        return (random.choice(["turn_left", "turn_right"]), None)
    elif r < 0.8:
        return ("decelerate", None)
    else:
        return (None, None)

def run():
    # passe en mode API
    set_control_mode("api")

    # boucle principale
    while True:
        action, side = dummy_decision()
        if action:
            if action == "fire":
                send_command(action, side)
            else:
                send_command(action)
        # Petite pause pour éviter un spam trop élevé
        time.sleep(0.001)

if __name__ == "__main__":
    run()

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

def get_enemies_status():
    resp = requests.get(f"{API_URL}/enemies/status")
    resp.raise_for_status()
    return resp.json().get("enemies", [])

def send_command(action, side="left"):
    url = f"{API_URL}/players/{PLAYER_ID}/command"
    payload = {"action": action, "side": side}
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    return resp.json()

def update_game():
    # avance d'un tick ; le serveur gère le clock.tick(FPS)
    resp = requests.post(f"{API_URL}/game/update")
    resp.raise_for_status()

def dummy_decision():
    player = get_player_status()
    enemies = get_enemies_status()
    px, py, speed = player["x"], player["y"], player["speed"]

    # Tir si ennemi très proche
    for e in enemies:
        if math.hypot(e["x"] - px, e["y"] - py) < 200:
            return ("fire", random.choice(["left", "right"]))

    # Si on est quasiment arrêté, accélère
    if speed <= 0.1:
        return ("accelerate", None)

    # Sinon choix aléatoire :
    # - 50% accelerate
    # - 20% tourner (possible car speed>0.1)
    # - 10% décélérer
    # - 20% aucun ordre (coasting)
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
            if side:
                send_command(action, side)
            else:
                send_command(action)
        # sinon on lâche les commandes pour la friction
        # pas de sleep pour ne pas contredire clock.tick(FPS) du serveur
        # mais on peut ajouter un micro‑délai pour éviter spam trop élevé :
        time.sleep(0.001)

if __name__ == "__main__":
    run()

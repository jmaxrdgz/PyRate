# pyrate/engine/input.py
import pygame

PLAYER_CONTROL = "human"  # Valeurs possibles: "human" ou "bot"

def set_player_control(control_type):
    global PLAYER_CONTROL
    if control_type in ["human", "bot"]:
        PLAYER_CONTROL = control_type
        print(f"[Input] Player control set to: {PLAYER_CONTROL}")
    else:
        print(f"[Input] Warning: Unknown control type '{control_type}'. Control remains '{PLAYER_CONTROL}'.")

def handle_input(ship):
    """
    Allows to control a ship using the keyboard (Z, Q, S, D) when PLAYER_CONTROL is "human".
    """
    global PLAYER_CONTROL
    if PLAYER_CONTROL == "human":
        keys = pygame.key.get_pressed()

        # Displacement
        if keys[pygame.K_z]:
            ship.accelerate()
        if keys[pygame.K_s]:
            ship.decelerate()
        if keys[pygame.K_q]:
            ship.turn_left()
        if keys[pygame.K_d]:
            ship.turn_right()

        # Shooting
        if keys[pygame.K_LEFT]:
            ship.fire("left")
        if keys[pygame.K_RIGHT]:
            ship.fire("right")
    # Si PLAYER_CONTROL est "bot", cette fonction ne fera rien.
    # Le contrôle du bot sera géré par l'API.
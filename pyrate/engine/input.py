# pyrate/engine/input.py
import pygame
from pyrate.settings import INPUT_MODE


def set_player_control(control_type):
    global INPUT_MODE
    if control_type in ["keyboard", "api"]:
        PLAYER_CONTROL = control_type
        print(f"[Input] Player controle set to: {PLAYER_CONTROL}")
    else:
        print(f"[Input] Warning: Unknown controle type '{control_type}'")

def handle_input(ship):
    """
    Allows to control a ship using the keyboard (Z, Q, S, D) when INPUT_MODE is "keyboard".
    """
    if INPUT_MODE == "keyboard":
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
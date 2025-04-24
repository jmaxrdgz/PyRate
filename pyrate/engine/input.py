# pyrate/engine/input.py
import pygame

def handle_input(ship):
    """
    Allows to control a ship using the keyboard (Z, Q, S, D).
    """
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
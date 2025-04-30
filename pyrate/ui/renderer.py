# pyrate/ui/renderer.py
import pygame
import math
from pyrate.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, DEBUG_MODE
from pyrate.engine.game import Game


def run_game():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    game = Game()

    # semi-transparent overlay for debug drawings
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    running = True
    debug = DEBUG_MODE

    while running:
        # Close window if x is pressed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        #===================#
        #   ENGINE UPDATE   #
        #===================#
        game.update()

        #============#
        #   RENDER   #
        #============#
        screen.fill("blue")
        if debug:
            overlay.fill((0, 0, 0, 0))  # clear debug overlay

        # Draw player ship (with debug hitbox)
        draw_ship(screen, game.player_ship, role='player', debug=debug)

        # Draw enemies and optional debug agro zones
        for enemy in game.enemies:
            if debug:
                # agro zone
                pygame.draw.circle(overlay, (0, 255, 0, 40), (int(enemy.x), int(enemy.y)), enemy.agro_radius)
            draw_ship(screen, enemy, role='enemy', debug=debug)

        # Draw projectiles (and debug hitbox as circle)
        for projectile in game.projectiles:
            # actual projectile
            pygame.draw.circle(screen, (0, 0, 0), (int(projectile.x), int(projectile.y)), projectile.radius)
            if debug:
                # hitbox circle
                pygame.draw.circle(overlay, (255, 255, 255, 80), (int(projectile.x), int(projectile.y)), projectile.radius, width=1)

        # Blit debug overlay
        if debug:
            screen.blit(overlay, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


def draw_ship(screen, ship, role, debug=False):
    # Draw the ship as a triangle
    if role == 'player':
        color = (0, 255, 0)
    elif role == 'enemy':
        color = (255, 0, 0)
    points = [
        (ship.x + math.cos(math.radians(ship.angle)) * 15,
         ship.y + math.sin(math.radians(ship.angle)) * 15),
        (ship.x + math.cos(math.radians(ship.angle + 140)) * 15,
         ship.y + math.sin(math.radians(ship.angle + 140)) * 15),
        (ship.x + math.cos(math.radians(ship.angle - 140)) * 15,
         ship.y + math.sin(math.radians(ship.angle - 140)) * 15),
    ]
    pygame.draw.polygon(screen, color, points)

    if debug:
        # draw hitbox polygon
        hitbox = ship.get_hitbox()
        pygame.draw.polygon(overlay if False else screen, (255, 255, 255), hitbox, width=1)

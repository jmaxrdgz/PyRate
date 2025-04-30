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

    # Load assets
    # Sea texture (tileable)
    # sea_tex = pygame.image.load("assets/images/sea_tile.png").convert()
    # Player and enemy sprites
    player_img = pygame.image.load("assets/images/player_full_health.png").convert_alpha()
    enemy_img = pygame.image.load("assets/images/enemy_full_health.png").convert_alpha()
    # Cannonball sprite
    # cannon_img = pygame.image.load("assets/images/cannonball.png").convert_alpha()

    # semi-transparent overlay for debug drawings
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    running = True
    debug = DEBUG_MODE

    # Pre-tile sea background once into a surface
    sea_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    # tex_w, tex_h = sea_tex.get_width(), sea_tex.get_height()
    # for x in range(0, SCREEN_WIDTH, tex_w):
    #     for y in range(0, SCREEN_HEIGHT, tex_h):
    #         sea_bg.blit(sea_tex, (x, y))

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
        # draw tiled sea background
        screen.blit(sea_bg, (0, 0))
        if debug:
            overlay.fill((0, 0, 0, 0))  # clear debug overlay

        # Draw player ship
        draw_entity(screen, game.player_ship, player_img, debug)

        # Draw enemies and agro zones
        for enemy in game.enemies:
            if debug:
                pygame.draw.circle(overlay, (0,255,0,40), (int(enemy.x), int(enemy.y)), enemy.agro_radius)
            draw_entity(screen, enemy, enemy_img, debug)

        # Draw projectiles
        for projectile in game.projectiles:
            # blit rotated cannonball
            # draw_rotated(screen, cannon_img, projectile.x, projectile.y, projectile.angle)
            if debug:
                # hitbox circle
                pygame.draw.circle(overlay, (255,255,255,80), (int(projectile.x), int(projectile.y)), projectile.radius, width=1)

        # Blit debug overlay
        if debug:
            screen.blit(overlay, (0,0))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


def draw_entity(screen, entity, sprite, debug=False):
    """
    Draws an entity by blitting its rotated sprite centered on (entity.x, entity.y).
    """
    draw_rotated(screen, sprite, entity.x, entity.y, entity.angle)
    if debug:
        # draw hitbox polygon
        hitbox = entity.get_hitbox()
        pygame.draw.polygon(screen, (255,255,255), hitbox, width=1)


def draw_rotated(screen, image, x, y, angle):
    """
    Rotate an image and blit it centered at (x,y).
    """
    rotated = pygame.transform.rotate(image, -angle + 90)
    rect = rotated.get_rect(center=(int(x), int(y)))
    screen.blit(rotated, rect)

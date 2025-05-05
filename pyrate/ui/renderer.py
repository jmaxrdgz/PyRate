# pyrate/ui/renderer.py
import pygame
import math
from pyrate.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, DEBUG_MODE
from pyrate.engine.game import Game
from pyrate.ui.animation import AnimatedEffect


def run_game():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    game = Game()

    # Load assets
    sea_tex = pygame.image.load("assets/images/sea_tile.png").convert()
    splash_frames = load_frames(['assets/images/splash1.png', 'assets/images/splash2.png', 'assets/images/splash3.png', 'assets/images/splash4.png'])
    explosion_frames = load_frames(['assets/images/explosion1.png', 'assets/images/explosion2.png', 'assets/images/explosion3.png'])
    player_frames = load_frames(['assets/images/player_full.png', 'assets/images/player_damaged1.png', 'assets/images/player_damaged2.png'])
    enemy_frames = load_frames(['assets/images/enemy_full.png', 'assets/images/enemy_damaged1.png', 'assets/images/enemy_damaged2.png'])

    # semi-transparent overlay for debug drawings
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    running = True
    debug = DEBUG_MODE

    # Pre-tile sea background once into a surface
    sea_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    tex_w, tex_h = sea_tex.get_width(), sea_tex.get_height()
    for x in range(0, SCREEN_WIDTH, tex_w):
        for y in range(0, SCREEN_HEIGHT, tex_h):
            sea_bg.blit(sea_tex, (x, y))

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
        draw_ship(screen, game.player_ship, player_frames, debug)

        # Draw enemies and agro zones
        for enemy in game.enemies:
            if debug:
                pygame.draw.circle(overlay, (0,255,0,40), (int(enemy.x), int(enemy.y)), enemy.agro_radius)
            draw_ship(screen, enemy, enemy_frames, debug)

        # Draw projectiles
        for projectile in game.projectiles:
            pygame.draw.circle(screen, (0, 0, 0), (int(projectile.x), int(projectile.y)), projectile.radius)
            if debug:
                # hitbox circle
                pygame.draw.circle(overlay, (255,255,255,80), (int(projectile.x), int(projectile.y)), projectile.radius, width=1)

        # Draw animated effects
        active_effects = []

        for impact in game.impacts:
            if impact[1] == "hit":
                # Draw explosion effect
                explosion_effect = AnimatedEffect(explosion_frames, (impact[0].x, impact[0].y), duration=1500)
                active_effects.append(explosion_effect)
            elif impact[1] == "miss":
                # Draw splash effect
                splash_effect = AnimatedEffect(splash_frames, (impact[0].x, impact[0].y), duration=1500)
                active_effects.append(splash_effect)
            game.impacts.pop(0) # Remove the impact after processing

        for effect in active_effects[:]:
            effect.update()
            if effect.finished:
                active_effects.remove(effect)
        for effect in active_effects:
            effect.draw(screen)

        # Blit debug overlay
        if debug:
            screen.blit(overlay, (0,0))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


def draw_ship(screen, ship, frames, debug=False):
    if ship.health >= 50 and ship.is_living:
        sprite = frames[0]
    if ship.health > 20 and ship.is_living:
        sprite = frames[1]
    if ship.health <= 20 and ship.is_living:
        sprite = frames[2]
    draw_entity(screen, ship, sprite, debug)

def draw_entity(screen, entity, sprite, debug=False):
    """
    Draws an entity by blitting its rotated sprite centered on (entity.x, entity.y).
    """
    draw_rotated(screen, sprite, entity.x, entity.y, entity.angle)
    if debug:
        # draw hitbox polygon
        hitbox = entity.get_hitbox()
        pygame.draw.polygon(screen, (255,255,255), hitbox, width=1)


# TODO: Add size factor choice (for explosions)
def draw_rotated(screen, image, x, y, angle):
    """
    Rotate an image and blit it centered at (x,y).
    """
    rotated = pygame.transform.rotate(image, -angle + 90)
    rect = rotated.get_rect(center=(int(x), int(y)))
    screen.blit(rotated, rect)

def load_frames(path_list):
    """
    Load frames in a list.
    """
    try:
        frames = [pygame.image.load(path).convert_alpha() for path in path_list]
    except pygame.error as e:
        print(f"Error loading frames: {e}")
        frames = []
    return frames

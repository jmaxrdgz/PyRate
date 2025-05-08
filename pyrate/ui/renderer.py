# pyrate/ui/renderer.py
import pygame
import math
from pyrate.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, DEBUG_MODE
from pyrate.engine.game import Game
from pyrate.ui.animation import AnimatedEffect


def run_game():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("PyRate")
    clock = pygame.time.Clock()
    game = Game()

    # Load assets
    sea_tex = pygame.image.load("assets/images/sea_tile.png").convert()
    splash_frames = load_frames([
        'assets/images/splash1.png', 'assets/images/splash2.png',
        'assets/images/splash3.png', 'assets/images/splash4.png'
    ])
    explosion_frames = load_frames([
        'assets/images/explosion1.png', 'assets/images/explosion2.png',
        'assets/images/explosion3.png'
    ])
    player_frames = load_frames([
        'assets/images/player_full.png', 'assets/images/player_damaged1.png',
        'assets/images/player_damaged2.png'
    ])
    enemy_frames = load_frames([
        'assets/images/enemy_full.png', 'assets/images/enemy_damaged1.png',
        'assets/images/enemy_damaged2.png'
    ])

    # Fonts for end screens
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)

    # semi-transparent overlay for debug drawings
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    # Pre-tile sea background once into a surface
    sea_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    tex_w, tex_h = sea_tex.get_width(), sea_tex.get_height()
    for x in range(0, SCREEN_WIDTH, tex_w):
        for y in range(0, SCREEN_HEIGHT, tex_h):
            sea_bg.blit(sea_tex, (x, y))

    running = True
    debug = DEBUG_MODE
    active_effects = []

    while running:
        # Handle input events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # allow restart on end screen
            if event.type == pygame.KEYDOWN and game.state in ("gameover", "victory"):
                running = False

        # Engine update
        game.update()

        # End game state handling
        if game.state != "playing":
            screen.fill((0, 0, 0))
            if game.state == "gameover":
                text = font.render("Game Over", True, (255, 0, 0))
                sub = small_font.render("Press any key to exit", True, (255, 255, 255))
            else:
                text = font.render("Victory!", True, (0, 255, 0))
                sub = small_font.render("Press any key to exit", True, (255, 255, 255))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            sub_rect = sub.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            screen.blit(text, text_rect)
            screen.blit(sub, sub_rect)
            pygame.display.flip()
            clock.tick(FPS)
            continue

        # Render world
        screen.blit(sea_bg, (0, 0))
        if debug:
            overlay.fill((0, 0, 0, 0))

        # Player
        draw_ship(screen, game.player_ship, player_frames, debug)

        # Enemies
        for enemy in game.enemies:
            if debug:
                pygame.draw.circle(
                    overlay, (0, 255, 0, 40), (int(enemy.x), int(enemy.y)), enemy.agro_radius
                )
            draw_ship(screen, enemy, enemy_frames, debug)

        # Projectiles
        for projectile in game.projectiles:
            pygame.draw.circle(
                screen, (0, 0, 0), (int(projectile.x), int(projectile.y)), projectile.radius
            )
            if debug:
                pygame.draw.circle(
                    overlay, (255, 255, 255, 80),
                    (int(projectile.x), int(projectile.y)), projectile.radius, width=1
                )

        # Animated effects
        new_impacts = game.impacts[:]
        game.impacts.clear()
        for impact in new_impacts:
            fx, fy = impact[0].x, impact[0].y
            if impact[1] == "hit":
                effect = AnimatedEffect(explosion_frames, (fx, fy), duration=200)
            else:
                effect = AnimatedEffect(splash_frames, (fx, fy), duration=300)
            active_effects.append(effect)

        for effect in active_effects[:]:
            effect.update()
            if effect.finished:
                active_effects.remove(effect)
        for effect in active_effects:
            effect.draw(screen)

        # Debug overlay
        if debug:
            screen.blit(overlay, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


def draw_ship(screen, ship, frames, debug=False):
    if not ship.is_living:
        return
    # choose frame based on health
    if ship.health > 50:
        sprite = frames[0]
    elif ship.health > 20:
        sprite = frames[1]
    else:
        sprite = frames[2]
    draw_entity(screen, ship, sprite, debug)


def draw_entity(screen, entity, sprite, debug=False):
    draw_rotated(screen, sprite, entity.x, entity.y, entity.angle)
    if debug:
        hitbox = entity.get_hitbox()
        pygame.draw.polygon(screen, (255, 255, 255), hitbox, width=1)


def draw_rotated(screen, image, x, y, angle):
    rotated = pygame.transform.rotate(image, -angle + 90)
    rect = rotated.get_rect(center=(int(x), int(y)))
    screen.blit(rotated, rect)


def load_frames(path_list):
    try:
        return [pygame.image.load(p).convert_alpha() for p in path_list]
    except pygame.error as e:
        print(f"Error loading frames: {e}")
        return []


def draw_ship(screen, ship, frames, debug=False):
    if not ship.is_living:
        return
    if ship.health > 50:
        sprite = frames[0]
    elif ship.health > 20:
        sprite = frames[1]
    else:
        sprite = frames[2]
    draw_entity(screen, ship, sprite, debug)
    draw_health_bar(screen, ship)  # ⬅️ AJOUT


def draw_health_bar(surface, ship):
    if not ship.is_living:
        return

    bar_width = 40
    bar_height = 6
    x = int(ship.x - bar_width / 2)
    y = int(ship.y - ship.height / 2 - 12)  # juste au-dessus du vaisseau

    # fond rouge
    pygame.draw.rect(surface, (100, 0, 0), (x, y, bar_width, bar_height))

    # barre verte selon la vie restante
    health_ratio = ship.health / 100
    pygame.draw.rect(surface, (0, 200, 0), (x, y, int(bar_width * health_ratio), bar_height))

    # bordure blanche
    pygame.draw.rect(surface, (255, 255, 255), (x, y, bar_width, bar_height), 1)




# pyrate/ui/renderer.py
import os
# Use dummy video driver for headless rendering
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame
import math
from pyrate.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, DEBUG_MODE
from pyrate.engine.game import Game
from pyrate.ui.animation import AnimatedEffect

# Initialize pygame
pygame.init()
pygame.display.set_mode((1, 1))


def load_frames(path_list):
    try:
        return [pygame.image.load(p).convert_alpha() for p in path_list]
    except pygame.error as e:
        print(f"Error loading frames: {e}")
        return []


class RendererAssets:
    """
    Preload and cache all assets needed for rendering.
    """
    def __init__(self):
        # Textures
        self.sea_tex = pygame.image.load("assets/images/sea_tile.png").convert()

        # Sprite frames
        self.splash_frames = load_frames([
            'assets/images/splash1.png', 'assets/images/splash2.png',
            'assets/images/splash3.png', 'assets/images/splash4.png'
        ])
        self.explosion_frames = load_frames([
            'assets/images/explosion1.png', 'assets/images/explosion2.png',
            'assets/images/explosion3.png'
        ])
        self.player_frames = load_frames([
            'assets/images/player_full.png', 'assets/images/player_damaged1.png',
            'assets/images/player_damaged2.png'
        ])
        self.enemy_frames = load_frames([
            'assets/images/enemy_full.png', 'assets/images/enemy_damaged1.png',
            'assets/images/enemy_damaged2.png'
        ])
        # Fonts
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
        # Overlay
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        # Pre-tiled sea background
        self.sea_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        tw, th = self.sea_tex.get_width(), self.sea_tex.get_height()
        for x in range(0, SCREEN_WIDTH, tw):
            for y in range(0, SCREEN_HEIGHT, th):
                self.sea_bg.blit(self.sea_tex, (x, y))


# Instantiate assets once
_assets = RendererAssets()


def run_game():
    """
    Main loop for interactive play.
    """
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("PyRate")
    clock = pygame.time.Clock()
    game = Game()
    debug = DEBUG_MODE
    effects = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and game.state in ("gameover", "victory"):
                running = False

        _render_frame(screen, clock, game, _assets, debug, effects)

    pygame.quit()


def _render_frame(screen, clock, game, assets, debug, active_effects):
    """
    Update game and draw one frame onto 'screen'.
    """
    game.update()

    # End game screens
    if game.state != "playing":
        screen.fill((0, 0, 0))
        if game.state == "gameover":
            title = "Game Over"
            color = (255, 0, 0)
        else:
            title = "Victory!"
            color = (0, 255, 0)
        text = assets.font.render(title, True, color)
        sub = assets.small_font.render("Press any key to exit", True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 20)))
        screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 40)))
    else:
        # Draw background
        screen.blit(assets.sea_bg, (0, 0))
        if debug:
            assets.overlay.fill((0, 0, 0, 0))

        # Player
        for ship in getattr(game, "player_ships", [game.player_ships]):
            # (optional) debug hitbox overlay for each player
            draw_ship(screen, ship, assets.player_frames, debug)

        # Enemies
        for enemy in game.enemy_ships:
            if debug:
                pygame.draw.circle(assets.overlay, (0, 255, 0, 40), (int(enemy.x), int(enemy.y)), enemy.agro_radius)
            draw_ship(screen, enemy, assets.enemy_frames, debug)

        # Projectiles
        for proj in game.projectiles:
            pygame.draw.circle(screen, (0, 0, 0), (int(proj.x), int(proj.y)), proj.radius)
            if debug:
                pygame.draw.circle(assets.overlay, (255, 255, 255, 80), (int(proj.x), int(proj.y)), proj.radius, 1)

        # Animated effects
        new = game.impacts[:]
        game.impacts.clear()
        for imp in new:
            x, y = imp[0].x, imp[0].y
            frames = assets.explosion_frames if imp[1] == "hit" else assets.splash_frames
            active_effects.append(AnimatedEffect(frames, (x, y), duration=200 if imp[1]=="hit" else 300))

        for eff in active_effects[:]:
            eff.update()
            if eff.finished:
                active_effects.remove(eff)
        for eff in active_effects:
            eff.draw(screen)

        if debug:
            screen.blit(assets.overlay, (0, 0))

    pygame.display.flip()
    clock.tick(FPS)


def render_frame_to_surface(game):
    """
    Capture a single frame headlessly and return the Surface.
    """
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    effects = []
    _render_frame(screen, clock, game, _assets, DEBUG_MODE, effects)
    return screen


def draw_entity(screen, entity, sprite, debug=False):
    rotated = pygame.transform.rotate(sprite, -entity.angle + 90)
    screen.blit(rotated, rotated.get_rect(center=(int(entity.x), int(entity.y))))
    if debug:
        pygame.draw.polygon(screen, (255, 255, 255), entity.get_hitbox(), 1)


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
    draw_health_bar(screen, ship)


def draw_health_bar(surface, ship):
    if not ship.is_living:
        return
    
    bar_width = 40
    bar_height = 6
    x = int(ship.x - bar_width / 2)
    y = int(ship.y - ship.height / 2 - 12)
    health_ratio = ship.health / 100

    pygame.draw.rect(surface, (100, 0, 0), (x, y, bar_width, bar_height))
    pygame.draw.rect(surface, (0, 200, 0), (x, y, int(bar_width * health_ratio), bar_height))
    pygame.draw.rect(surface, (255, 255, 255), (x, y, bar_width, bar_height), 1)




import pygame
from pyrate.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from pyrate.engine.game import Game

def run_game():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    game = Game()

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    running = True

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
        # fill the screen with a color to wipe away anything from last frame
        screen.fill("blue")
        overlay.fill((0, 0, 0, 0))

        # Player
        x, y = game.get_player_position()
        pygame.draw.circle(screen, (0, 255, 0), (x, y), 15)

        # Enemies
        for ex, ey, radius in game.get_enemies_positions():
            # Zone d’agro (transparente)
            pygame.draw.circle(overlay, (0, 255, 0, 40), (ex, ey), radius)
            # Ennemis
            pygame.draw.circle(screen, (255, 0, 0), (ex, ey), 15)

        # Projectiles
        for projectile in game.player_ship.projectiles:
            pygame.draw.circle(screen, (0, 0, 0), (int(projectile.x), int(projectile.y)), projectile.radius)


        screen.blit(overlay, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
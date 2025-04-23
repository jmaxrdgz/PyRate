import pygame
from pyrate.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

def run_game():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill("purple")  # Clear the screen

        # TODO: RENDER YOUR GAME HERE

        pygame.display.flip()  # Update the display
        clock.tick(FPS)        # Limit FPS

    pygame.quit()
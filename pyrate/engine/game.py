# pyrate/engine/game.py
import random
import math
from pyrate.engine.ship import Ship
from pyrate.engine.enemy import EnemyShip
from pyrate.engine.input import handle_input
from pyrate.settings import SCREEN_WIDTH, SCREEN_HEIGHT

class Game:
    def __init__(self, n_enemies=3, min_distance=200):
        # Position centrale du joueur
        player_x = SCREEN_WIDTH // 2
        player_y = SCREEN_HEIGHT // 2
        self.player_ship = Ship(player_x, player_y)

        self.enemies = []
        attempts = 0
        while len(self.enemies) < n_enemies and attempts < n_enemies * 10:
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            dist = math.hypot(x - player_x, y - player_y)
            if dist >= min_distance:
                self.enemies.append(EnemyShip(x, y))
            attempts += 1


    def update(self):
        handle_input(self.player_ship)
        self.player_ship.update()
        px, py = self.player_ship.x, self.player_ship.y
        pa = self.player_ship.angle
        for enemy in self.enemies:
            enemy.update(px, py, pa)


    def get_player_position(self):
        return int(self.player_ship.x), int(self.player_ship.y)


    def get_enemies_positions(self):
        return [
            (int(e.x), int(e.y), e.agro_radius)
            for e in self.enemies
        ]

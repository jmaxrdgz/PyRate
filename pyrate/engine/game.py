# pyrate/engine/game.py
import random
import math
from pyrate.engine.ship import Ship
from pyrate.engine.enemy import EnemyShip
from pyrate.engine.input import handle_input
from pyrate.settings import SCREEN_WIDTH, SCREEN_HEIGHT

class Game:
    def __init__(self, n_enemies=3, min_distance=200):
        """ Sets up entities spawn and state.

            Args:
            - n_enemies: Number of enemies in game.
            - min_distance: Minimum distance from the player where enemies can spawn
            at launch.
        """
        # player's spawn
        player_x = SCREEN_WIDTH // 2
        player_y = SCREEN_HEIGHT // 2
        self.player_ship = Ship(player_x, player_y)

        # projectiles memory
        self.projectiles = []

        self.enemies = []
        # enemies spawn outside of min_distance radius centered at player's spawn
        attempts = 0 # avoid infinite loop
        while len(self.enemies) < n_enemies and attempts < n_enemies * 10:
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            dist = math.hypot(x - player_x, y - player_y)
            if dist >= min_distance:
                self.enemies.append(EnemyShip(x, y))
            attempts += 1


    def update(self):
        """ Update all entities position, state & interaction.
        """
        handle_input(self.player_ship)
        self.player_ship.update()
        px, py, pa = self.player_ship.x, self.player_ship.y, self.player_ship.angle

        # update all enemies' position & state
        for enemy in self.enemies:
            enemy.update(px, py, pa)

        # update all projectiles' position & state
        remaining_projectiles = []
        for projectile in self.projectiles:
            projectile.update()
            if not projectile.has_exceeded_range():
                remaining_projectiles.append(projectile)
        self.projectiles = remaining_projectiles

        # check for collisions & handle damage
        self._handle_collisions()


    def _handle_collisions(self):
        # projectile vs Ship collisions
        collisions = []
        for projectile in self.projectiles:
            # check against player and enemies
            targets = [self.player_ship] + self.enemies
            for target in targets:
                if self.collide(projectile, target):
                    damage = self.compute_damage(projectile, target)
                    target.apply_damage(damage)
                    collisions.append((projectile, None))
        # remove collided projectiles
        self.projectiles = [p for p in self.projectiles if not any(p is c[0] for c in collisions)]

        # ship vs Ship collisions
        ships = [self.player_ship] + self.enemies
        for i in range(len(ships)):
            for j in range(i+1, len(ships)):
                s1, s2 = ships[i], ships[j]
                if self.collide(s1, s2):
                    damage = self.compute_damage(s1, s2)
                    s1.apply_damage(damage)
                    s2.apply_damage(damage)
    

    def collide(self, entity1, entity2):
        """
        Check polygonal hitbox collision between two entities using Separating Axis Theorem.
        Entities must implement .get_hitbox() -> List of (x,y) tuples.
        """
        poly1 = entity1.get_hitbox()
        poly2 = entity2.get_hitbox()
        # SAT: for each polygon's edges
        for points in (poly1, poly2):
            for i in range(len(points)):
                x1, y1 = points[i]
                x2, y2 = points[(i+1) % len(points)]
                # edge vector
                edge = (x2 - x1, y2 - y1)
                # perpendicular axis
                axis = (-edge[1], edge[0])
                # project both polys onto axis
                proj1 = [axis[0]*px + axis[1]*py for px, py in poly1]
                proj2 = [axis[0]*px + axis[1]*py for px, py in poly2]
                if max(proj1) < min(proj2) or max(proj2) < min(proj1):
                    return False
        return True


    def get_player_position(self):
        return int(self.player_ship.x), int(self.player_ship.y)


    def get_enemies_positions(self):
        return [
            (int(e.x), int(e.y), e.agro_radius)
            for e in self.enemies
        ]

    def get_projectile_position(self):
        return [
            (int(p.x), int(p.y))
            for p in self.projectiles
        ]
    
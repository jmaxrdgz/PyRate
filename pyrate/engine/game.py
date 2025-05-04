# pyrate/engine/game.py
import random
import math
from pyrate.engine.entities.ship import Ship
from pyrate.engine.entities.enemy import EnemyShip
from pyrate.engine.entities.projectile import Cannonball
from pyrate.engine.input import handle_input
from pyrate.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Game:
    def __init__(self, n_enemies=3, min_distance=300):
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
        self.impacts = []

        # enemies list
        self.enemies = []
        attempts = 0  # avoid infinite loop
        while len(self.enemies) < n_enemies and attempts < n_enemies * 10:
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            dist = math.hypot(x - player_x, y - player_y)
            if dist >= min_distance:
                self.enemies.append(EnemyShip(x, y))
            attempts += 1

    def update(self):
        """ Update all entities position, state & interaction. """
        handle_input(self.player_ship)
        self.player_ship.update()
        px, py, pa = self.player_ship.x, self.player_ship.y, self.player_ship.angle

        # update enemies
        for enemy in self.enemies:
            enemy.update(px, py, pa)

        # update projectiles and gather new from ships
        # transfer projectiles
        self.projectiles.extend(self.player_ship.projectiles)
        for enemy in self.enemies:
            self.projectiles.extend(enemy.projectiles)
        self.player_ship.projectiles.clear()
        for enemy in self.enemies:
            enemy.projectiles.clear()

        remaining_projectiles = []
        for projectile in self.projectiles:
            projectile.update()
            if not projectile.has_exceeded_range():
                remaining_projectiles.append(projectile)
            else:
                self.impacts.append((projectile, "miss"))
        self.projectiles = remaining_projectiles

        # handle collisions & damage
        self._handle_collisions()

    def _handle_collisions(self):
        # projectile vs ship
        collisions = []
        for projectile in self.projectiles:
            for target in [self.player_ship] + self.enemies:
                if self.collide(projectile, target):
                    target.apply_damage(projectile.damage)
                    print(f"{target.name} took {projectile.damage} damage, health remaining {target.health}")
                    collisions.append(projectile)
                    self.impacts.append((projectile, "hit"))
        # remove collided projectiles
        self.projectiles = [p for p in self.projectiles if p not in collisions]

        # ship vs ship
        ships = [self.player_ship] + self.enemies
        for i in range(len(ships)):
            for j in range(i + 1, len(ships)):
                s1, s2 = ships[i], ships[j]
                if self.collide(s1, s2):
                    damage = self.compute_damage(s1, s2)
                    s1.apply_damage(damage)
                    s2.apply_damage(damage)
                    print(f"Collision between {s1.name} and {s2.name}: {damage} damage each, "
                          f"{s1.name} health {s1.health}, {s2.name} health {s2.health}")

        # remove destroyed enemies
        before = len(self.enemies)
        self.enemies = [e for e in self.enemies if getattr(e, 'is_living', True)]
        removed = before - len(self.enemies)
        if removed > 0:
            print(f"Removed {removed} destroyed enemy ship(s)")

    def collide(self, entity1, entity2):
        """
        Check polygonal hitbox collision between two entities using Separating Axis Theorem.
        Entities must implement .get_hitbox() -> List of (x,y) tuples.
        """
        poly1 = entity1.get_hitbox()
        poly2 = entity2.get_hitbox()
        for points in (poly1, poly2):
            for i in range(len(points)):
                x1, y1 = points[i]
                x2, y2 = points[(i + 1) % len(points)]
                edge = (x2 - x1, y2 - y1)
                axis = (-edge[1], edge[0])
                proj1 = [axis[0] * px + axis[1] * py for px, py in poly1]
                proj2 = [axis[0] * px + axis[1] * py for px, py in poly2]
                if max(proj1) < min(proj2) or max(proj2) < min(proj1):
                    return False
        return True

    def compute_damage(self, e1, e2):
        rad1 = math.radians(e1.angle)
        v1x, v1y = e1.speed * math.cos(rad1), e1.speed * math.sin(rad1)
        rad2 = math.radians(e2.angle)
        v2x, v2y = e2.speed * math.cos(rad2), e2.speed * math.sin(rad2)
        rvx, rvy = v1x - v2x, v1y - v2y
        rel_speed = math.hypot(rvx, rvy)
        angle_diff = abs((e1.angle - e2.angle + 180) % 360 - 180)
        impact_factor = abs(math.cos(math.radians(angle_diff)))
        avg_coeff = (e1.dmg_coeff + e2.dmg_coeff) / 2
        damage = rel_speed * avg_coeff * impact_factor
        return damage

    def get_player_position(self):
        return int(self.player_ship.x), int(self.player_ship.y)

    def get_enemies_positions(self):
        return [(int(e.x), int(e.y), e.agro_radius) for e in self.enemies]

    def get_projectile_position(self):
        return [(int(p.x), int(p.y)) for p in self.projectiles]

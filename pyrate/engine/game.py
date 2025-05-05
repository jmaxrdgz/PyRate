# pyrate/engine/game.py
import random
import math
from pyrate.engine.entities.ship import Ship
from pyrate.engine.entities.enemy import EnemyShip
from pyrate.engine.entities.projectile import Cannonball
from pyrate.engine.input import handle_input
from pyrate.settings import SCREEN_WIDTH, SCREEN_HEIGHT


def distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def normalize(dx, dy):
    dist = math.hypot(dx, dy)
    if dist == 0:
        return 0, 0
    return dx / dist, dy / dist

class Game:
    def __init__(self, n_enemies=3, min_distance=300):
        """ Sets up entities spawn and state. """
        player_x = SCREEN_WIDTH // 2
        player_y = SCREEN_HEIGHT // 2
        self.player_ship = Ship(player_x, player_y)

        self.projectiles = []
        self.impacts = []
        self.enemies = []
        attempts = 0
        while len(self.enemies) < n_enemies and attempts < n_enemies * 10:
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            if math.hypot(x - player_x, y - player_y) >= min_distance:
                self.enemies.append(EnemyShip(x, y))
            attempts += 1

    def update(self):
        handle_input(self.player_ship)
        self.player_ship.update()
        px, py, pa = self.player_ship.x, self.player_ship.y, self.player_ship.angle

        # update enemies
        for enemy in self.enemies:
            enemy.update(px, py, pa, self.enemies)

        # transfer and update projectiles
        self.projectiles.extend(self.player_ship.projectiles)
        for enemy in self.enemies:
            self.projectiles.extend(enemy.projectiles)
        self.player_ship.projectiles.clear()
        for enemy in self.enemies:
            enemy.projectiles.clear()

        remaining = []
        for proj in self.projectiles:
            proj.update()
            if not proj.has_exceeded_range():
                remaining.append(proj)
            else:
                self.impacts.append((proj, 'miss'))
        self.projectiles = remaining

        # handle projectile vs ship collisions
        self._handle_projectile_hits()

        # handle ship vs ship collisions (separation, no enemy-enemy damage)
        self._handle_ship_collisions()

    def _handle_projectile_hits(self):
        collisions = []
        for proj in self.projectiles:
            for target in [self.player_ship] + self.enemies:
                if self.collide(proj, target):
                    target.apply_damage(proj.damage)
                    print(f"{target.name} took {proj.damage} damage, health remaining {target.health}")
                    collisions.append(proj)
                    self.impacts.append((proj, 'hit'))
        self.projectiles = [p for p in self.projectiles if p not in collisions]

    # TODO: Collision between 2 hitboxes (not hitbox to center)
    def _handle_ship_collisions(self):
        ships = [self.player_ship] + self.enemies
        for i in range(len(ships)):
            for j in range(i+1, len(ships)):
                s1, s2 = ships[i], ships[j]
                if not self.collide(s1, s2):
                    continue
                # separation: move ships apart
                dx = s1.x - s2.x
                dy = s1.y - s2.y
                nx, ny = normalize(dx, dy)
                overlap = (s1.width/2 + s2.width/2) - distance(s1, s2)
                # push half the overlap each
                if overlap > 0:
                    s1.x += nx * overlap * 1.25
                    s1.y += ny * overlap * 1.25
                    s2.x -= nx * overlap * 1.25
                    s2.y -= ny * overlap * 1.25
                # apply damage only if not both enemies
                if not (isinstance(s1, EnemyShip) and isinstance(s2, EnemyShip)):
                    dmg = self.compute_damage(s1, s2) / 3 # temp!
                    s1.apply_damage(dmg)
                    s2.apply_damage(dmg)
                    print(f"Collision between {s1.name} and {s2.name}: {dmg} damage each, "
                          f"{s1.name} health {s1.health}, {s2.name} health {s2.health}")
        # remove destroyed enemies
        before = len(self.enemies)
        self.enemies = [e for e in self.enemies if e.is_living]
        removed = before - len(self.enemies)
        if removed:
            print(f"Removed {removed} destroyed enemy ship(s)")

    def collide(self, e1, e2):
        poly1 = e1.get_hitbox()
        poly2 = e2.get_hitbox()
        for points in (poly1, poly2):
            for k in range(len(points)):
                x1, y1 = points[k]
                x2, y2 = points[(k+1)%len(points)]
                edge = (x2-x1, y2-y1)
                axis = (-edge[1], edge[0])
                proj1 = [axis[0]*px+axis[1]*py for px,py in poly1]
                proj2 = [axis[0]*px+axis[1]*py for px,py in poly2]
                if max(proj1) < min(proj2) or max(proj2) < min(proj1):
                    return False
        return True

    def compute_damage(self, e1, e2):
        rad1 = math.radians(e1.angle)
        v1x, v1y = e1.speed*math.cos(rad1), e1.speed*math.sin(rad1)
        rad2 = math.radians(e2.angle)
        v2x, v2y = e2.speed*math.cos(rad2), e2.speed*math.sin(rad2)
        rvx, rvy = v1x-v2x, v1y-v2y
        rel_speed = math.hypot(rvx, rvy)
        angle_diff = abs((e1.angle-e2.angle+180)%360-180)
        impact = abs(math.cos(math.radians(angle_diff)))
        coeff = (e1.dmg_coeff + e2.dmg_coeff)/2
        return rel_speed * coeff * impact

    def get_player_position(self):
        return int(self.player_ship.x), int(self.player_ship.y)

    def get_enemies_positions(self):
        return [(int(e.x), int(e.y), e.agro_radius) for e in self.enemies]

    def get_projectile_position(self):
        return [(int(p.x), int(p.y)) for p in self.projectiles]

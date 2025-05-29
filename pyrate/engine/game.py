# pyrate/engine/game.py
import random
import math
from pyrate.engine.entities.ship import Ship
from pyrate.engine.entities.enemy import EnemyShip
from pyrate.engine.entities.projectile import Cannonball
from pyrate.engine.input import handle_input
from pyrate.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from pyrate.engine.entities.island import Island
import time
from pyrate.engine.entities.bonus import Bonus





def sat_mtv(poly1, poly2):
    """
    Compute the Minimum Translation Vector (dx, dy) to separate poly1 from poly2
    using the Separating Axis Theorem. Returns None if no collision.
    """
    min_overlap = float('inf')
    mtv_axis = (0, 0)

    for points in (poly1, poly2):
        for i in range(len(points)):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % len(points)]
            # edge vector
            edge = (x2 - x1, y2 - y1)
            # perpendicular axis
            axis = (-edge[1], edge[0])
            # normalize axis
            length = math.hypot(axis[0], axis[1])
            if length == 0:
                continue
            axis = (axis[0] / length, axis[1] / length)

            # project both polygons onto axis
            proj1 = [axis[0] * px + axis[1] * py for px, py in poly1]
            proj2 = [axis[0] * px + axis[1] * py for px, py in poly2]
            min1, max1 = min(proj1), max(proj1)
            min2, max2 = min(proj2), max(proj2)

            # check overlap
            overlap = min(max1, max2) - max(min1, min2)
            if overlap <= 0:
                return None  # no collision
            # track smallest overlap
            if overlap < min_overlap:
                min_overlap = overlap
                mtv_axis = axis

    # mtv to push poly1 out of poly2
    return (mtv_axis[0] * min_overlap, mtv_axis[1] * min_overlap)


def distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)

def add_uniform_noise(value, noise_range):
    return value + random.uniform(-noise_range, noise_range) #Adds uniform noise in the range [-noise_range, +noise_range]

def normalize(dx, dy):
    dist = math.hypot(dx, dy)
    return (dx / dist, dy / dist) if dist != 0 else (0, 0)


class Game:
    def __init__(self, n_enemies=3, min_distance=300):
        """ Sets up entities spawn and state. """
        player_x = SCREEN_WIDTH // 2
        player_y = SCREEN_HEIGHT // 2
        self.player_ship = Ship(player_x, player_y)

        self.ships_colliding_with_island = {}

        self.bonuses = []
        self.last_bonus_time = time.time()

        self.projectiles = []
        self.impacts = []
        self.enemies = []
        self.state = "playing"  # 'playing', 'victory', 'gameover'
        attempts = 0
        while len(self.enemies) < n_enemies and attempts < n_enemies * 10:
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            if math.hypot(x - player_x, y - player_y) >= min_distance:
                self.enemies.append(EnemyShip(x, y))
            attempts += 1
        
        self.sensor_range = 200

    def update(self):
        # skip logic if game ended
        if self.state != "playing":
            return

        handle_input(self.player_ship)
        self.player_ship.update()
        px, py, pa = self.player_ship.x, self.player_ship.y, self.player_ship.angle

        self._maybe_spawn_bonus()
        self._handle_bonus_collection()


        # update enemies
        for enemy in self.enemies:
            enemy.update(px, py, pa, self.enemies)

        # update projectiles
        remaining = []
        # gather new from ships
        self.projectiles.extend(self.player_ship.projectiles)
        for enemy in self.enemies:
            self.projectiles.extend(enemy.projectiles)
        self.player_ship.projectiles.clear()
        for enemy in self.enemies:
            enemy.projectiles.clear()
        for proj in self.projectiles:
            proj.update()
            if proj.has_exceeded_range():
                self.impacts.append((proj, 'miss'))
            else:
                remaining.append(proj)
        self.projectiles = remaining

        # handle collisions
        self._handle_projectile_hits()
        self._handle_ship_collisions()

        for ship in [self.player_ship] + self.enemies:
            collided = False
            for island in self.islands:
                if self.collide(ship, island):
                    dx = ship.x - island.x
                    dy = ship.y - island.y  
                    nx, ny = normalize(dx, dy)
                    ship.x += nx * 4
                    ship.y += ny * 4

                    if not self.ships_colliding_with_island.get(ship, False):
                        ship.apply_damage(0.5)
                        print(f"{ship.name} hit an island !") 
                        self.ships_colliding_with_island[ship] = True
                    collided = True
                    break
                if not collided:
                    self.ships_colliding_with_island[ship] = False
    
        # end game check
        self._check_end_conditions()

    def _check_end_conditions(self):
        if not getattr(self.player_ship, 'is_living', True):
            self.state = "gameover"
            print("Game Over: Player ship destroyed.")
        elif not self.enemies:
            self.state = "victory"
            print("Victory: All enemy ships destroyed.")

    def _handle_projectile_hits(self):
        collisions = []
        for proj in self.projectiles:
            for target in [self.player_ship] + self.enemies:
                if self.collide(proj, target):
                    target.apply_damage(proj.damage)
                    print(f"{target.name} took {proj.damage} damage, health remaining {target.health}")
                    collisions.append(proj)
                    self.impacts.append((proj, 'hit'))
                if not target.is_living and isinstance(target, EnemyShip):
                    self.score += 100
                    print("Enemy destroyed! +100 points")
        self.projectiles = [p for p in self.projectiles if p not in collisions]

    def _handle_ship_collisions(self):
        ships = [self.player_ship] + self.enemies
        for i in range(len(ships)):
            for j in range(i+1, len(ships)):
                s1, s2 = ships[i], ships[j]
                if not self.collide(s1, s2):
                    continue
                # separation
                dx = s1.x - s2.x
                dy = s1.y - s2.y
                nx, ny = normalize(dx, dy)
                overlap = (s1.width/2 + s2.width/2) - distance(s1, s2)
                if overlap > 0:
                    s1.x += nx * overlap * 1.25
                    s1.y += ny * overlap * 1.25
                    s2.x -= nx * overlap * 1.25
                    s2.y -= ny * overlap * 1.25
                # damage
                if not (isinstance(s1, EnemyShip) and isinstance(s2, EnemyShip)):
                    dmg = self.compute_damage(s1, s2) / 3
                    s1.apply_damage(dmg)
                    s2.apply_damage(dmg)
                    print(f"Collision between {s1.name} and {s2.name}: {dmg} damage each, "
                          f"{s1.name} health {s1.health}, {s2.name} health {s2.health}")
        # remove destroyed
        before = len(self.enemies)
        self.enemies = [e for e in self.enemies if getattr(e, 'is_living', True)]
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


    def update_sensors(self):
        #Updates the sensors on each boat with uniform noise
        ships = [self.player_ship] + self.enemies
        for ship in ships:
            ship.detected_ships = []

        for ship in ships:
            for other_ship in ships:
                if ship is other_ship:
                    continue

                dist = distance(ship, other_ship)
                if dist <= self.sensor_range:
                    ship.detected_ships.append({
                        "ship": other_ship,
                        "x": add_uniform_noise(other_ship.x, noise_range=3),
                        "y": add_uniform_noise(other_ship.y, noise_range=3),
                        "angle": add_uniform_noise(other_ship.angle, noise_range=5),
                        "distance": add_uniform_noise(dist, noise_range=2),
                    })



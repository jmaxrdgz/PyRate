# pyrate/engine/game.py
import random
import math
from math import hypot
from pyrate.engine.entities.ship import Ship
from pyrate.engine.entities.enemy import EnemyShip
from pyrate.engine.entities.projectile import Cannonball
from pyrate.engine.input import handle_input
from pyrate.settings import SCREEN_WIDTH, SCREEN_HEIGHT


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


def normalize(dx, dy):
    dist = math.hypot(dx, dy)
    return (dx / dist, dy / dist) if dist != 0 else (0, 0)


class Game:
    def __init__(self, n_players=4, n_enemies=3, min_distance=300):
        """ Sets up entities spawn and state. """
        self.control_mode = "api"
        self.state = "playing"  # 'playing', 'A victory', 'B victory', 'gameover'

        self.player_ships = self._spawn_players(n_players) # List of player ships
        self.enemy_ships = self._spawn_enemies(n_enemies, min_distance) # List of enemy ships

        self.projectiles = []
        self.impacts = []


    def update(self):
        # skip logic if game ended
        if self.state != "playing":
            return

        # 1) input & physics for each player
        for ship in self.player_ships:
            if self.control_mode == "keyboard":
                handle_input(ship)
            ship.update()

        # prepare a list of (x,y,angle) for targeting
        player_positions = [(ship.x, ship.y, ship.angle) for ship in self.player_ships]

        # 2) update enemies, targeting nearest player
        for enemy in self.enemy_ships:
            # find closest player
            closest = min(
                player_positions,
                key=lambda p: math.hypot(p[0] - enemy.x, p[1] - enemy.y)
            )
            px, py, pa = closest
            enemy.update(px, py, pa, self.enemy_ships)

        # 3) update projectiles
        remaining = []

        # pull in any projectiles from all players
        for ship in self.player_ships:
            self.projectiles.extend(ship.projectiles)
            ship.projectiles.clear()

        # …and also from enemies
        for enemy in self.enemy_ships:
            self.projectiles.extend(enemy.projectiles)
            enemy.projectiles.clear()

        # step every projectile
        for proj in self.projectiles:
            proj.update()
            if proj.has_exceeded_range():
                self.impacts.append((proj, 'miss'))
            else:
                remaining.append(proj)
        self.projectiles = remaining

        # collisions & end‐game
        self._handle_projectile_hits()
        self._handle_ship_collisions()
        self._check_end_conditions()


    
    def _spawn_players(self, n_players):
        """ Spawn player ships at predefined locations. """
        if n_players > 6:
            raise ValueError("Number of players must be less than 6.")
        
        # Spawn points defined as (x, y, angle)
        # NOTE: order of spawn points is important for the player team creation
        spawn_info = [
            (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4, 0, "A"),
            (SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT // 4, 180, "B"),
            (SCREEN_WIDTH // 4, SCREEN_HEIGHT * 3 // 4, 0, "A"),
            (SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT * 3 // 4, 180, "B"),
            (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2, 0, "A"),
            (SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT // 2, 180, "B"),
        ]

        player_ships = []
        for i_player in range(n_players):
            x, y, angle, team = spawn_info[i_player]
            new_player = Ship(x, y, angle, team)
            player_ships.append(new_player)

        return player_ships
    

    def _spawn_enemies(self, n_enemies, min_distance):
        """ Spawn enemy ships at random locations at least `min_distance` from every player. """
        enemies = []

        # Gather all player positions
        player_positions = [(p.x, p.y) for p in self.player_ships]

        for _ in range(n_enemies):
            while True:
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)

                # 1) Must be far enough from every player
                too_close_to_player = any(
                    hypot(x - px, y - py) < min_distance
                    for px, py in player_positions
                )
                if too_close_to_player:
                    continue

                # 2) (Optional) If you still want enemies spaced from each other:
                too_close_to_enemy = any(
                    hypot(x - e.x, y - e.y) < min_distance
                    for e in enemies
                )
                if too_close_to_enemy:
                    continue

                # passed both checks
                break

            new_enemy = EnemyShip(x, y)
            enemies.append(new_enemy)

        return enemies


    def _check_end_conditions(self):
        """
        Evaluate end-game conditions and set self.state accordingly:
        - "A victory": at least one team-A ship alive, all team-B dead, all enemies dead
        - "B victory": at least one team-B ship alive, all team-A dead, all enemies dead
        - "gameover": at least one enemy alive, and both team-A and team-B ships are all dead
        """
        a_alive = any(p.team == "A" and p.is_living for p in self.player_ships)
        b_alive = any(p.team == "B" and p.is_living for p in self.player_ships)
        enemies_alive = any(e.is_living for e in self.enemy_ships)

        # A victory
        if not enemies_alive and a_alive and not b_alive:
            self.state = "A victory"
            print("A Victory: Team A wins, all enemies destroyed and Team B eliminated.")

        # B victory
        elif not enemies_alive and b_alive and not a_alive:
            self.state = "B victory"
            print("B Victory: Team B wins, all enemies destroyed and Team A eliminated.")

        # Game over
        elif enemies_alive and not a_alive and not b_alive:
            self.state = "gameover"
            print("Game Over: All player ships destroyed, enemies still active.")

        # Otherwise stay in playing
        else:
            self.state = "playing"


    def _handle_projectile_hits(self):
        collisions = []
        targets = self.player_ships + self.enemy_ships
        for proj in self.projectiles:
            for target in targets:
                if self.collide(proj, target):
                    target.apply_damage(proj.damage)
                    print(f"{target.name} took {proj.damage} damage, health remaining {target.health}")
                    collisions.append(proj)
                    self.impacts.append((proj, 'hit'))
        # remove hit projectiles
        self.projectiles = [p for p in self.projectiles if p not in collisions]


    def _handle_ship_collisions(self):
        ships = self.player_ships + self.enemy_ships
        for i in range(len(ships)):
            for j in range(i+1, len(ships)):
                s1, s2 = ships[i], ships[j]
                if not self.collide(s1, s2):
                    continue

                # separation
                dx, dy = s1.x - s2.x, s1.y - s2.y
                nx, ny = normalize(dx, dy)
                overlap = (s1.width/2 + s2.width/2) - distance(s1, s2)
                if overlap > 0:
                    s1.x += nx * overlap * 1.25
                    s1.y += ny * overlap * 1.25
                    s2.x -= nx * overlap * 1.25
                    s2.y -= ny * overlap * 1.25

                # damage (only between player↔enemy or player↔player if desired)
                if not (isinstance(s1, EnemyShip) and isinstance(s2, EnemyShip)):
                    dmg = self.compute_damage(s1, s2) / 3
                    s1.apply_damage(dmg)
                    s2.apply_damage(dmg)
                    print(f"Collision between {s1.name} and {s2.name}: {dmg} damage each, "
                          f"{s1.name} health {s1.health}, {s2.name} health {s2.health}")

        # clean up destroyed enemies
        before = len(self.enemy_ships)
        self.enemy_ships = [e for e in self.enemy_ships if e.is_living]
        removed = before - len(self.enemy_ships)
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


    def get_player_positions(self):
        """ Return list of (x, y) for all living players """
        return [(int(p.x), int(p.y)) for p in self.player_ships if p.is_living]


    def get_enemies_positions(self):
        return [(int(e.x), int(e.y), e.agro_radius) for e in self.enemy_ships]


    def get_projectile_positions(self):
        return [(int(p.x), int(p.y)) for p in self.projectiles]

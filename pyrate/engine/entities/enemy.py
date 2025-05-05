# pyrate/engine/entities/enemy.py
from pyrate.engine.entities.ship import Ship
import math, random
import time

class EnemyShip(Ship):
    def __init__(self, x, y, agro_radius=250, preferred_distance=100, patrol_radius=400, avoidance_radius=50):
        super().__init__(x, y)
        self.name = "Enemy ship"
        self.anchor_x = x
        self.anchor_y = y
        self.agro_radius = agro_radius
        self.preferred_distance = preferred_distance
        self.patrol_radius = patrol_radius
        self.avoidance_radius = avoidance_radius
        self.time = 0

    def update(self, player_x, player_y, player_angle, all_enemies):
        dx = player_x - self.x
        dy = player_y - self.y
        dist_to_player = math.hypot(dx, dy)
        dist_to_anchor = math.hypot(self.x - self.anchor_x, self.y - self.anchor_y)

        in_pursuit = dist_to_player < self.agro_radius
        # Détecter mode parallèle (à bonne distance)
        parallel_mode = in_pursuit and abs(dist_to_player - self.preferred_distance) <= 20

        if in_pursuit:
            # calcul angle de poursuite
            angle_to_player = math.degrees(math.atan2(dy, dx))
            if dist_to_player > self.preferred_distance + 20:
                target_angle = angle_to_player + 30
            elif dist_to_player < self.preferred_distance - 20:
                target_angle = angle_to_player - 150
            else:
                target_angle = player_angle + 90

            # orienter et accélérer
            self._steer_towards(target_angle)
            self.accelerate()

            # tirer si en mode parallèle et canon prêt
            if parallel_mode:
                # côté de tir selon écart d'angle
                diff = (target_angle - self.angle + 180) % 360 - 180
                side = 'right' if diff > 0 else 'left'
                self.fire(side)
        else:
            # mode patrouille
            self._steer_towards(random.uniform(0, 360))
            if dist_to_anchor > self.patrol_radius:
                angle_to_anchor = math.degrees(math.atan2(self.anchor_y - self.y, self.anchor_x - self.x))
                self._steer_towards(angle_to_anchor)
            self.speed = min(self.speed + self.acceleration, self.max_speed * 0.5)

        # éviter collisions entre ennemis
        for other in all_enemies:
            if other is self:
                continue
            dx_e = other.x - self.x
            dy_e = other.y - self.y
            dist_e = math.hypot(dx_e, dy_e)
            if 0 < dist_e < self.avoidance_radius:
                away_angle = math.degrees(math.atan2(-dy_e, -dx_e))
                self._steer_towards(away_angle)
                self.decelerate()

        super().update()
        self.time += 1

    def _steer_towards(self, target_angle, deadzone=5):
        """ Adjust rotation velocity to steer toward a target angle with inertia """
        diff = (target_angle - self.angle + 180) % 360 - 180
        if abs(diff) > deadzone:
            if diff > 0:
                self.turn_right()
            else:
                self.turn_left()

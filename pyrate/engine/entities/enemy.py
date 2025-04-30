# pyrate/engine/enemy.py
from pyrate.engine.entities.ship import Ship
import math, random

class EnemyShip(Ship):
    def __init__(self, x, y, agro_radius=150, preferred_distance=100, patrol_radius=400):
        super().__init__(x, y)
        # point d’ancrage et zones
        self.name = "Enemy ship"
        self.anchor_x = x
        self.anchor_y = y
        self.agro_radius = agro_radius
        self.preferred_distance = preferred_distance
        self.patrol_radius = patrol_radius
        self.time = 0

    def update(self, player_x, player_y, player_angle):
        # calculs de distances
        dx = player_x - self.x
        dy = player_y - self.y
        dist_to_player = math.hypot(dx, dy)
        dist_to_anchor = math.hypot(self.x - self.anchor_x, self.y - self.anchor_y)

        if dist_to_player < self.agro_radius:
            # === COMPORTEMENT DE POURSUIVANT TACTIQUE ===
            angle_to_player = math.degrees(math.atan2(dy, dx))

            if dist_to_player > self.preferred_distance + 20:
                offset = angle_to_player + 30
            elif dist_to_player < self.preferred_distance - 20:
                offset = angle_to_player - 150
            else:
                offset = player_angle + 90

            self.angle = self._smooth_angle(self.angle, offset)
            self.accelerate()

        else:
            # === PATROUILLE ALÉATOIRE DANS LA ZONE DE PATROL ===
            # 1) léger jitter aléatoire sur l'angle
            self.angle += random.uniform(-1, 1) * self.rotation_speed

            # 2) si on s'éloigne trop de l’ancre, on recentre la trajectoire
            if dist_to_anchor > self.patrol_radius:
                angle_to_anchor = math.degrees(
                    math.atan2(self.anchor_y - self.y, self.anchor_x - self.x)
                )
                # on oriente doucement vers l’ancre
                self.angle = self._smooth_angle(self.angle, angle_to_anchor)

            # 3) avance à mi-vitesse pour la patrouille
            self.speed = min(self.speed + self.acceleration, self.max_speed * 0.5)

        # applique la physique de base
        super().update()
        self.time += 1

    def _smooth_angle(self, current, target, factor=0.2):
        diff = (target - current + 180) % 360 - 180
        return current + factor * diff

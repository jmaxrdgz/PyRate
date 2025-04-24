# pyrate/engine/enemy.py
from pyrate.engine.ship import Ship
import math

class EnemyShip(Ship):
    def __init__(self, x, y, agro_radius=300, preferred_distance=200):
        super().__init__(x, y)
        self.anchor_x = x
        self.anchor_y = y
        self.agro_radius = agro_radius
        self.preferred_distance = preferred_distance
        self.time = 0

    def update(self, player_x, player_y, player_angle):
        dx = player_x - self.x
        dy = player_y - self.y
        dist_to_player = math.hypot(dx, dy)

        if dist_to_player < self.agro_radius:
            # Angle entre l’ennemi et le joueur
            angle_to_player = math.degrees(math.atan2(dy, dx))

            # Cherche à rester en parallèle, décalé latéralement
            if dist_to_player > self.preferred_distance + 20:
                # Trop loin → s’approche en diagonale, légèrement latéral
                offset_angle = angle_to_player + 30  # 30° de biais
            elif dist_to_player < self.preferred_distance - 20:
                # Trop proche → recule/élargit l’écart
                offset_angle = angle_to_player - 150
            else:
                # À bonne distance → se met en parallèle
                offset_angle = player_angle + 90  # se place sur le flanc

            self.angle = self._smooth_angle(self.angle, offset_angle)
            self.accelerate()
        else:
            # Patrouille autour de l’ancre
            self.angle += math.sin(self.time / 60) * self.rotation_speed
            self.accelerate()

        super().update()
        self.time += 1

    def _smooth_angle(self, current, target, factor=0.2):
        diff = (target - current + 180) % 360 - 180
        return current + factor * diff

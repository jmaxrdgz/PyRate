# pyrate/engine/projectile.py
import math

from pyrate.engine.entities.entity import Entity

class Cannonball(Entity):
    def __init__(self, x, y, angle, speed=8, max_distance=600):
        super().__init__(x, y, name="Cannonball")
        self.start_x = self.x
        self.start_y = self.y
        self.angle = angle
        self.speed = speed
        self.radius = 5
        self.max_distance = max_distance
        self.damage = 30

    def update(self):
        rad = math.radians(self.angle)
        self.x += math.cos(rad) * self.speed
        self.y += math.sin(rad) * self.speed

    def has_exceeded_range(self):
        dx = self.x - self.start_x
        dy = self.y - self.start_y
        return math.hypot(dx, dy) > self.max_distance
    

    def get_hitbox(self):
        return [
            (self.x - self.radius, self.y - self.radius),
            (self.x + self.radius, self.y - self.radius),
            (self.x + self.radius, self.y + self.radius),
            (self.x - self.radius, self.y + self.radius),
        ]
    

    def apply_damage(self, target):
        pass

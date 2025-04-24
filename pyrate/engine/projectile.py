# pyrate/engine/projectile.py
import math

class Cannonball:
    def __init__(self, x, y, angle, speed=8, max_distance=600):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.angle = angle
        self.speed = speed
        self.radius = 5
        self.max_distance = max_distance

    def update(self):
        rad = math.radians(self.angle)
        self.x += math.cos(rad) * self.speed
        self.y += math.sin(rad) * self.speed

    def has_exceeded_range(self):
        dx = self.x - self.start_x
        dy = self.y - self.start_y
        return math.hypot(dx, dy) > self.max_distance

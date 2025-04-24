# pyrate/engine/ship.py
import math

class Ship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0      # en degrés
        self.speed = 0
        self.max_speed = 5
        self.acceleration = 0.2
        self.rotation_speed = 3
        self.friction = 0.05

    def update(self):
        # Appliquer la friction
        if self.speed > 0:
            self.speed -= self.friction
        elif self.speed < 0:
            self.speed += self.friction

        # Calcul du déplacement
        rad = math.radians(self.angle)
        self.x += self.speed * math.cos(rad)
        self.y += self.speed * math.sin(rad)

    def accelerate(self):
        self.speed = min(self.speed + self.acceleration, self.max_speed)

    def decelerate(self):
        self.speed = max(self.speed - self.acceleration, 0)

    def turn_left(self):
        self.angle -= self.rotation_speed

    def turn_right(self):
        self.angle += self.rotation_speed

# pyrate/engine/ship.py
import math
import time

from pyrate.engine.projectile import Cannonball

class Ship:

    def __init__(self, x, y):
        # Displacement
        self.x = x
        self.y = y
        self.angle = 0      # en degrés
        self.speed = 0
        self.max_speed = 2
        self.acceleration = 0.2
        self.rotation_speed = 3
        self.friction = 0.05

        # Projectile
        self.projectiles = []
        self.last_fire_time = {"left": 0, "right": 0}
        self.cooldown = 4.0

        # Gameplay
        self.health = 100
        self.is_living = True


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


    def fire(self, side="left"):
        now = time.time()
        if now - self.last_fire_time[side] < self.cooldown:
            return  # still in cooldown

        self.last_fire_time[side] = now

        angle_offset = 90 if side == "right" else -90
        cannon_angle = (self.angle + angle_offset) % 360
        offset_rad = math.radians(cannon_angle)

        x = self.x + math.cos(offset_rad) * 20
        y = self.y + math.sin(offset_rad) * 20

        self.projectiles.append(Cannonball(x, y, cannon_angle))
    
    def apply_damage(self, amount):
        self.health = max(self.health - amount, 0)
        if self.health == 0:
            self.is_living = False
            self.on_destroy()


    def on_destroy(self):
        # Handle ship destruction logic here
        pass

    
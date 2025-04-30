# pyrate/engine/ship.py
import math
import time

from pyrate.engine.entities.entity import Entity
from pyrate.engine.entities.projectile import Cannonball

class Ship(Entity):

    def __init__(self, x, y):
        super().__init__(x, y, name="Player ship")
        # Displacement
        super().__init__(x, y, name="Ship")
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
        self.width = 50 # temp!
        self.height = 20 # temp!


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


    def get_hitbox(self):
        """
        Retourne la liste des sommets (x, y) du rectangle
        centrée sur (self.x, self.y), tourné de self.angle degrés.
        """
        hw, hh = self.width / 2, self.height / 2
        # définition des coins avant rotation
        corners = [
            (-hw, -hh),
            ( hw, -hh),
            ( hw,  hh),
            (-hw,  hh),
        ]
        rad = math.radians(self.angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)

        hitbox = []
        for dx, dy in corners:
            # rotation puis translation
            rx = dx * cos_a - dy * sin_a
            ry = dx * sin_a + dy * cos_a
            hitbox.append((self.x + rx, self.y + ry))

        return hitbox


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

    
# pyrate/engine/ship.py
import math
import time

from pyrate.engine.entities.entity import Entity
from pyrate.engine.entities.projectile import Cannonball
from pyrate.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Ship(Entity):

    def __init__(self, x, y, angle=0, team="A"):
        super().__init__(x, y, name="Ship")
        # Displacement
        self.angle = angle  # degrees
        self.speed = 0
        self.max_speed = 2
        self.acceleration = 0.1
        self.friction = 0.04

        # Rotation inertia
        self.rotation_velocity = 0
        self.rotation_acceleration = 0.3
        self.rotation_max_speed = 2
        self.rotation_friction = 0.1

        # Projectile
        self.projectiles = []
        self.last_fire_time = {"left": 0, "right": 0}
        self.cooldown = 4.0

        # Gameplay
        self.team = team
        self.health = 100
        self.is_living = True
        self.height = 100
        self.width = 40
    
        self.temp_damage_boost = False


    def update(self):
        # Apply friction to linear speed
        if self.speed > 0:
            self.speed -= self.friction
            self.speed = max(self.speed, 0)
        elif self.speed < 0:
            self.speed += self.friction
            self.speed = min(self.speed, 0)

        # Apply friction to rotation
        if self.rotation_velocity > 0:
            self.rotation_velocity -= self.rotation_friction
            self.rotation_velocity = max(self.rotation_velocity, 0)
        elif self.rotation_velocity < 0:
            self.rotation_velocity += self.rotation_friction
            self.rotation_velocity = min(self.rotation_velocity, 0)

        # Apply rotation
        self.angle += self.rotation_velocity

        # Apply movement
        rad = math.radians(self.angle)
        self.x += self.speed * math.cos(rad)
        self.y += self.speed * math.sin(rad)

        # Keep ship within screen bounds
        self.x = max(20, min(self.x, SCREEN_WIDTH - 20))
        self.y = max(20, min(self.y, SCREEN_HEIGHT - 20))


    def get_hitbox(self):
        """
        Retourne la liste des sommets (x, y) du rectangle
        centrée sur (self.x, self.y), tourné de self.angle degrés.
        """
        hw, hh = self.height / 2, self.width / 2
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
        if self.speed > 0.1:
            self.rotation_velocity = max(self.rotation_velocity - self.rotation_acceleration, -self.rotation_max_speed)


    def turn_right(self):
        if self.speed > 0.1:
            self.rotation_velocity = min(self.rotation_velocity + self.rotation_acceleration, self.rotation_max_speed)


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
        
        cannonball = Cannonball(x, y, cannon_angle)
        if self.temp_damage_boost:
            cannonball.damage *= 2
            self.temp_damage_boost = False

        self.projectiles.append(cannonball)

    def apply_damage(self, amount):
        self.health = max(self.health - amount, 0)
        if self.health == 0:
            self.on_destroy()


    def on_destroy(self):
        self.is_living = False
        pass

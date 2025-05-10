import pygame

class Bonus:
    def __init__(self, x, y, bonus_type="health"):
        self.x = x
        self.y = y
        self.type = bonus_type  # 'health' or 'damage'
        self.radius = 20
        self.collected = False

        image_path = f"assets/images/bonus_{bonus_type}.png"
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 40))

    def draw(self, screen):
        rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(self.image, rect)

    def get_hitbox(self):
        return [
            (self.x - self.radius, self.y - self.radius),
            (self.x + self.radius, self.y - self.radius),
            (self.x + self.radius, self.y + self.radius),
            (self.x - self.radius, self.y + self.radius),
        ]

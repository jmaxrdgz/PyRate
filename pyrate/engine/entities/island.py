class Island:

    def __init__(self, x, y, radius=60):
        self.x = x
        self.y = y
        self.radius = radius

    def get_hitbox(self):
        margin = self.radius * 0.70
        return [
            (self.x - margin, self.y - margin),
            (self.x + margin, self.y - margin),
            (self.x + margin, self.y + margin),
            (self.x - margin, self.y + margin),
        ]

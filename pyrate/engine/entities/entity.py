class Entity:
    """
    Base class for all entities in the game.
    """

    def __init__(self, x, y, name="Entity"):
        self.x = x
        self.y = y
        self.speed = 0
        self.dmg_coeff = 1.0
        self.name = name
        self._is_alive = True

    def on_destroy(self):
        self._is_alive = False
import pygame

class AnimatedEffect:
    def __init__(self, frames, pos, duration, loop=False):
        """
        frames: list of pygame.Surface objects
        pos: (x, y) position to render the effect
        duration: total duration of the animation in milliseconds
        loop: whether the animation should loop
        """
        self.frames = frames
        self.pos = pos
        self.duration = duration
        self.loop = loop
        self.start_time = pygame.time.get_ticks()
        self.frame_count = len(frames)
        self.frame_duration = duration / self.frame_count
        self.finished = False

    def update(self):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time

        if self.loop:
            elapsed %= self.duration
        elif elapsed >= self.duration:
            self.finished = True
            return

        frame_index = int(elapsed / self.frame_duration)
        self.current_frame = self.frames[frame_index]

    def draw(self, surface):
        if not self.finished:
            rect = self.current_frame.get_rect(center=self.pos)
            surface.blit(self.current_frame, rect)

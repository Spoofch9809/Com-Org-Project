import pygame

class HealthBar:
    def __init__(self, max_health):
        self.max_health = max_health
        self.health = max_health

    def draw(self, surface, x, y):
        bar_width = 40  # Width of the health bar
        bar_height = 5   # Height of the health bar
        fill = (self.health / self.max_health) * bar_width  # Calculate fill based on current health

        # Draw the empty health bar
        pygame.draw.rect(surface, (0, 0, 0), (x, y, bar_width, bar_height))  # Red background
        # Draw the filled part of the health bar
        pygame.draw.rect(surface, (255, 0, 0), (x, y, fill, bar_height))  # Green filled part

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def reset(self):
        self.health = self.max_health

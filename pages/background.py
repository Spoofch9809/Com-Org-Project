import pygame

class Background:
    def __init__(self, image_path, size, scroll_speed1=1):
        self.image = pygame.image.load(image_path).convert()
        self.image = pygame.transform.scale(self.image, size)
        self.scroll_speed = scroll_speed1
        self.y1 = 0
        self.y2 = -self.image.get_height()  # Start the second image off-screen

    def scroll(self):
        # Move both background images
        self.y1 += self.scroll_speed
        self.y2 += self.scroll_speed

        # Reset the position of the background images when they move off-screen
        if self.y1 >= self.image.get_height():
            self.y1 = self.y2 - self.image.get_height()
        if self.y2 >= self.image.get_height():
            self.y2 = self.y1 - self.image.get_height()

    def draw(self, surface):
        # Draw the background images
        surface.blit(self.image, (0, self.y1))
        surface.blit(self.image, (0, self.y2))

import pygame

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, size=(15, 15)):  # Add size parameter
        super().__init__()
        # Load multiple frames of the GIF as separate images
        self.frames = [
            pygame.image.load(f"elements/coin/coin{i}.png").convert_alpha()
            for i in range(1, 5)
        ]  # Assuming the GIF has 4 frames, adjust as needed

        # Resize each frame to the specified size
        self.frames = [pygame.transform.scale(frame, size) for frame in self.frames]

        # Set the initial frame
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 1  # Speed for moving downward
        
        # Create a mask for the bullet image
        self.mask = pygame.mask.from_surface(self.image)

        # Timer to control the animation speed
        self.animation_speed = 0.1  # Adjust to control how fast the frames change
        self.time_since_last_frame = 0

    def update(self):
        # Update the animation based on time
        self.time_since_last_frame += self.animation_speed
        if self.time_since_last_frame >= 1:
            self.time_since_last_frame = 0
            # Cycle to the next frame
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

        # Move the coin downward slowly
        self.rect.y += self.speed

        # Optional: Remove the coin when it goes off-screen (if needed)
        if self.rect.top > 800:  # Assuming screen height is 800
            self.kill()  # Remove the coin when it moves off the screen

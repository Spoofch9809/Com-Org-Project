import pygame

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, x_velocity=0):
        super().__init__()
        # Load multiple frames of the GIF as separate images
        self.frames = [
            pygame.image.load(f"elements/player/bullet/{i}.png").convert_alpha() 
            for i in range(1, 8)
        ]  # Assuming the GIF has 7 frames, adjust as needed
        
        # Set the initial frame
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -20  # Moves up the screen
        self.x_velocity = x_velocity  # Horizontal speed for diagonal bullets
        
        # Create a mask for the bullet image
        self.mask = pygame.mask.from_surface(self.image)
        
        # Timer to control the animation speed
        self.animation_speed = 0.1  # Lower is faster
        self.time_since_last_frame = 0

    def update(self):
        # Move the bullet upwards and apply horizontal velocity
        self.rect.y += self.speed
        self.rect.x += self.x_velocity  # Move left or right based on x_velocity
        
        if self.rect.bottom < 0:
            self.kill()  # Remove the bullet when it goes off-screen

        # Update the animation based on time
        self.time_since_last_frame += self.animation_speed
        if self.time_since_last_frame >= 1:
            self.time_since_last_frame = 0
            # Cycle to the next frame
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
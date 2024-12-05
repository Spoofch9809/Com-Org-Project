import pygame

class Button:
    def __init__(self, x, y, image, action=None, border_thickness=5, cooldown_time=1000):
        self.x = x
        self.y = y
        self.image = image
        self.original_image = image  # Keep the original image for later use
        self.rect = self.image.get_rect(topleft=(x, y))
        self.action = action  # Optional action to be triggered when the button is clicked
        self.border_thickness = border_thickness
        self.cooldown_time = cooldown_time  # Cooldown time in milliseconds
        self.last_click_time = 0  # The time of the last click
        self.is_on_cooldown = False  # Flag to track if the button is on cooldown
        self.alpha = 255  # Initial alpha (fully opaque)

    def draw(self, surface):
        # Draw the border circle
        border_color = (255, 215, 0)  # Example: gold border
        pygame.draw.circle(surface, border_color, self.rect.center, 20, 3)
        
        # If the button is on cooldown, apply transparency
        if self.is_on_cooldown:
            self.alpha = max(50, 255 - (pygame.time.get_ticks() - self.last_click_time) / self.cooldown_time * 255)  # Fade over cooldown time
        else:
            self.alpha = 255  # Full opacity

        # Apply the alpha transparency to the image
        self.image.set_alpha(self.alpha)
        
        # Draw the image with the applied transparency
        #print(f"Alpha value of button: {self.image.get_at((0, 0))[3]}")
        surface.blit(self.image, (self.x, self.y))
        
    def update(self):
        """ Update the cooldown state """
        current_time = pygame.time.get_ticks()  # Get the current time in milliseconds
        if self.is_on_cooldown and current_time - self.last_click_time >= self.cooldown_time:
            self.is_on_cooldown = False  # End the cooldown if enough time has passed

    def handle_key_press(self, event, skill_key, pos):
        """ Handle key press events to trigger skill actions with key """
        if event.type == pygame.KEYDOWN and event.key == skill_key:  # Check if the assigned key is pressed
            if not self.is_on_cooldown:
                self.click(pos)  # Trigger the skill button action if the key matches and cooldown is not active

    def set_alpha(self, alpha_value):
        #print(f"Setting alpha to: {alpha_value}")
        self.image.set_alpha(alpha_value) # Set the alpha value of the button image

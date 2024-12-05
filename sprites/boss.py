import pygame
import math
from sprites.healthbar import HealthBar
from sprites.bullet_boss import BulletBoss, BossShootingPatterns # Import the BulletBoss class

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Load the boss image with transparency
        self.image = pygame.image.load("elements/enemy/boss.png").convert_alpha()
        # Scale the image
        self.image = pygame.transform.scale(self.image, (200, 200))

        # Create a mask for pixel-perfect collision
        self.mask = pygame.mask.from_surface(self.image)

        # Create a rect for positioning
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 1  # Set the speed of the boss

        # Set the health of the boss
        self.hp = 100
        self.health_bar = HealthBar(max_health=self.hp)

        # Shooting attributes
        self.shoot_timer = 0  # Timer to control shooting frequency
        self.shoot_delay = 30  # Delay between shots (in frames)
        self.bullet_group = pygame.sprite.Group()  # Group to hold bullets

        # Angle for infinity movement
        self.angle = 0

    def update(self):
        # Boss will move down to its position and stay still
        if self.rect.y < 75:
            self.rect.y += 2
        # else:
        #     # Infinity sign movement after reaching its initial position
        #     self.angle += 0.05  # Adjust speed of infinity movement here
        #     r = math.sqrt(2) * math.sqrt(math.cos(2 * self.angle))
        #     self.rect.x = 200 + int(r * math.cos(self.angle) * 50)
        #     self.rect.y = 200 + int(r * math.sin(self.angle) * 50)

        # Update the shoot timer
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_delay:
            self.shoot()  # Call the shoot method
            self.shoot_timer = 0

        # Update bullets
        self.bullet_group.update()  # Make sure to call update for bullet group

    def shoot(self):
        # Use a shooting pattern from BossShootingPatterns
        BossShootingPatterns.spread_shooting(self, self.bullet_group, spread_angle=60, num_bullets=5)

    def take_damage(self, amount):
        """Reduce the boss's health by the amount of damage taken."""
        self.hp -= amount
        self.health_bar.take_damage(amount)
        if self.hp <= 0:
            self.kill()  # Remove the boss when health reaches 0

    def draw_health_bar(self, surface):
        # Draw the health bar above the enemy
        self.health_bar.draw(surface, self.rect.centerx - 20, self.rect.top + 200)  # Adjust position as needed

    def draw_bullets(self, surface):
        # Draw the bullets (if needed)
        self.bullet_group.draw(surface)

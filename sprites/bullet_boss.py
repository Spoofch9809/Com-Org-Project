import pygame
import math

# BulletBoss class for boss's bullets with animated frames
class BulletBoss(pygame.sprite.Sprite):
    def __init__(self, x_position, y_position, target_x, target_y):
        super().__init__()

        # Load bullet frames
        self.frames = []
        for i in range(1, 5):  # Assuming you have 4 frames
            frame = pygame.image.load(f"elements/enemy/bullet/1_{i}.png").convert_alpha()  # Update path as needed
            frame = pygame.transform.scale(frame, (10, 30))  # Set the desired size for the bullet
            self.frames.append(frame)

        self.index = 0  # Current frame index
        self.image = self.frames[self.index]  # Set the initial image to the first frame
        self.rect = self.image.get_rect(center=(x_position, y_position))  # Set the initial position
        self.speed = 5  # Set the bullet speed
        
        # Calculate direction to the target
        self.dx = target_x - x_position
        self.dy = target_y - y_position
        distance = math.hypot(self.dx, self.dy)  # Calculate the distance
        
        # Normalize the direction vector and adjust with speed
        if distance > 0:
            self.dx = (self.dx / distance) * self.speed
            self.dy = (self.dy / distance) * self.speed

    def update(self):
        # Move the bullet towards the target
        self.rect.x += self.dx
        self.rect.y += self.dy
        
        # Update the frame for animation
        self.index += 1
        if self.index >= len(self.frames):
            self.index = 0  # Loop back to the first frame
        self.image = self.frames[self.index]  # Update the bullet image to the current frame

        # Remove the bullet when it goes off-screen
        if (self.rect.bottom < 0 or self.rect.top > 800 or
                self.rect.right < 0 or self.rect.left > 400):
            self.kill()

    def draw(self, screen):
        # Draw the bullet to the screen
        screen.blit(self.image, self.rect)

# Boss's shooting patterns
class BossShootingPatterns:
    @staticmethod
    def circular_shooting(boss, bullet_group, num_bullets=5):
        """Shoots bullets in a circular pattern."""
        for i in range(num_bullets):
            angle = i * (360 / num_bullets)  # Divide the full circle by the number of bullets
            target_x = boss.rect.centerx + math.cos(math.radians(angle)) * 200  # Adjust distance as needed
            target_y = boss.rect.centery + math.sin(math.radians(angle)) * 200  # Adjust distance as needed
            bullet = BulletBoss(boss.rect.centerx, boss.rect.centery, target_x, target_y)
            bullet_group.add(bullet)

    @staticmethod
    def spiral_shooting(boss, bullet_group, num_bullets=5, rotation_speed=5):
        """Shoots bullets in a spiral pattern."""
        for i in range(num_bullets):
            angle = (i * (360 / num_bullets) + rotation_speed * (pygame.time.get_ticks() // 100)) % 360
            target_x = boss.rect.centerx + math.cos(math.radians(angle)) * 200  # Adjust distance as needed
            target_y = boss.rect.centery + math.sin(math.radians(angle)) * 200  # Adjust distance as needed
            bullet = BulletBoss(boss.rect.centerx, boss.rect.centery, target_x, target_y)
            bullet_group.add(bullet)

    @staticmethod
    def spread_shooting(boss, bullet_group, spread_angle=60, num_bullets=5):
        """Shoots bullets in a spread pattern (fan shape)."""
        center_angle = 90  # Directly downwards, adjust based on the boss position
        angle_step = spread_angle / (num_bullets - 1)
        start_angle = center_angle - (spread_angle / 2)
        
        for i in range(num_bullets):
            angle = start_angle + i * angle_step
            target_x = boss.rect.centerx + math.cos(math.radians(angle)) * 200  # Adjust distance as needed
            target_y = boss.rect.centery + math.sin(math.radians(angle)) * 200  # Adjust distance as needed
            bullet = BulletBoss(boss.rect.centerx, boss.rect.centery, target_x, target_y)
            bullet_group.add(bullet)

import pygame
import random
from sprites.healthbar import HealthBar
from sprites.bullet_enemy import BulletEnemy

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x_position, pattern=None):
        super().__init__()
        # Load the image from a file
        self.image = pygame.image.load("elements/enemy/ufo.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (100, 100))
        
        # Create a mask for the bullet image
        self.mask = pygame.mask.from_surface(self.image)

        # Set the x position from the passed argument and fixed y position at 0
        self.rect = self.image.get_rect(center=(x_position, 0))
        # self.speed = random.randint(1, 3)
        self.speed = 1
        
        # Add health points for the enemy
        self.hp = 10  # Each enemy starts with 10 health points
        self.health_bar = HealthBar(max_health=self.hp)

        # Set the movement pattern, or randomly select one if not specified
        if pattern is None:
            self.pattern = random.choice(['straight', 'zigzag', 'diagonal'])
        else:
            self.pattern = pattern

        # Additional variables for zigzag and diagonal patterns
        self.direction = random.choice([-1, 1])  # Left or right for zigzag
        self.zigzag_offset = 0  # Zigzag horizontal movement counter
        self.diagonal_speed_x = self.direction * random.randint(1, 3)  # Diagonal movement speed

    def update(self):
        # Move downwards regardless of the pattern
        self.rect.y += self.speed

        # Implement the movement pattern
        if self.pattern == 'straight':
            # For straight pattern, we want to keep the current x position
            pass  # No horizontal movement for straight pattern
        elif self.pattern == 'zigzag':
            # Zigzag pattern: move left and right as it moves down
            self.rect.x += self.direction * 3  # Zigzag left-right movement
            # Reverse direction at certain intervals
            if self.rect.x <= 50 or self.rect.x >= 350:
                self.direction *= -1  # Change direction when hitting screen edge
        elif self.pattern == 'diagonal':
            # Diagonal movement: move diagonally while going down
            self.rect.x += self.diagonal_speed_x  # Move diagonally left or right

        # Remove the enemy when it goes off-screen
        if self.rect.top > 800 or self.rect.right < 0 or self.rect.left > 400:
            self.kill()

    def take_damage(self, amount):
        """Reduce the enemy's health by a specified amount"""
        self.hp -= amount
        self.health_bar.take_damage(amount)
        if self.hp <= 0:
            self.kill()  # Remove the enemy when health is zero
            
    def shoot(self, player_x, player_y):
        bullet = BulletEnemy(self.rect.centerx, self.rect.bottom, player_x, player_y)  # Spawn the bullet towards the player
        return bullet

            
    def draw_health_bar(self, surface):
        # Draw the health bar above the enemy
        self.health_bar.draw(surface, self.rect.centerx - 20, self.rect.top + 75)  # Adjust position as needed
            
def spawn_enemy_pack(pattern, player_x):
    enemy_pack = pygame.sprite.Group()  # Group to store the pack of enemies
    row_count = 3  # Number of rows in the triangle
    gap = 40  # Horizontal gap between each enemy
    vertical_gap = 30  # Vertical gap between rows

    # Create enemies in a triangular formation only for the straight pattern
    if pattern == 'straight':
        # Generate a suitable starting x position that does not overlap with the player
        while True:
            start_x = random.randint(100, 300)  # Random starting x position
            # Check if start_x is not too close to the player's x position
            if abs(start_x - player_x) > 40:  # Adjust 40 based on desired spacing
                break

        # Create enemies in the desired downward triangle formation
        for row in range(row_count):  # Iterate through the rows
            y_position = row * vertical_gap  # Set the y position for each row based on the vertical gap

            if row == 0:
                # First row: spawn enemies at the edges
                enemy_left = Enemy(start_x - gap // 1, pattern)  # Left enemy
                enemy_right = Enemy(start_x + gap // 1, pattern)  # Right enemy
                enemy_left.rect.y = y_position  # Set the y position
                enemy_right.rect.y = y_position  # Set the y position
                enemy_pack.add(enemy_left, enemy_right)  # Add both enemies to the pack

            elif row == 1:
                # Second row: spawn enemies in between the edges
                enemy_left = Enemy(start_x - gap // 2, pattern)  # Left enemy
                enemy_right = Enemy(start_x + gap // 2, pattern)  # Right enemy
                enemy_left.rect.y = y_position  # Set the y position
                enemy_right.rect.y = y_position  # Set the y position
                enemy_pack.add(enemy_left, enemy_right)  # Add both enemies to the pack

            elif row == 2:
                # Third row: spawn one enemy in the center
                enemy = Enemy(start_x, pattern)  # Center enemy
                enemy.rect.y = y_position  # Set the y position
                enemy_pack.add(enemy)  # Add the enemy to the pack

    else:
        # For zigzag and diagonal patterns, spawn a single enemy
        while True:
            x_position = random.randint(50, 350)  # Random x position within screen width
            # Check if x_position is not too close to the player's x position
            if abs(x_position - player_x) > 40:  # Adjust 40 based on desired spacing
                break

        enemy = Enemy(x_position, pattern)  # Create a single enemy
        enemy_pack.add(enemy)  # Add to the group (still using group for consistency)

    return enemy_pack
import pygame
import smbus
import time
from sprites.bullet import Bullet

# Initialize SMBus for gyroscope
bus = smbus.SMBus(1)
DEVICE_ADDRESS = 0x68
PWR_MGMT_1 = 0x6B
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45

# Initialize MPU6050
bus.write_byte_data(DEVICE_ADDRESS, PWR_MGMT_1, 0)

def read_raw_data(addr):
    high = bus.read_byte_data(DEVICE_ADDRESS, addr)
    low = bus.read_byte_data(DEVICE_ADDRESS, addr + 1)
    value = (high << 8) | low
    return value - 65536 if value > 32768 else value

def read_gyro():
    gyro_x = -read_raw_data(GYRO_XOUT_H) / 131.0 / 15  # Adjust division for sensitivity if needed
    gyro_y = read_raw_data(GYRO_YOUT_H) / 131.0 / 15
    return gyro_x, gyro_y

GYRO_SENSITIVITY = 5  # Controls how sensitive the movement is

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()
        self.image = pygame.image.load("elements/player/aircraft_green.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))
        
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=(400 // 2, 800 - 50))
        self.speed = 5
        self.hp = 100
        self.max_hp = 100
        self.coins = 0
        self.three_way_active = False
        self.three_way_duration = 5  # 5 seconds
        self.three_way_cost = 30
        self.three_way_cooldown = 10  # 10 seconds cooldown
        self.three_way_last_used = 0

        self.hp_restore_cost = 10
        self.hp_restore_amount = 20
        self.hp_restore_cooldown = 10  # 10 seconds cooldown
        self.hp_restore_last_used = 0

    def update(self):
        # Get gyroscope data for movement
        gyro_x, gyro_y = read_gyro()
        
        # Update position based on gyroscope values
        new_x = self.rect.x + int(gyro_x * GYRO_SENSITIVITY)
        new_y = self.rect.y + int(gyro_y * GYRO_SENSITIVITY)
        
        # Keep the player within the screen boundaries
        self.rect.x = max(0, min(400 - self.rect.width, new_x))
        self.rect.y = max(0, min(800 - self.rect.height, new_y))

    def shoot(self):
        if self.three_way_active:
            # Three-way shooting ability active
            left_bullet = Bullet(self.rect.centerx, self.rect.top, -1)
            center_bullet = Bullet(self.rect.centerx, self.rect.top, 0)
            right_bullet = Bullet(self.rect.centerx, self.rect.top, 1)
            return [left_bullet, center_bullet, right_bullet]
        else:
            # Normal shooting
            return [Bullet(self.rect.centerx, self.rect.top, 0)]

    def activate_three_way(self):
        current_time = time.time()
        if self.coins >= self.three_way_cost and current_time - self.three_way_last_used >= self.three_way_cooldown:
            self.coins -= self.three_way_cost
            self.three_way_active = True
            self.three_way_last_used = current_time
            pygame.time.set_timer(pygame.USEREVENT + 1, self.three_way_duration * 1000)  # Set timer for 5 seconds

    def deactivate_three_way(self):
        self.three_way_active = False

    def restore_hp(self):
        current_time = time.time()
        if self.coins >= self.hp_restore_cost and current_time - self.hp_restore_last_used >= self.hp_restore_cooldown:
            self.coins -= self.hp_restore_cost
            self.hp = min(self.hp + self.hp_restore_amount, 100)  # Cap HP at 100
            self.hp_restore_last_used = current_time

    def set_alpha(self, alpha_value):
        self.image.set_alpha(alpha_value)

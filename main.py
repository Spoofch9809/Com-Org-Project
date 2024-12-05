import pygame
import random
import RPi.GPIO as GPIO
from sprites.player import Player
from sprites.enemy import Enemy, spawn_enemy_pack
from sprites.bullet import Bullet
from sprites.bullet_enemy import BulletEnemy
from sprites.coin import Coin
from sprites.boss import Boss
from sprites.healthbar import HealthBar
from sprites.button import Button
from pages.menu import Menu
from pages.background import Background
from sprites.bullet_boss import BossShootingPatterns
from sprites.controller import Controller

# Initialize Pygame
pygame.init()
controller = Controller()
beeping_active = False
# Constants
heal_LED = 10
skill_LED = 4
GPIO.setup(heal_LED, GPIO.OUT)
GPIO.setup(skill_LED, GPIO.OUT)

SCREEN_WIDTH, SCREEN_HEIGHT = 400, 800
WHITE = (255, 255, 255)
FPS = 120
PLAYER_HIT_COOLDOWN = 3000
BLINK_INTERVAL = 500

# Skill Constants
TRIPLE_SHOT_COST = 3
TRIPLE_SHOT_DURATION = 5000  # 5 seconds
TRIPLE_SHOT_COOLDOWN = 10000  # 10 seconds
HEALTH_BOOST_COST = 1
HEALTH_BOOST_AMOUNT = 20
HEALTH_BOOST_COOLDOWN = 10000  # 10 seconds

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("1945 Air Force Clone")

# Initialize player, groups, and score
player = Player(width=80, height=80)
all_sprites = pygame.sprite.Group(player)
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
coins = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
boss_bullet = pygame.sprite.Group()

# Initialize the menu
menu = Menu(screen)
menu_active = False

# Load background images using the Background class
bg_layer1 = Background('elements/background/background1.png', (SCREEN_WIDTH, SCREEN_HEIGHT), scroll_speed1=0.5)
bg_layer2 = Background('elements/background/background1.png', (SCREEN_WIDTH, SCREEN_HEIGHT), scroll_speed1=0.5)

# Set up clock and game variables
clock = pygame.time.Clock()
score = 0
total_coins = 0
boss_spawned = False
game_over = False
last_hit_time = 0
blink_start_time = 0
is_blinking = False

# Create font for button text
button_font = pygame.font.Font(None, 30)

# Functions to handle button actions
def activate_triple_shot():
    global triple_shot_active, triple_shot_start_time, total_coins, last_triple_shot_time
    current_time = pygame.time.get_ticks()
    if total_coins >= TRIPLE_SHOT_COST and current_time - last_triple_shot_time >= TRIPLE_SHOT_COOLDOWN:
        triple_shot_active = True
        triple_shot_start_time = current_time
        total_coins -= TRIPLE_SHOT_COST
        last_triple_shot_time = current_time
        #print("Triple Shot activated!")

def activate_health_boost():
    global total_coins, last_health_boost_time
    current_time = pygame.time.get_ticks()
    if total_coins >= HEALTH_BOOST_COST and current_time - last_health_boost_time >= HEALTH_BOOST_COOLDOWN:
        player.hp += HEALTH_BOOST_AMOUNT
        total_coins -= HEALTH_BOOST_COST
        last_health_boost_time = current_time
        #print("Health Boost activated! Player HP:", player.hp)

# Load button images
triple_shot_button_img = pygame.image.load(f'elements/ui/button_potion.png').convert_alpha()
health_boost_button_img = pygame.image.load(f'elements/ui/button_hp.png').convert_alpha()

# Create button objects
triple_shot_button = Button(SCREEN_WIDTH - 50, SCREEN_HEIGHT - 60, triple_shot_button_img, action=activate_triple_shot, cooldown_time=TRIPLE_SHOT_COOLDOWN)
health_boost_button = Button(SCREEN_WIDTH - 95, SCREEN_HEIGHT - 60, health_boost_button_img, action=activate_health_boost, cooldown_time=HEALTH_BOOST_COOLDOWN)

# Skill state variables
triple_shot_active = False
triple_shot_start_time = 0
last_triple_shot_time = -TRIPLE_SHOT_COOLDOWN  # Ensures it's ready at start

last_health_boost_time = -HEALTH_BOOST_COOLDOWN  # Ensures it's ready at start


# Set up enemy spawn timer
enemy_spawn_timer = 1600
pygame.time.set_timer(pygame.USEREVENT, enemy_spawn_timer)

# Set up font for displaying score and coins
font = pygame.font.Font(None, 36)

# Separate shooting cooldown times for player and boss
boss_shoot_cooldown = 80
player_shoot_cooldown = 100
player_last_shot_time = 0
boss_last_shot_time = 0

# Add a variable to track the last spawn time
last_spawn_time = 0
spawn_cooldown = 2000

# Boss shooting pattern variables
boss_shooting_patterns = [
    BossShootingPatterns.circular_shooting,
    BossShootingPatterns.spiral_shooting,
    BossShootingPatterns.spread_shooting
]
current_pattern_index = 0
pattern_duration = 5000
last_pattern_switch_time = 0

# Add constants for score threshold and cooldowns
BOSS_SPAWN_THRESHOLD = 200
current_score_threshold = BOSS_SPAWN_THRESHOLD

# Main game loop
running = True
while running:
    clock.tick(FPS)
    elapsed_time = clock.tick(FPS)

    # Update backgrounds
    bg_layer1.scroll()
    bg_layer2.scroll()

    # Draw background layers
    bg_layer1.draw(screen)
    bg_layer2.draw(screen)

    current_time = pygame.time.get_ticks()
    controller.check_hp_and_control_buzzer(player)
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.USEREVENT:
            # Spawn enemies if boss is not on screen
            if not boss_spawned:
                if current_time - last_spawn_time >= spawn_cooldown:
                    pattern = random.choice(['straight', 'zigzag', 'diagonal'])
                    enemy_pack = spawn_enemy_pack(pattern, player.rect.centerx)
                    all_sprites.add(enemy_pack)
                    enemies.add(enemy_pack)
                    last_spawn_time = current_time

            # Enemies shoot
            for enemy in enemies:
                if random.random() < 0.25:
                    bullet = enemy.shoot(player.rect.centerx, player.rect.centery)
                    if bullet:
                        enemy_bullets.add(bullet)
                        all_sprites.add(bullet)

    # Handle input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        menu_active = not menu_active
        pygame.time.wait(200)

    # Activate Triple Shot (press Z)
    if GPIO.input(controller.TRIPLE_SHOT_BUTTON) == GPIO.LOW and total_coins >= TRIPLE_SHOT_COST and current_time - last_triple_shot_time >= TRIPLE_SHOT_COOLDOWN:
        triple_shot_active = True
        triple_shot_start_time = current_time
        total_coins -= TRIPLE_SHOT_COST
        last_triple_shot_time = current_time
        triple_shot_button_img.set_alpha(255)  # Reset to full opacity when activated
        ##print("Triple Shot activated!")

    # Update the alpha of the button during cooldown
    if current_time - triple_shot_start_time < TRIPLE_SHOT_COOLDOWN:
        # If cooldown is still active, dim the button
        alpha_value = max(1, 255 * (TRIPLE_SHOT_COOLDOWN - (current_time - triple_shot_start_time)) / TRIPLE_SHOT_COOLDOWN)
        GPIO.output(skill_LED, 0)
        triple_shot_button_img.set_alpha(alpha_value)
    else:
        # Once the cooldown is over, restore full opacity
        triple_shot_button_img.set_alpha(255)
        GPIO.output(skill_LED, 1)

    # Activate Health Boost (press X)
    if GPIO.input(controller.HEALTH_BUTTON) == GPIO.LOW and total_coins >= HEALTH_BOOST_COST and current_time - last_health_boost_time >= HEALTH_BOOST_COOLDOWN and player.hp < player.max_hp:
        if player.hp < player.max_hp:
            if player.hp + HEALTH_BOOST_AMOUNT > player.max_hp:
                player.hp = player.max_hp
            else:
                player.hp += HEALTH_BOOST_AMOUNT
        total_coins -= HEALTH_BOOST_COST
        last_health_boost_time = current_time
        health_boost_button_img.set_alpha(255)  # Reset to full opacity when activated
        #print("Health Boost activated! Player HP:", player.hp)

    # Update the alpha of the health boost button during cooldown
    if current_time - last_health_boost_time < HEALTH_BOOST_COOLDOWN:
        # If cooldown is still active, dim the button
        alpha_value = max(1, 255 * (HEALTH_BOOST_COOLDOWN - (current_time - last_health_boost_time)) / HEALTH_BOOST_COOLDOWN)
        health_boost_button_img.set_alpha(alpha_value)
        GPIO.output(heal_LED, 0)
    else:
        # Once the cooldown is over, restore full opacity
        health_boost_button_img.set_alpha(255)
        GPIO.output(heal_LED, 1)
        # Deactivate Triple Shot after duration
        if triple_shot_active and current_time - triple_shot_start_time >= TRIPLE_SHOT_DURATION:
            triple_shot_active = False
            #print("Triple Shot deactivated")

    # Player shooting
    if current_time - player_last_shot_time >= player_shoot_cooldown:
        if triple_shot_active:
            # Three-way shot
            bullet1 = Bullet(player.rect.centerx, player.rect.top, -1)
            bullet2 = Bullet(player.rect.centerx, player.rect.top, 0)
            bullet3 = Bullet(player.rect.centerx, player.rect.top, 1)
            for bullet in (bullet1, bullet2, bullet3):
                if bullet:
                    all_sprites.add(bullet)
                    bullets.add(bullet)
        else:
            # Normal shot
            bullet = player.shoot()
            if bullet:
                all_sprites.add(bullet)
                bullets.add(bullet)
        player_last_shot_time = current_time
        
    # Menu logic
    if menu_active:
        menu.run()
        menu_active = not menu_active
    else:
        all_sprites.update()
        boss_group.update()
        boss_bullet.update()
        enemy_bullets.update()
        triple_shot_button.update()
        health_boost_button.update()

        # Player shooting
        if current_time - player_last_shot_time >= player_shoot_cooldown:
            bullet = player.shoot()
            if bullet:
                all_sprites.add(bullet)
                bullets.add(bullet)
            player_last_shot_time = current_time

        # Enemy collisions with player bullets
        hits = pygame.sprite.groupcollide(enemies, bullets, False, True, collided=pygame.sprite.collide_mask)
        for enemy, bullets_hit in hits.items():
            for bullet in bullets_hit:
                enemy.take_damage(1)
                if enemy.hp <= 0:
                    enemy.kill()
                    score += 10
                    coin = Coin(enemy.rect.centerx, enemy.rect.centery)
                    all_sprites.add(coin)
                    coins.add(coin)

        # Boss spawning logic based on score threshold
        if score >= current_score_threshold and not boss_spawned:
            #print("Spawning Boss!")
            boss = Boss(SCREEN_WIDTH // 2, -50)
            all_sprites.add(boss)
            boss_group.add(boss)
            boss_spawned = True
            current_score_threshold += BOSS_SPAWN_THRESHOLD  # Increment threshold for next boss spawn

        # Boss shooting pattern logic
        if boss_spawned and boss_group:
            boss = boss_group.sprites()[0]

            if current_time - last_pattern_switch_time >= pattern_duration:
                current_pattern_index = (current_pattern_index + 1) % len(boss_shooting_patterns)
                last_pattern_switch_time = current_time

            if current_time - boss_last_shot_time >= boss_shoot_cooldown:
                boss_shooting_patterns[current_pattern_index](boss, enemy_bullets)
                boss_last_shot_time = current_time

        # Handle collisions with boss
        boss_hits = pygame.sprite.groupcollide(boss_group, bullets, False, True, collided=pygame.sprite.collide_mask)
        for boss, bullets_hit in boss_hits.items():
            for bullet in bullets_hit:
                boss.take_damage(1)
                if boss.hp <= 0:
                    boss.kill()
                    score += 50  # Extra points for defeating boss
                    boss_spawned = False  # Allow enemies to spawn again after boss death

        # Player collecting coins
        collected_coins = pygame.sprite.spritecollide(player, coins, True, collided=pygame.sprite.collide_mask)
        total_coins += len(collected_coins)

        # Player hit by enemies or boss
        if (pygame.sprite.spritecollideany(player, enemies, collided=pygame.sprite.collide_mask) or
        pygame.sprite.spritecollideany(player, boss_group, collided=pygame.sprite.collide_mask)) and \
        (current_time - last_hit_time > PLAYER_HIT_COOLDOWN):
            
            controller.blink_twice()
            controller.play_buzzer(0.2)
            
            damage = 20
            player.hp -= damage
            last_hit_time = current_time
            blink_start_time = current_time
            is_blinking = True

            # Trigger shake effect
            shake_duration = 1000  # Duration of the shake (in milliseconds)
            shake_timer = current_time  # Start the timer
            #print(f"Player hit! Damage taken: {damage}. Player HP: {player.hp}")
            if player.hp <= 0:
                game_over = True

        # Player blinking effect after being hit
        if is_blinking:
            elapsed_blink_time = current_time - blink_start_time
            if elapsed_blink_time < PLAYER_HIT_COOLDOWN:
                if (elapsed_blink_time // BLINK_INTERVAL) % 2 == 0:
                    player.set_alpha(0)
                else:
                    player.set_alpha(255)
            else:
                is_blinking = False
                player.set_alpha(255)

        # Player hit by enemy bullets
        player_bullet_hits = pygame.sprite.spritecollide(player, enemy_bullets, True, collided=pygame.sprite.collide_mask)
        for bullet in player_bullet_hits:
            damage = 2
            player.hp -= damage
            #print(f"Player hit by enemy bullet! Damage taken: {damage}. Player HP: {player.hp}")
            if player.hp <= 0:
                game_over = True

        # Game over logic
        if game_over:
            screen.fill((0, 0, 0))
            game_over_text = font.render("Game Over!", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 20))
            pygame.display.flip()
            pygame.time.wait(2000)
            pygame.quit()
            running = False
        else:
            # Draw all sprites
            all_sprites.draw(screen)
            boss_group.draw(screen)
            

            # Draw health bars for enemies and boss
            for enemy in enemies:
                enemy.draw_health_bar(screen)
            for boss in boss_group:
                boss.draw_health_bar(screen)

            # Draw bullets for the boss
            for bullet in enemy_bullets:
                bullet.draw(screen)
            
            for bullet in boss_bullet:
                bullet.draw(screen)
                

            # Display score, coins, health, and FPS
            score_text = font.render(f"Score: {score}", False, (255, 255, 255))
            coins_text = font.render(f"Coins: {total_coins}", False, (255, 255, 255))
            health_text = font.render(f"HP: {player.hp}", False, (255, 255, 255))
            fps_text = font.render(f"FPS: {int(clock.get_fps())}", False, (255, 255, 255))
            controller.update_health_led(player)
            screen.blit(score_text, (10, 10))
            screen.blit(coins_text, (10, 40))
            screen.blit(health_text, (10, 70))
            screen.blit(fps_text, (10, 100))
            
            # Draw the skill buttons
            triple_shot_button.draw(screen)
            health_boost_button.draw(screen)
            
            # Refresh the display
            pygame.display.flip()

# Quit Pygame
pygame.quit()
GPIO.cleanup()
exit()


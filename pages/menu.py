import pygame

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.buttons = {
            "Resume": self.resume_game,
            "Settings": self.open_settings,
            "Quit": self.quit_game
        }
        self.selected_button = 0
        self.button_rects = []
        self.cooldown_time = 200  # Time in milliseconds for the cooldown
        self.last_switch_time = pygame.time.get_ticks()
        self.last_enter_time = pygame.time.get_ticks()  # Track last enter key press
        self.in_menu = True

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.button_rects.clear()  # Clear the button_rects for each draw call
        for i, (text, _) in enumerate(self.buttons.items()):
            color = (255, 0, 0) if i == self.selected_button else (255, 255, 255)
            button_surface = self.font.render(text, True, color)
            button_rect = button_surface.get_rect(center=(self.screen.get_width() // 2, 200 + i * 50))
            self.screen.blit(button_surface, button_rect)
            self.button_rects.append(button_rect)  # Store the rect for potential future use

    def handle_input(self):
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()

        # Handle button selection with arrow keys
        if keys[pygame.K_DOWN] and current_time - self.last_switch_time > self.cooldown_time:
            self.selected_button = (self.selected_button + 1) % len(self.buttons)
            self.last_switch_time = current_time

        if keys[pygame.K_UP] and current_time - self.last_switch_time > self.cooldown_time:
            self.selected_button = (self.selected_button - 1) % len(self.buttons)
            self.last_switch_time = current_time

        # Handle "Enter" key press
        if keys[pygame.K_RETURN] and current_time - self.last_enter_time > self.cooldown_time:
            self.last_enter_time = current_time  # Update the last enter time
            list(self.buttons.values())[self.selected_button]()  # Call the corresponding method

    def resume_game(self):
        print("Resume is selected")
        self.in_menu = False

    def open_settings(self):
        print("Settings menu (not implemented yet)")

    def quit_game(self):
        GPIO.cleanup()
        pygame.quit()
        exit()

    def run(self):
        print("Menu is running")
        while self.in_menu:
            self.draw()
            self.handle_input()
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
        self.in_menu = True

import RPi.GPIO as GPIO
import time
import threading

class Controller:
    def __init__(self):
        self.TRIPLE_SHOT_BUTTON = 17
        self.HEALTH_BUTTON = 18
        self.R_PIN = 5
        self.G_PIN = 6
        self.B_PIN = 13
        self.BUZZER_PIN = 24
        self.BUZZER_PIN2 = 12

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.TRIPLE_SHOT_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.HEALTH_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.R_PIN, GPIO.OUT)
        GPIO.setup(self.G_PIN, GPIO.OUT)
        GPIO.setup(self.B_PIN, GPIO.OUT)
        GPIO.setup(self.BUZZER_PIN, GPIO.OUT)
        GPIO.setup(self.BUZZER_PIN2, GPIO.OUT)
        
        self.buzzer_pwm = GPIO.PWM(self.BUZZER_PIN, 1000)
        self.buzzer_pwm2 = GPIO.PWM(self.BUZZER_PIN2, 1000)
        self.beeping_active = False
        self.buzzer_thread = None
    
    def set_led_color(self, r, g, b):
        GPIO.output(self.R_PIN, r)
        GPIO.output(self.G_PIN, g)
        GPIO.output(self.B_PIN, b)
    
    def blink_twice(self, color=(1, 0, 1), blink_duration=0.1, pause_duration=0.1):
        for _ in range(2): 
            self.set_led_color(*color)  
            time.sleep(blink_duration)  
            self.set_led_color(0, 0, 0) 
            time.sleep(pause_duration)

    def play_buzzer(self, duration=0.1, pause=0.1, volume=100):
        self.buzzer_pwm2.start(volume) 
        for _ in range(2):  
            self.buzzer_pwm2.ChangeDutyCycle(volume) 
            time.sleep(duration) 
            self.buzzer_pwm2.ChangeDutyCycle(0) 
            time.sleep(pause)  
        self.buzzer_pwm2.stop() 

    def update_health_led(self, player):
        if player.hp > 70:
            self.set_led_color(0, 1, 0)
            #self.set_led_color(1, 1, 1)
        elif 50 < player.hp <= 70:
            self.set_led_color(1, 1, 0)
            #self.set_led_color(1, 1, 0)
        else:
            self.set_led_color(1, 0, 0)
            #self.set_led_color(1, 0, 0)
        
    def play_continuous_buzzer(self):
        while self.beeping_active:
            #self.buzzer_pwm.ChangeFrequency(999999)
            self.buzzer_pwm.start(50)  
            time.sleep(0.3)
            self.buzzer_pwm.stop()
            time.sleep(0.3)

    def check_hp_and_control_buzzer(self, player):
        """Check HP and start or stop the buzzer beeping accordingly."""
        if player.hp <= 50:
            if not self.beeping_active:
                self.beeping_active = True
                if self.buzzer_thread is None or not self.buzzer_thread.is_alive():
                    self.buzzer_thread = threading.Thread(target=self.play_continuous_buzzer, daemon=True)
                    self.buzzer_thread.start()
        else:
            self.beeping_active = False
            if self.buzzer_pwm:
                self.buzzer_pwm.stop()
        

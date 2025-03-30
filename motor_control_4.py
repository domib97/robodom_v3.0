import RPi.GPIO as GPIO
import time
import threading
import pygame
import sys

# Globaler Parameter für den PWM-Duty-Cycle
MAX_DUTY_CYCLE = 100

# GPIO initialisieren
GPIO.setmode(GPIO.BCM)

# Definition der GPIO-Pins für jeden Motor
MOTOR_PINS = {
    1: {'EN': 12, 'IN1': 5,  'IN2': 6},
    2: {'EN': 18, 'IN1': 16, 'IN2': 20},
    3: {'EN': 13, 'IN1': 21, 'IN2': 26},
    4: {'EN': 19, 'IN1': 23, 'IN2': 24}
}

class Motor:
    def __init__(self, EN, IN1, IN2, reversed=False):
        self.en_pin = EN
        self.in1_pin = IN1
        self.in2_pin = IN2
        self.reversed = reversed

        # Initialisiere die GPIO-Pins
        GPIO.setup(self.en_pin, GPIO.OUT)
        GPIO.setup(self.in1_pin, GPIO.OUT)
        GPIO.setup(self.in2_pin, GPIO.OUT)

        # Erstelle und starte das PWM-Signal
        self.pwm = GPIO.PWM(self.en_pin, 1000)
        self.pwm.start(0)

    def set_direction(self, direction):
        # Falls der Motor invertiert ist, kehre die Richtung um
        if self.reversed:
            if direction == 'forward':
                direction = 'backward'
            elif direction == 'backward':
                direction = 'forward'
        if direction == 'forward':
            GPIO.output(self.in1_pin, GPIO.HIGH)
            GPIO.output(self.in2_pin, GPIO.LOW)
        elif direction == 'backward':
            GPIO.output(self.in1_pin, GPIO.LOW)
            GPIO.output(self.in2_pin, GPIO.HIGH)
        else:  # Stop
            GPIO.output(self.in1_pin, GPIO.LOW)
            GPIO.output(self.in2_pin, GPIO.LOW)
        # Debug: print(f"Motor {self.en_pin} Richtung: {direction}")

    def set_speed(self, speed):
        speed = max(0, min(speed, MAX_DUTY_CYCLE))
        self.pwm.ChangeDutyCycle(speed)
        # Debug: print(f"Motor {self.en_pin} Geschwindigkeit: {speed}")

    def stop(self):
        self.set_speed(0)
        self.pwm.stop()

class MecanumRobot:
    def __init__(self):
        # Motor 2 ist invertiert, da er physisch umgekehrt montiert/verkabelt wurde.
        self.motors = {
            1: Motor(**MOTOR_PINS[1]),
            2: Motor(**MOTOR_PINS[2], reversed=True),
            3: Motor(**MOTOR_PINS[3]),
            4: Motor(**MOTOR_PINS[4])
        }

    def stop_all(self):
        for motor in self.motors.values():
            motor.stop()
        GPIO.cleanup()
        print("Alle Motoren gestoppt und GPIO aufgeräumt.")

def live_control(robot):
    """
    Liest den Xbox-Controller via Pygame aus und berechnet anhand der Achsenwerte
    für Translation (x, y) und Rotation (r) die gewünschten Geschwindigkeiten und Richtungen
    der einzelnen Motoren. Anschließend werden diese Werte direkt an den Motoren gesetzt.
    """
    pygame.init()
    pygame.joystick.init()
    try:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        print(f"Verbunden mit {joystick.get_name()}")
    except pygame.error:
        print("Kein Xbox-Controller gefunden.")
        sys.exit()

    clock = pygame.time.Clock()
    try:
        while True:
            # Pygame-Ereignisse verarbeiten
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise KeyboardInterrupt

            # Joystick-Achsen auslesen:
            # Linker Stick: Achse 0 (X) und Achse 1 (Y, invertiert, da up = negativ)
            # Rechter Stick: Achse 2 (Rotation, hier als horizontale Achse genutzt)
            x = joystick.get_axis(0)
            y = -joystick.get_axis(1)
            r = -joystick.get_axis(2)

            # Einfache Deadzone-Behandlung
            threshold = 0.1
            if abs(x) < threshold: x = 0
            if abs(y) < threshold: y = 0
            if abs(r) < threshold: r = 0

            # Mecanum-Drive Formel:
            # Motor 1 (Front Left) = y + x + r
            # Motor 2 (Front Right) = y - x - r
            # Motor 3 (Rear Left) = y - x + r
            # Motor 4 (Rear Right) = y + x - r
            m1_val = y + x + r
            m2_val = y - x - r
            m3_val = y - x + r
            m4_val = y + x - r

            # Normierung, falls Werte den MAX_DUTY_CYCLE überschreiten
            max_val = max(abs(m1_val), abs(m2_val), abs(m3_val), abs(m4_val), 1)
            scale = MAX_DUTY_CYCLE / max_val

            m1_speed = min(MAX_DUTY_CYCLE, abs(m1_val * scale))
            m2_speed = min(MAX_DUTY_CYCLE, abs(m2_val * scale))
            m3_speed = min(MAX_DUTY_CYCLE, abs(m3_val * scale))
            m4_speed = min(MAX_DUTY_CYCLE, abs(m4_val * scale))

            m1_dir = 'forward' if m1_val >= 0 else 'backward'
            m2_dir = 'forward' if m2_val >= 0 else 'backward'
            m3_dir = 'forward' if m3_val >= 0 else 'backward'
            m4_dir = 'forward' if m4_val >= 0 else 'backward'

            # Setze die Motoren in Echtzeit
            robot.motors[1].set_direction(m1_dir)
            robot.motors[1].set_speed(m1_speed)

            robot.motors[2].set_direction(m2_dir)
            robot.motors[2].set_speed(m2_speed)

            robot.motors[3].set_direction(m3_dir)
            robot.motors[3].set_speed(m3_speed)

            robot.motors[4].set_direction(m4_dir)
            robot.motors[4].set_speed(m4_speed)

            # Optional: Debug-Ausgabe der Werte
            # print(f"Motor1: {m1_dir} {m1_speed:.1f}, Motor2: {m2_dir} {m2_speed:.1f}, "
            #       f"Motor3: {m3_dir} {m3_speed:.1f}, Motor4: {m4_dir} {m4_speed:.1f}")

            clock.tick(60)
    except KeyboardInterrupt:
        pass
    finally:
        robot.stop_all()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    robot = MecanumRobot()
    live_control(robot)

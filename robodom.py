#!/usr/bin/env python3
import os
import sys
import time
import threading
import subprocess
import pygame
import RPi.GPIO as GPIO
from flask import Flask, render_template_string, request

# ----- Steuerungs-Skript: Motorensteuerung -----
MAX_DUTY_CYCLE = 100
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

        GPIO.setup(self.en_pin, GPIO.OUT)
        GPIO.setup(self.in1_pin, GPIO.OUT)
        GPIO.setup(self.in2_pin, GPIO.OUT)

        self.pwm = GPIO.PWM(self.en_pin, 1000)
        self.pwm.start(0)

    def set_direction(self, direction):
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

    def set_speed(self, speed):
        speed = max(0, min(speed, MAX_DUTY_CYCLE))
        self.pwm.ChangeDutyCycle(speed)

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

class RobotController:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.robot = MecanumRobot()

    def live_control(self):
        """
        Liest den Xbox-Controller via Pygame aus und steuert in Echtzeit
        die Motoren des Mecanum-Roboters.
        """
        pygame.init()
        pygame.joystick.init()
        try:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            print(f"Verbunden mit {joystick.get_name()}")
        except pygame.error as e:
            print("Kein Xbox-Controller gefunden. Bitte Controller verbinden.")
            # Hier nicht das ganze Programm beenden – stattdessen einfach zurückkehren.
            return

        clock = pygame.time.Clock()
        try:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise KeyboardInterrupt

                # Joystick-Achsen auslesen
                x = joystick.get_axis(0)
                y = -joystick.get_axis(1)
                r = -joystick.get_axis(2)

                # Einfache Deadzone
                threshold = 0.1
                if abs(x) < threshold: x = 0
                if abs(y) < threshold: y = 0
                if abs(r) < threshold: r = 0

                # Mecanum-Drive Formel
                m1_val = y + x + r
                m2_val = y - x - r
                m3_val = y - x + r
                m4_val = y + x - r

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

                # Setze die Motoren
                self.robot.motors[1].set_direction(m1_dir)
                self.robot.motors[1].set_speed(m1_speed)
                self.robot.motors[2].set_direction(m2_dir)
                self.robot.motors[2].set_speed(m2_speed)
                self.robot.motors[3].set_direction(m3_dir)
                self.robot.motors[3].set_speed(m3_speed)
                self.robot.motors[4].set_direction(m4_dir)
                self.robot.motors[4].set_speed(m4_speed)

                clock.tick(60)
        except KeyboardInterrupt:
            print("Manual Control unterbrochen.")
        finally:
            self.robot.stop_all()
            pygame.quit()

# ----- Flask-Webfrontend -----
class WebInterface:
    def __init__(self):
        self.app = Flask(__name__)
        self.controller = RobotController()
        self.setup_routes()

    def setup_routes(self):
        html_template = """
        <!doctype html>
        <html lang="de">
          <head>
            <meta charset="utf-8">
            <title>Robodom Steuerung</title>
          </head>
          <body>
            <h1>Modus auswählen</h1>
            <form action="/mode" method="post">
              <button name="mode" value="exploring" type="submit">Exploring</button>
              <button name="mode" value="manual" type="submit">Manual</button>
              <button name="mode" value="face-detection" type="submit">Face-Detection</button>
              <button name="mode" value="music" type="submit">Music</button>
            </form>
          </body>
        </html>
        """
        @self.app.route("/")
        def index():
            return html_template

        @self.app.route("/mode", methods=["POST"])
        def mode():
            selected_mode = request.form.get("mode")
            if selected_mode == "manual":
                # Starte den Manual-Modus in einem separaten Thread
                threading.Thread(target=self.controller.live_control, daemon=True).start()
                message = "Manual Mode gestartet."
            elif selected_mode == "exploring":
                message = "Exploring Mode ausgewählt. (Noch nicht implementiert)"
            elif selected_mode == "face-detection":
                message = "Face-Detection Mode ausgewählt. (Noch nicht implementiert)"
            elif selected_mode == "music":
                message = "Music Mode ausgewählt. (Noch nicht implementiert)"
            else:
                message = "Unbekannter Modus."
            return f"{message} <br><br><a href='/'>Zurück</a>"

    def run(self, host="0.0.0.0", port=8069):
        self.app.run(host=host, port=port)

if __name__ == "__main__":
    web_interface = WebInterface()
    web_interface.run()

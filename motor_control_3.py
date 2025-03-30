import RPi.GPIO as GPIO
import time
import threading

# GPIO-Konfiguration
GPIO.setmode(GPIO.BCM)
MAX_DUTY_CYCLE = 100

# Definition der GPIO-Pins für jeden Motor
MOTOR_PINS = {
    1: {'EN': 12, 'IN1': 5,  'IN2': 6},
    2: {'EN': 18, 'IN1': 16, 'IN2': 20},
    3: {'EN': 13, 'IN1': 21, 'IN2': 26},
    4: {'EN': 19, 'IN1': 23, 'IN2': 24}
}

class Motor:
    def __init__(self, en_pin, in1_pin, in2_pin, reversed=False):
        self.en_pin = en_pin
        self.in1_pin = in1_pin
        self.in2_pin = in2_pin
        self.reversed = reversed

        # Initialisiere die GPIO-Pins
        GPIO.setup(self.en_pin, GPIO.OUT)
        GPIO.setup(self.in1_pin, GPIO.OUT)
        GPIO.setup(self.in2_pin, GPIO.OUT)

        # Erstelle und starte das PWM-Signal
        self.pwm = GPIO.PWM(self.en_pin, 1000)
        self.pwm.start(0)

    def set_direction(self, direction):
        """
        Setzt die Logikrichtung des Motors. Falls der Motor inverted montiert ist,
        wird die Richtung automatisch umgekehrt.
        """
        # Logische Richtung invertieren, falls notwendig
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
        else:  # 'stop'
            GPIO.output(self.in1_pin, GPIO.LOW)
            GPIO.output(self.in2_pin, GPIO.LOW)
        print(f"Motor an Pin {self.en_pin} Richtung gesetzt: {direction}")

    def set_speed(self, speed):
        speed = max(0, min(speed, MAX_DUTY_CYCLE))
        self.pwm.ChangeDutyCycle(speed)
        print(f"Motor an Pin {self.en_pin} Geschwindigkeit gesetzt: {speed}%")

    def accelerate(self, start_speed, end_speed, step_delay=0.02):
        start_speed = max(0, min(start_speed, MAX_DUTY_CYCLE))
        end_speed = max(0, min(end_speed, MAX_DUTY_CYCLE))
        if start_speed < end_speed:
            for s in range(int(start_speed), int(end_speed) + 1):
                self.set_speed(s)
                time.sleep(step_delay)
        else:
            for s in range(int(start_speed), int(end_speed) - 1, -1):
                self.set_speed(s)
                time.sleep(step_delay)
        print(f"Motor an Pin {self.en_pin} erreicht {end_speed}%")

class MecanumRobot:
    def __init__(self):
        # Annahme: Motor 2 ist invertiert, da er physisch umgekehrt montiert/verkabelt wurde.
        self.motors = {
            1: Motor(**MOTOR_PINS[1]),
            2: Motor(**MOTOR_PINS[2], reversed=True),
            3: Motor(**MOTOR_PINS[3]),
            4: Motor(**MOTOR_PINS[4])
        }

    def motor_control(self, motor_id, direction, start_speed, end_speed, step_delay=0.099, run_time=1):
        motor = self.motors[motor_id]
        motor.set_direction(direction)
        motor.accelerate(start_speed, end_speed, step_delay)
        time.sleep(run_time)
        motor.accelerate(end_speed, start_speed, step_delay)
        motor.set_direction('stop')
        motor.set_speed(0)
        print(f"Motor {motor_id} gestoppt.")

    def run_motors(self, motor_instructions, start_speed=10, end_speed=MAX_DUTY_CYCLE):
        threads = []
        for motor_id, direction in motor_instructions:
            t = threading.Thread(
                target=self.motor_control, 
                args=(motor_id, direction, start_speed, end_speed)
            )
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    # Bewegungskommandos – die Anweisungen (logisch) orientieren sich an einem symmetrischen Modell.
    # Dabei wird der invertierte Motor (Motor 2) in der set_direction-Methode automatisch korrigiert.
    def forward(self):
        # Gewünschte effektive Bewegung: Vorwärts für alle Räder
        instructions = [
            (1, 'forward'),
            (2, 'forward'),  # Motor 2 wird intern zu 'backward'
            (3, 'forward'),
            (4, 'forward')
        ]
        self.run_motors(instructions)

    def backward(self):
        instructions = [
            (1, 'backward'),
            (2, 'backward'),  # Intern wird zu 'forward'
            (3, 'backward'),
            (4, 'backward')
        ]
        self.run_motors(instructions)

    def strafe_right(self):
        # Gewünschte effektive Befehle (entspricht original):
        # Motor 1: backward, Motor 2: forward, Motor 3: forward, Motor 4: backward
        instructions = [
            (1, 'backward'),
            (2, 'backward'),  # Da reversed, wird zu 'forward'
            (3, 'forward'),
            (4, 'backward')
        ]
        self.run_motors(instructions)

    def strafe_left(self):
        # Gewünschte effektive Befehle:
        # Motor 1: forward, Motor 2: forward, Motor 3: forward, Motor 4: backward
        instructions = [
            (1, 'forward'),
            (2, 'forward'),   # Da reversed, wird zu 'backward'
            (3, 'forward'),
            (4, 'backward')
        ]
        self.run_motors(instructions)

    def turn_left(self):
        # Gewünschte effektive Befehle (Rotation):
        # Motor 1: backward, Motor 2: forward, Motor 3: forward, Motor 4: backward
        instructions = [
            (1, 'backward'),
            (2, 'forward'),   # Bei Motor 2 wird 'forward' zu 'backward'
            (3, 'forward'),
            (4, 'backward')
        ]
        self.run_motors(instructions)

    def turn_right(self):
        # Gewünschte effektive Befehle (Rotation):
        # Motor 1: forward, Motor 2: backward, Motor 3: backward, Motor 4: forward
        instructions = [
            (1, 'forward'),
            (2, 'backward'),  # Bei Motor 2 wird 'backward' zu 'forward'
            (3, 'backward'),
            (4, 'forward')
        ]
        self.run_motors(instructions)

    def forward_left(self):
        # Diagonale Bewegung: Nur Motor 1 und 4 aktivieren
        instructions = [
            (1, 'forward'),
            (4, 'forward')
        ]
        self.run_motors(instructions)

    def forward_right(self):
        # Diagonale Bewegung: Motor 2 und 3 aktivieren
        instructions = [
            (2, 'backward'),  # Bei Motor 2 wird 'backward' zu 'forward'
            (3, 'forward')
        ]
        self.run_motors(instructions)

    def backward_left(self):
        # Diagonale Bewegung: Motor 2 und 3 aktivieren
        instructions = [
            (2, 'forward'),   # Bei Motor 2 wird 'forward' zu 'backward'
            (3, 'backward')
        ]
        self.run_motors(instructions)

    def backward_right(self):
        # Diagonale Bewegung: Motor 1 und 4 aktivieren
        instructions = [
            (1, 'backward'),
            (4, 'backward')
        ]
        self.run_motors(instructions)

    def stop_all(self):
        # Stoppt alle Motoren, beendet PWM und räumt die GPIO-Pins auf.
        for motor in self.motors.values():
            motor.set_speed(0)
            motor.pwm.stop()
        GPIO.cleanup()
        print("Alle Motoren gestoppt und GPIO aufgeräumt.")

def command_loop():
    robot = MecanumRobot()
    cmd_map = {
        '8': robot.forward,
        '2': robot.backward,
        '4': robot.strafe_left,
        '6': robot.strafe_right,
        '7': robot.forward_left,
        '9': robot.forward_right,
        '1': robot.turn_left,
        '3': robot.turn_right,
        # Zusätzliche Tasten (optional) für diagonale Bewegungen:
        'bl': robot.backward_left,
        'br': robot.backward_right
    }
    try:
        while True:
            cmd = input("Richtung eingeben (8=vor, 2=zurück, 4=links, 6=rechts, 7=vor-links, 9=vor-rechts, 1=dreh-links, 3=dreh-rechts, q=quit): ").strip()
            if cmd.lower() == 'q':
                break
            elif cmd in cmd_map:
                cmd_map[cmd]()
            else:
                print("Ungültiger Befehl")
    finally:
        robot.stop_all()

if __name__ == "__main__":
    command_loop()

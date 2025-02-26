import RPi.GPIO as GPIO
import time
import threading
import keyboard  # For real-time key detection

# Explicitly set the mode before any other GPIO operations
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)  # Disable warnings

# GPIO pin definitions
# Motor 1
EN_A = 12  # PWM
IN1_A = 5
IN2_A = 6

# Motor 2
EN_B = 18  # PWM
IN1_B = 16
IN2_B = 20

# Motor 3
EN_C = 13  # PWM
IN1_C = 21
IN2_C = 26

# Motor 4
EN_D = 19  # PWM
IN1_D = 24
IN2_D = 23

MAX_DUTY_CYCLE = 100

# Setup pins
GPIO.setup(EN_A, GPIO.OUT)
GPIO.setup(IN1_A, GPIO.OUT)
GPIO.setup(IN2_A, GPIO.OUT)

GPIO.setup(EN_B, GPIO.OUT)
GPIO.setup(IN1_B, GPIO.OUT)
GPIO.setup(IN2_B, GPIO.OUT)

GPIO.setup(EN_C, GPIO.OUT)
GPIO.setup(IN1_C, GPIO.OUT)
GPIO.setup(IN2_C, GPIO.OUT)

GPIO.setup(EN_D, GPIO.OUT)
GPIO.setup(IN1_D, GPIO.OUT)
GPIO.setup(IN2_D, GPIO.OUT)

# Initialize PWM
pwm_A = GPIO.PWM(EN_A, 1000)
pwm_B = GPIO.PWM(EN_B, 1000)
pwm_C = GPIO.PWM(EN_C, 1000)
pwm_D = GPIO.PWM(EN_D, 1000)

pwm_A.start(0)
pwm_B.start(0)
pwm_C.start(0)
pwm_D.start(0)

def cleanup_motors():
    """Safely stop PWM and clean up GPIO resources."""
    pwm_A.stop()
    pwm_B.stop()
    pwm_C.stop()
    pwm_D.stop()
    GPIO.cleanup()

def set_motor_direction(motor, direction):
    """Set motor direction."""
    if motor == 1:
        in1, in2 = IN1_A, IN2_A
    elif motor == 2:
        in1, in2 = IN1_B, IN2_B
    elif motor == 3:
        in1, in2 = IN1_C, IN2_C
    elif motor == 4:
        in1, in2 = IN1_D, IN2_D
    else:
        return
    if direction == 'forward':
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
    elif direction == 'backward':
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)
    else:
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.LOW)

def set_motor_speed(motor, speed):
    """Set motor speed."""
    speed = min(max(speed, 0), MAX_DUTY_CYCLE)
    if motor == 1:
        pwm_A.ChangeDutyCycle(speed)
    elif motor == 2:
        pwm_B.ChangeDutyCycle(speed)
    elif motor == 3:
        pwm_C.ChangeDutyCycle(speed)
    elif motor == 4:
        pwm_D.ChangeDutyCycle(speed)

def drive_all_motors(direction, speed):
    """Drive all motors in the same direction with the same speed."""
    for motor in range(1, 5):
        set_motor_direction(motor, direction)
        set_motor_speed(motor, speed)

def stop_all_motors():
    """Stop all motors."""
    for motor in range(1, 5):
        set_motor_direction(motor, 'stop')
        set_motor_speed(motor, 0)

def main():
    try:
        print("Press '8' to drive forward. Release to stop.")
        while True:
            if keyboard.is_pressed('8'):
                drive_all_motors('forward', MAX_DUTY_CYCLE)
            else:
                stop_all_motors()
            time.sleep(0.1)  # Small delay to reduce CPU usage
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    finally:
        stop_all_motors()
        cleanup_motors()

if __name__ == "__main__":
    main()
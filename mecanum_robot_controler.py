import pygame
import sys
import RPi.GPIO as GPIO
import time
import threading

# GPIO and Motor Setup (keeping your original configuration)
# [Previous GPIO and motor setup code remains the same until the PWM initialization]

# Initialize Pygame and Joystick
pygame.init()
pygame.joystick.init()

# Set up the display
width, height = 1000, 900
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Mecanum Robot Controller")

# Try to connect to the Xbox controller
try:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Connected to {joystick.get_name()}")
except pygame.error:
    print("No Xbox controller connected.")
    GPIO.cleanup()
    sys.exit()

# Motor control functions for mecanum movement
def set_mecanum_movement(x_velocity, y_velocity, rotation):
    """
    Convert controller inputs to mecanum wheel velocities
    x_velocity: left/right movement (-1 to 1)
    y_velocity: forward/backward movement (-1 to 1)
    rotation: rotational movement (-1 to 1)
    """
    # Calculate wheel speeds for mecanum drive
    front_left = y_velocity + x_velocity + rotation
    front_right = y_velocity - x_velocity - rotation
    rear_left = y_velocity - x_velocity + rotation
    rear_right = y_velocity + x_velocity - rotation

    # Normalize speeds to -1 to 1 range
    max_value = max(abs(front_left), abs(front_right), 
                   abs(rear_left), abs(rear_right), 1)
    
    front_left = front_left / max_value
    front_right = front_right / max_value
    rear_left = rear_left / max_value
    rear_right = rear_right / max_value

    # Convert to duty cycle (0-100)
    motor_speeds = {
        1: abs(front_left) * MAX_DUTY_CYCLE,
        2: abs(front_right) * MAX_DUTY_CYCLE,
        3: abs(rear_left) * MAX_DUTY_CYCLE,
        4: abs(rear_right) * MAX_DUTY_CYCLE
    }

    # Set directions
    motor_directions = {
        1: 'forward' if front_left >= 0 else 'backward',
        2: 'forward' if front_right >= 0 else 'backward',
        3: 'forward' if rear_left >= 0 else 'backward',
        4: 'forward' if rear_right >= 0 else 'backward'
    }

    # Apply to motors
    for motor in range(1, 5):
        set_motor_direction(motor, motor_directions[motor])
        set_motor_speed(motor, motor_speeds[motor])

# Main control loop
running = True
try:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Get joystick values
        x_axis = joystick.get_axis(0)  # Left stick X-axis (strafe left/right)
        y_axis = -joystick.get_axis(1)  # Left stick Y-axis (forward/backward)
        rotation = joystick.get_axis(2)  # Right stick X-axis (rotation)

        # Apply deadzone to prevent drift
        deadzone = 0.1
        x_axis = 0 if abs(x_axis) < deadzone else x_axis
        y_axis = 0 if abs(y_axis) < deadzone else y_axis
        rotation = 0 if abs(rotation) < deadzone else rotation

        # Update motor controls
        set_mecanum_movement(x_axis, y_axis, rotation)

        # [Your original visualization code goes here]
        # Update the display
        pygame.display.flip()
        pygame.time.Clock().tick(60)

except KeyboardInterrupt:
    print("\nProgram terminated by user")
finally:
    # Cleanup
    pygame.quit()
    pwm_A.stop()
    pwm_B.stop()
    pwm_C.stop()
    pwm_D.stop()
    GPIO.cleanup()
    sys.exit()

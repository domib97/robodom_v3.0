import pygame
import time

# Initialize Pygame
pygame.init()

# Initialize the joystick
pygame.joystick.init()

# Try to connect to the Xbox controller
try:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Connected to {joystick.get_name()}")
except pygame.error:
    print("No Xbox controller connected.")
    exit()

# Main loop to test the Xbox controller inputs
try:
    while True:
        # Process Pygame events
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                print(f"Axis {event.axis} value: {event.value}")
            elif event.type == pygame.JOYBUTTONDOWN:
                print(f"Button {event.button} pressed.")
            elif event.type == pygame.JOYBUTTONUP:
                print(f"Button {event.button} released.")
            elif event.type == pygame.JOYHATMOTION:
                print(f"Hat {event.hat} value: {event.value}")

        # Add a small delay to make the output more readable
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    # Quit Pygame
    pygame.quit()

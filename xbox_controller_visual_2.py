import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 1000, 600  # Increased width to accommodate buttons
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Xbox Controller Visualization")

# Initialize the joystick
pygame.joystick.init()

# Try to connect to the Xbox controller
try:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Connected to {joystick.get_name()}")
except pygame.error:
    print("No Xbox controller connected.")
    sys.exit()

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

# Main loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    window.fill(white)

    # Get axis values
    axis_0 = joystick.get_axis(0)
    axis_1 = joystick.get_axis(1)
    axis_2 = joystick.get_axis(2)
    axis_3 = joystick.get_axis(3)

    # Draw axis 0 and 1 (left stick)
    pygame.draw.circle(window, red, (int(width / 4 + axis_0 * 100), int(height / 2 + axis_1 * 100)), 10)
    pygame.draw.line(window, black, (width / 4, height / 2 - 100), (width / 4, height / 2 + 100), 1)
    pygame.draw.line(window, black, (width / 4 - 100, height / 2), (width / 4 + 100, height / 2), 1)

    # Draw axis 2 and 3 (right stick)
    pygame.draw.circle(window, blue, (int(2 * width / 4 + axis_2 * 100), int(height / 2 + axis_3 * 100)), 10)
    pygame.draw.line(window, black, (2 * width / 4, height / 2 - 100), (2 * width / 4, height / 2 + 100), 1)
    pygame.draw.line(window, black, (2 * width / 4 - 100, height / 2), (2 * width / 4 + 100, height / 2), 1)

    # Get button values
    button_a = joystick.get_button(0)
    button_b = joystick.get_button(1)
    button_x = joystick.get_button(2)
    button_y = joystick.get_button(3)

    # Draw buttons A, B, X, Y
    button_radius = 20
    button_positions = {
        "A": (4 * width / 5, 2 * height / 3),
        "B": (4 * width / 5 + 50, height / 2),
        "X": (4 * width / 5 - 50, height / 2),
        "Y": (4 * width / 5, height / 3),
    }
    button_colors = {
        "A": green if button_a else black,
        "B": red if button_b else black,
        "X": blue if button_x else black,
        "Y": yellow if button_y else black,
    }

    for button, position in button_positions.items():
        pygame.draw.circle(window, button_colors[button], position, button_radius)
        pygame.draw.circle(window, black, position, button_radius, 2)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)

# Quit Pygame
pygame.quit()
sys.exit()

import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 1000, 600
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
yellow = (255, 255, 0)
gray = (128, 128, 128)  # For bumper buttons

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
    button_a = joystick.get_button(0)  # A Button (bottom)
    button_b = joystick.get_button(1)  # B Button (right)
    button_x = joystick.get_button(3)  # X Button (left)
    button_y = joystick.get_button(4)  # Y Button (top)
    button_lb = joystick.get_button(5)  # Left Bumper
    button_rb = joystick.get_button(6)  # Right Bumper

    # Button center positions
    button_center_x = 4 * width / 5
    button_center_y = height / 2
    button_offset = 50

    # Draw buttons A, B, X, Y in correct positions
    button_radius = 20
    button_positions = {
        "A": (button_center_x, button_center_y + button_offset),  # Bottom
        "B": (button_center_x + button_offset, button_center_y),  # Right
        "X": (button_center_x - button_offset, button_center_y),  # Left
        "Y": (button_center_x, button_center_y - button_offset),  # Top
    }

    # Draw face buttons (A, B, X, Y)
    # A Button (green, bottom)
    pygame.draw.circle(window, green if button_a else black, button_positions["A"], button_radius)
    pygame.draw.circle(window, black, button_positions["A"], button_radius, 2)
    
    # B Button (red, right)
    pygame.draw.circle(window, red if button_b else black, button_positions["B"], button_radius)
    pygame.draw.circle(window, black, button_positions["B"], button_radius, 2)
    
    # X Button (blue, left)
    pygame.draw.circle(window, blue if button_x else black, button_positions["X"], button_radius)
    pygame.draw.circle(window, black, button_positions["X"], button_radius, 2)
    
    # Y Button (yellow, top)
    pygame.draw.circle(window, yellow if button_y else black, button_positions["Y"], button_radius)
    pygame.draw.circle(window, black, button_positions["Y"], button_radius, 2)

    # Draw bumper buttons (LB, RB)
    bumper_width = 80
    bumper_height = 30
    # Left Bumper (LB)
    lb_pos = (width / 4, height / 4)
    pygame.draw.rect(window, 
                    gray if button_lb else black,
                    (lb_pos[0] - bumper_width/2, lb_pos[1] - bumper_height/2,
                     bumper_width, bumper_height))
    pygame.draw.rect(window, black,
                    (lb_pos[0] - bumper_width/2, lb_pos[1] - bumper_height/2,
                     bumper_width, bumper_height), 2)
    
    # Right Bumper (RB)
    rb_pos = (3 * width / 4, height / 4)
    pygame.draw.rect(window,
                    gray if button_rb else black,
                    (rb_pos[0] - bumper_width/2, rb_pos[1] - bumper_height/2,
                     bumper_width, bumper_height))
    pygame.draw.rect(window, black,
                    (rb_pos[0] - bumper_width/2, rb_pos[1] - bumper_height/2,
                     bumper_width, bumper_height), 2)

    # Add button labels
    font = pygame.font.Font(None, 36)
    # Labels for A, B, X, Y
    for button, pos in button_positions.items():
        text = font.render(button, True, black)
        text_rect = text.get_rect(center=pos)
        window.blit(text, text_rect)
    
    # Labels for LB, RB
    lb_text = font.render("LB", True, black)
    rb_text = font.render("RB", True, black)
    window.blit(lb_text, (lb_pos[0] - lb_text.get_width()/2, lb_pos[1] - lb_text.get_height()/2))
    window.blit(rb_text, (rb_pos[0] - rb_text.get_width()/2, rb_pos[1] - rb_text.get_height()/2))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)

# Quit Pygame
pygame.quit()
sys.exit()

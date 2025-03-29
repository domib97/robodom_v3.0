import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 1000, 900  # Increased height to accommodate D-pad
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
blue = (0, 179, 255)
yellow = (255, 255, 0)
gray = (128, 128, 128)
neon_green = (57, 255, 20)

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
    
    trigger_lt = joystick.get_axis(5)  # Left Trigger (ranges from -1 to 1)
    trigger_rt = joystick.get_axis(4)  # Right Trigger (ranges from -1 to 1)
    
    # Draw trigger buttons (LT, RT)
    trigger_width = 80
    trigger_height = 60
    lt_pos = (width / 4, height / 6)  # Positioned above LB
    rt_pos = (3 * width / 4, height / 6)  # Positioned above RB
    
    # Left Trigger (LT)
    # Convert trigger value from [-1, 1] to [0, 1] range
    lt_value = (trigger_lt + 1) / 2
    lt_fill_height = trigger_height * lt_value
    
    # Draw LT background
    pygame.draw.rect(window, 
                    black,
                    (lt_pos[0] - trigger_width/2, lt_pos[1] - trigger_height/2,
                     trigger_width, trigger_height))
    # Draw LT fill based on trigger value
    if lt_value > 0:
        pygame.draw.rect(window, 
                        neon_green,
                        (lt_pos[0] - trigger_width/2, 
                         lt_pos[1] + trigger_height/2 - lt_fill_height,
                         trigger_width, lt_fill_height))
    # Draw LT outline
    pygame.draw.rect(window, 
                    black,
                    (lt_pos[0] - trigger_width/2, lt_pos[1] - trigger_height/2,
                     trigger_width, trigger_height), 2)

    # Right Trigger (RT)
    # Convert trigger value from [-1, 1] to [0, 1] range
    rt_value = (trigger_rt + 1) / 2
    rt_fill_height = trigger_height * rt_value
    
    # Draw RT background
    pygame.draw.rect(window, 
                    black,
                    (rt_pos[0] - trigger_width/2, rt_pos[1] - trigger_height/2,
                     trigger_width, trigger_height))
    # Draw RT fill based on trigger value
    if rt_value > 0:
        pygame.draw.rect(window, 
                        neon_green,
                        (rt_pos[0] - trigger_width/2, 
                         rt_pos[1] + trigger_height/2 - rt_fill_height,
                         trigger_width, rt_fill_height))
    # Draw RT outline
    pygame.draw.rect(window, 
                    black,
                    (rt_pos[0] - trigger_width/2, rt_pos[1] - trigger_height/2,
                     trigger_width, trigger_height), 2)

    # Add trigger labels
    trigger_font = pygame.font.Font(None, 36)
    lt_text = trigger_font.render("LT", True, black)
    rt_text = trigger_font.render("RT", True, black)
    window.blit(lt_text, (lt_pos[0] - lt_text.get_width()/2, lt_pos[1] - trigger_height/2 - 30))
    window.blit(rt_text, (rt_pos[0] - rt_text.get_width()/2, rt_pos[1] - trigger_height/2 - 30))
    
    # Draw axis 0 and 1 (left stick)
    pygame.draw.circle(window, red, (int(width / 4 + axis_0 * 100), int(height / 2 + axis_1 * 100)), 10)
    pygame.draw.line(window, black, (width / 4, height / 2 - 100), (width / 4, height / 2 + 100), 1)
    pygame.draw.line(window, black, (width / 4 - 100, height / 2), (width / 4 + 100, height / 2), 1)

    # Draw axis 2 and 3 (right stick)
    pygame.draw.circle(window, blue, (int(2 * width / 4 + axis_2 * 100), int(height / 2 + axis_3 * 100)), 10)
    pygame.draw.line(window, black, (2 * width / 4, height / 2 - 100), (2 * width / 4, height / 2 + 100), 1)
    pygame.draw.line(window, black, (2 * width / 4 - 100, height / 2), (2 * width / 4 + 100, height / 2), 1)

    # Get button values
    button_a = joystick.get_button(0)     # A Button (bottom)
    button_b = joystick.get_button(1)     # B Button (right)
    button_x = joystick.get_button(3)     # X Button (left)
    button_y = joystick.get_button(4)     # Y Button (top)
    button_lb = joystick.get_button(6)    # Left Bumper
    button_rb = joystick.get_button(7)    # Right Bumper
    
    # D-pad values (using the hat/POV)
    dpad = joystick.get_hat(0)  # Returns (x, y) tuple: (-1/0/1, -1/0/1)
    dpad_x, dpad_y = dpad

    # Button center positions
    button_center_x = 4 * width / 5
    button_center_y = height / 2
    button_offset = 50

    # D-pad position (below the left analog stick)
    dpad_center_x = width / 4
    dpad_center_y = height * 3/4
    dpad_size = 40  # Size of each direction button
    dpad_spacing = 5  # Space between buttons

    # Draw D-pad
    # Center button (always gray)
    pygame.draw.rect(window, gray, 
                    (dpad_center_x - dpad_size/2, 
                     dpad_center_y - dpad_size/2,
                     dpad_size, dpad_size))

    # Up button
    pygame.draw.rect(window, 
                    neon_green if dpad_y == 1 else gray,
                    (dpad_center_x - dpad_size/2,
                     dpad_center_y - dpad_size*1.5 - dpad_spacing,
                     dpad_size,
                     dpad_size))

    # Down button
    pygame.draw.rect(window,
                    neon_green if dpad_y == -1 else gray,
                    (dpad_center_x - dpad_size/2,
                     dpad_center_y + dpad_size/2 + dpad_spacing,
                     dpad_size,
                     dpad_size))

    # Left button
    pygame.draw.rect(window,
                    neon_green if dpad_x == -1 else gray,
                    (dpad_center_x - dpad_size*1.5 - dpad_spacing,
                     dpad_center_y - dpad_size/2,
                     dpad_size,
                     dpad_size))

    # Right button
    pygame.draw.rect(window,
                    neon_green if dpad_x == 1 else gray,
                    (dpad_center_x + dpad_size/2 + dpad_spacing,
                     dpad_center_y - dpad_size/2,
                     dpad_size,
                     dpad_size))

    # Draw D-pad outlines
    pygame.draw.rect(window, black, 
                    (dpad_center_x - dpad_size/2, 
                     dpad_center_y - dpad_size/2,
                     dpad_size, dpad_size), 2)
    pygame.draw.rect(window, black,
                    (dpad_center_x - dpad_size/2,
                     dpad_center_y - dpad_size*1.5 - dpad_spacing,
                     dpad_size,
                     dpad_size), 2)
    pygame.draw.rect(window, black,
                    (dpad_center_x - dpad_size/2,
                     dpad_center_y + dpad_size/2 + dpad_spacing,
                     dpad_size,
                     dpad_size), 2)
    pygame.draw.rect(window, black,
                    (dpad_center_x - dpad_size*1.5 - dpad_spacing,
                     dpad_center_y - dpad_size/2,
                     dpad_size,
                     dpad_size), 2)
    pygame.draw.rect(window, black,
                    (dpad_center_x + dpad_size/2 + dpad_spacing,
                     dpad_center_y - dpad_size/2,
                     dpad_size,
                     dpad_size), 2)

    # Button positions for A, B, X, Y
    button_positions = {
        "A": (button_center_x, button_center_y + button_offset),
        "B": (button_center_x + button_offset, button_center_y),
        "X": (button_center_x - button_offset, button_center_y),
        "Y": (button_center_x, button_center_y - button_offset),
    }

    # Draw face buttons (A, B, X, Y)
    button_radius = 20
    pygame.draw.circle(window, green if button_a else gray, button_positions["A"], button_radius)
    pygame.draw.circle(window, red if button_b else gray, button_positions["B"], button_radius)
    pygame.draw.circle(window, blue if button_x else gray, button_positions["X"], button_radius)
    pygame.draw.circle(window, yellow if button_y else gray, button_positions["Y"], button_radius)
    
    # Draw button outlines
    for pos in button_positions.values():
        pygame.draw.circle(window, black, pos, button_radius, 2)

    # Draw bumper buttons (LB, RB)
    bumper_width = 80
    bumper_height = 30
    lb_pos = (width / 4, height / 4)
    rb_pos = (3 * width / 4, height / 4)

    # Left Bumper (LB)
    pygame.draw.rect(window, 
                    neon_green if button_lb else gray,
                    (lb_pos[0] - bumper_width/2, lb_pos[1] - bumper_height/2,
                     bumper_width, bumper_height))
    pygame.draw.rect(window, black,
                    (lb_pos[0] - bumper_width/2, lb_pos[1] - bumper_height/2,
                     bumper_width, bumper_height), 2)

    # Right Bumper (RB)
    pygame.draw.rect(window,
                    neon_green if button_rb else gray,
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

    # D-pad labels
    dpad_font = pygame.font.Font(None, 24)
    dpad_labels = {
        "U": (dpad_center_x, dpad_center_y - dpad_size - dpad_spacing),
        "D": (dpad_center_x, dpad_center_y + dpad_size + dpad_spacing),
        "L": (dpad_center_x - dpad_size - dpad_spacing, dpad_center_y),
        "R": (dpad_center_x + dpad_size + dpad_spacing, dpad_center_y)
    }
    
    for label, pos in dpad_labels.items():
        text = dpad_font.render(label, True, black)
        text_rect = text.get_rect(center=pos)
        window.blit(text, text_rect)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)

# Quit Pygame
pygame.quit()
sys.exit()

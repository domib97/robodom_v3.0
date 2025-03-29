# python
import RPi.GPIO as GPIO
import time
import threading

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
IN1_D = 23
IN2_D = 24

MAX_DUTY_CYCLE = 100

# Initialize GPIO
GPIO.setmode(GPIO.BCM)

# Setup pins for all motors
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

# Initialize PWM (fixed for motors 3 and 4)
pwm_A = GPIO.PWM(EN_A, 1000)
pwm_B = GPIO.PWM(EN_B, 1000)
pwm_C = GPIO.PWM(EN_C, 1000)
pwm_D = GPIO.PWM(EN_D, 1000)

pwm_A.start(0)
pwm_B.start(0)
pwm_C.start(0)
pwm_D.start(0)

def set_motor_direction(motor, direction):
    # Choose pins based on motor number
    if motor == 1:
        in1, in2 = IN1_A, IN2_A
    elif motor == 2:
        in1, in2 = IN1_B, IN2_B
    elif motor == 3:
        in1, in2 = IN1_C, IN2_C
    elif motor == 4:
        in1, in2 = IN1_D, IN2_D
    else:
        print("Invalid motor number")
        return
    # Set direction
    if direction == 'forward':
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
    elif direction == 'backward':
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)
    else:
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.LOW)
    print(f"Motor {motor} direction set to {direction}")

def set_motor_speed(motor, speed):
    speed = min(max(speed, 0), MAX_DUTY_CYCLE)
    if motor == 1:
        pwm_A.ChangeDutyCycle(speed)
    elif motor == 2:
        pwm_B.ChangeDutyCycle(speed)
    elif motor == 3:
        pwm_C.ChangeDutyCycle(speed)
    elif motor == 4:
        pwm_D.ChangeDutyCycle(speed)
    else:
        print("Invalid motor number")
        return
    print(f"Motor {motor} speed set to {speed}% duty cycle")

def accelerate_motor(motor, start_speed, end_speed, step_delay=0.02):
    start_speed = max(min(start_speed, MAX_DUTY_CYCLE), 0)
    end_speed = max(min(end_speed, MAX_DUTY_CYCLE), 0)
    if start_speed < end_speed:
        for speed in range(int(start_speed), int(end_speed) + 1):
            set_motor_speed(motor, speed)
            time.sleep(step_delay)
    else:
        for speed in range(int(start_speed), int(end_speed) - 1, -1):
            set_motor_speed(motor, speed)
            time.sleep(step_delay)
    print(f"Motor {motor} reached speed {end_speed}%")

def motor_control_thread(motor, direction, start_speed, end_speed, step_delay=0.099, run_time=1):
    set_motor_direction(motor, direction)
    accelerate_motor(motor, start_speed, end_speed, step_delay)
    time.sleep(run_time)
    accelerate_motor(motor, end_speed, start_speed, step_delay)
    set_motor_direction(motor, 'stop')
    set_motor_speed(motor, 0)
    print(f"Motor {motor} stopped")

def forward():
    threads = []
    for m in range(1, 5):
        t = threading.Thread(target=motor_control_thread, args=(m, 'forward', 10, MAX_DUTY_CYCLE))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

def backward():
    threads = []
    for m in range(1, 5):
        t = threading.Thread(target=motor_control_thread, args=(m, 'backward', 10, MAX_DUTY_CYCLE))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

def right():
    threads = []
    # For a right strafe, set motors differently
    t1 = threading.Thread(target=motor_control_thread, args=(1, 'backward', 10, MAX_DUTY_CYCLE))
    t2 = threading.Thread(target=motor_control_thread, args=(2, 'forward', 10, MAX_DUTY_CYCLE))
    t3 = threading.Thread(target=motor_control_thread, args=(3, 'forward', 10, MAX_DUTY_CYCLE))
    t4 = threading.Thread(target=motor_control_thread, args=(4, 'backward', 10, MAX_DUTY_CYCLE))
    threads.extend([t1, t2, t3, t4])
    for t in threads:
        t.start()
    for t in threads:
        t.join()

def left():
    threads = []
    t1 = threading.Thread(target=motor_control_thread, args=(1, 'forward', 10, MAX_DUTY_CYCLE))
    t2 = threading.Thread(target=motor_control_thread, args=(2, 'backward', 10, MAX_DUTY_CYCLE))
    t3 = threading.Thread(target=motor_control_thread, args=(3, 'backward', 10, MAX_DUTY_CYCLE))
    t4 = threading.Thread(target=motor_control_thread, args=(4, 'forward', 10, MAX_DUTY_CYCLE))
    threads.extend([t1, t2, t3, t4])
    for t in threads:
        t.start()
    for t in threads:
        t.join()

def forward_right():
    threads = []
    # Only control motors 2 and 3 for strafe forward right
    t2 = threading.Thread(target=motor_control_thread, args=(2, 'forward', 10, MAX_DUTY_CYCLE))
    t3 = threading.Thread(target=motor_control_thread, args=(3, 'forward', 10, MAX_DUTY_CYCLE))
    threads.extend([t2, t3])
    for t in threads:
        t.start()
    for t in threads:
        t.join()

def forward_left():
    threads = []
    t1 = threading.Thread(target=motor_control_thread, args=(1, 'forward', 10, MAX_DUTY_CYCLE))
    t4 = threading.Thread(target=motor_control_thread, args=(4, 'forward', 10, MAX_DUTY_CYCLE))
    threads.extend([t1, t4])
    for t in threads:
        t.start()
    for t in threads:
        t.join()

def backward_right():
    threads = []
    t1 = threading.Thread(target=motor_control_thread, args=(1, 'backward', 10, MAX_DUTY_CYCLE))
    t4 = threading.Thread(target=motor_control_thread, args=(4, 'backward', 10, MAX_DUTY_CYCLE))
    threads.extend([t1, t4])
    for t in threads:
        t.start()
    for t in threads:
        t.join()

def backward_left():
    threads = []
    t2 = threading.Thread(target=motor_control_thread, args=(2, 'backward', 10, MAX_DUTY_CYCLE))
    t3 = threading.Thread(target=motor_control_thread, args=(3, 'backward', 10, MAX_DUTY_CYCLE))
    threads.extend([t2, t3])
    for t in threads:
        t.start()
    for t in threads:
        t.join()

def stop_all():
    # Stop all motors, stop PWM and cleanup GPIO
    for pwm in [pwm_A, pwm_B, pwm_C, pwm_D]:
        pwm.ChangeDutyCycle(0)
        pwm.stop()
    GPIO.cleanup()
    print("All motors stopped and GPIO cleaned up.")

def command_loop():
    # Map keys to movement functions
    cmd_map = {
        '8': forward,
        '2': backward,
        '4': left,
        '6': right,
        '7': forward_left,
        '9': forward_right,
        '1': backward_left,
        '3': backward_right
    }
    try:
        while True:
            cmd = input("Enter direction (8=forward,2=backward,4=left,6=right,7=fw-left,9=fw-right,1=bw-left,3=bw-right, q=quit): ").strip()
            if cmd.lower() == 'q':
                break
            elif cmd in cmd_map:
                cmd_map[cmd]()
            else:
                print("Invalid command")
    finally:
        stop_all()

if __name__ == "__main__":
    command_loop()

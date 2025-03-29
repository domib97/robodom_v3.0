import RPi.GPIO as GPIO
import time
import threading
import logging
from typing import Dict, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('motor_controller.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GPIOPins:
    """GPIO pin definitions for all motors"""
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

class MotorConfig:
    """Motor configuration constants"""
    MAX_DUTY_CYCLE = 100
    PWM_FREQUENCY = 1000
    DEFAULT_STEP_DELAY = 0.02
    DEFAULT_RUN_TIME = 1.0
    MIN_SPEED = 0
    STARTUP_SPEED = 10

class MotorController:
    """Main class for controlling the 4-motor system"""
    
    def __init__(self):
        """Initialize the motor controller with GPIO setup and PWM instances"""
        self._cleanup_done = False
        self._cleanup_lock = threading.Lock()
        self._motor_locks: Dict[int, threading.Lock] = {
            i: threading.Lock() for i in range(1, 5)
        }
        self.pwm_instances: Dict[str, Optional[GPIO.PWM]] = {
            'A': None, 'B': None, 'C': None, 'D': None
        }
        self._emergency_stop = False
        self._emergency_stop_lock = threading.Lock()
        self.setup_gpio()
        logger.info("Motor controller initialized")

    def setup_gpio(self):
        """Setup GPIO pins and initialize PWM"""
        try:
            GPIO.setmode(GPIO.BCM)
            
            # Setup Motor 1
            GPIO.setup(GPIOPins.EN_A, GPIO.OUT)
            GPIO.setup(GPIOPins.IN1_A, GPIO.OUT)
            GPIO.setup(GPIOPins.IN2_A, GPIO.OUT)
            
            # Setup Motor 2
            GPIO.setup(GPIOPins.EN_B, GPIO.OUT)
            GPIO.setup(GPIOPins.IN1_B, GPIO.OUT)
            GPIO.setup(GPIOPins.IN2_B, GPIO.OUT)
            
            # Setup Motor 3
            GPIO.setup(GPIOPins.EN_C, GPIO.OUT)
            GPIO.setup(GPIOPins.IN1_C, GPIO.OUT)
            GPIO.setup(GPIOPins.IN2_C, GPIO.OUT)
            
            # Setup Motor 4
            GPIO.setup(GPIOPins.EN_D, GPIO.OUT)
            GPIO.setup(GPIOPins.IN1_D, GPIO.OUT)
            GPIO.setup(GPIOPins.IN2_D, GPIO.OUT)
            
            # Initialize PWM
            self.pwm_instances['A'] = GPIO.PWM(GPIOPins.EN_A, MotorConfig.PWM_FREQUENCY)
            self.pwm_instances['B'] = GPIO.PWM(GPIOPins.EN_B, MotorConfig.PWM_FREQUENCY)
            self.pwm_instances['C'] = GPIO.PWM(GPIOPins.EN_C, MotorConfig.PWM_FREQUENCY)
            self.pwm_instances['D'] = GPIO.PWM(GPIOPins.EN_D, MotorConfig.PWM_FREQUENCY)
            
            # Start PWM with 0% duty cycle
            for pwm in self.pwm_instances.values():
                if pwm:
                    pwm.start(0)
            
            logger.info("GPIO setup completed successfully")
        except Exception as e:
            logger.error(f"Failed to setup GPIO: {str(e)}")
            self.cleanup()
            raise

    def get_motor_pins(self, motor: int) -> tuple:
        """Get the GPIO pins for a specific motor"""
        pins = {
            1: (GPIOPins.IN1_A, GPIOPins.IN2_A),
            2: (GPIOPins.IN1_B, GPIOPins.IN2_B),
            3: (GPIOPins.IN1_C, GPIOPins.IN2_C),
            4: (GPIOPins.IN1_D, GPIOPins.IN2_D)
        }
        if motor not in pins:
            raise ValueError(f"Invalid motor number: {motor}")
        return pins[motor]

    def get_motor_pwm(self, motor: int) -> Optional[GPIO.PWM]:
        """Get the PWM instance for a specific motor"""
        pwm_map = {1: 'A', 2: 'B', 3: 'C', 4: 'D'}
        return self.pwm_instances.get(pwm_map.get(motor))

    def set_motor_direction(self, motor: int, direction: str):
        """Set the direction of a specific motor"""
        with self._motor_locks[motor]:
            try:
                in1, in2 = self.get_motor_pins(motor)
                if direction == 'forward':
                    GPIO.output(in1, GPIO.HIGH)
                    GPIO.output(in2, GPIO.LOW)
                elif direction == 'backward':
                    GPIO.output(in1, GPIO.LOW)
                    GPIO.output(in2, GPIO.HIGH)
                else:  # stop
                    GPIO.output(in1, GPIO.LOW)
                    GPIO.output(in2, GPIO.LOW)
                logger.info(f"Motor {motor} direction set to {direction}")
            except Exception as e:
                logger.error(f"Error setting motor {motor} direction: {str(e)}")
                raise

    def set_motor_speed(self, motor: int, speed: float):
        """Set the speed of a specific motor"""
        with self._motor_locks[motor]:
            try:
                speed = float(speed)
                speed = min(max(speed, MotorConfig.MIN_SPEED), MotorConfig.MAX_DUTY_CYCLE)
                pwm = self.get_motor_pwm(motor)
                if pwm:
                    pwm.ChangeDutyCycle(speed)
                    logger.info(f"Motor {motor} speed set to {speed}% duty cycle")
                else:
                    raise ValueError(f"PWM not initialized for motor {motor}")
            except Exception as e:
                logger.error(f"Error setting motor {motor} speed: {str(e)}")
                raise

    def accelerate_motor(self, motor: int, start_speed: float, end_speed: float, 
                        step_delay: float = MotorConfig.DEFAULT_STEP_DELAY):
        """Accelerate or decelerate a motor between two speeds"""
        with self._motor_locks[motor]:
            try:
                start_speed = max(min(start_speed, MotorConfig.MAX_DUTY_CYCLE), MotorConfig.MIN_SPEED)
                end_speed = max(min(end_speed, MotorConfig.MAX_DUTY_CYCLE), MotorConfig.MIN_SPEED)
                
                if start_speed < end_speed:
                    for speed in range(int(start_speed), int(end_speed) + 1):
                        if self._emergency_stop:
                            break
                        self.set_motor_speed(motor, speed)
                        time.sleep(step_delay)
                else:
                    for speed in range(int(start_speed), int(end_speed) - 1, -1):
                        if self._emergency_stop:
                            break
                        self.set_motor_speed(motor, speed)
                        time.sleep(step_delay)
                
                logger.info(f"Motor {motor} acceleration completed: {start_speed} -> {end_speed}")
            except Exception as e:
                logger.error(f"Error during motor {motor} acceleration: {str(e)}")
                raise

    def emergency_stop(self):
        """Immediately stop all motors"""
        with self._emergency_stop_lock:
            self._emergency_stop = True
        
        for motor in range(1, 5):
            with self._motor_locks[motor]:
                self.set_motor_direction(motor, 'stop')
                self.set_motor_speed(motor, 0)
        
        logger.warning("Emergency stop activated")

    def reset_emergency_stop(self):
        """Reset the emergency stop flag"""
        with self._emergency_stop_lock:
            self._emergency_stop = False
        logger.info("Emergency stop reset")

    def cleanup(self):
        """Clean up GPIO resources"""
        with self._cleanup_lock:
            if not self._cleanup_done:
                try:
                    for pwm in self.pwm_instances.values():
                        if pwm:
                            pwm.stop()
                    GPIO.cleanup()
                    self._cleanup_done = True
                    logger.info("GPIO cleanup completed")
                except Exception as e:
                    logger.error(f"Error during GPIO cleanup: {str(e)}")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()

class MotorMovement:
    """Class handling coordinated movement of multiple motors"""
    
    def __init__(self, controller: MotorController):
        self.controller = controller

    def _run_motor_sequence(self, motor_commands: list):
        """Execute a sequence of motor commands in parallel"""
        threads = []
        for motor, direction in motor_commands:
            thread = threading.Thread(
                target=self._motor_control_thread,
                args=(motor, direction)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def _motor_control_thread(self, motor: int, direction: str,
                            start_speed: float = MotorConfig.STARTUP_SPEED,
                            end_speed: float = MotorConfig.MAX_DUTY_CYCLE,
                            step_delay: float = MotorConfig.DEFAULT_STEP_DELAY,
                            run_time: float = MotorConfig.DEFAULT_RUN_TIME):
        """Control thread for a single motor"""
        try:
            self.controller.set_motor_direction(motor, direction)
            self.controller.accelerate_motor(motor, start_speed, end_speed, step_delay)
            time.sleep(run_time)
            self.controller.accelerate_motor(motor, end_speed, start_speed, step_delay)
            self.controller.set_motor_direction(motor, 'stop')
            self.controller.set_motor_speed(motor, 0)
        except Exception as e:
            logger.error(f"Error in motor {motor} control thread: {str(e)}")
            self.controller.emergency_stop()

    def forward(self):
        """Move all motors forward"""
        motor_commands = [(i, 'forward') for i in range(1, 5)]
        self._run_motor_sequence(motor_commands)

    def backward(self):
        """Move all motors backward"""
        motor_commands = [(i, 'backward') for i in range(1, 5)]
        self._run_motor_sequence(motor_commands)

    def right(self):
        """Turn right (tank turn)"""
        motor_commands = [
            (1, 'backward'), (2, 'forward'),
            (3, 'forward'), (4, 'backward')
        ]
        self._run_motor_sequence(motor_commands)

    def left(self):
        """Turn left (tank turn)"""
        motor_commands = [
            (1, 'forward'), (2, 'backward'),
            (3, 'backward'), (4, 'forward')
        ]
        self._run_motor_sequence(motor_commands)

    def turning_right(self):
        """Turn right in place"""
        motor_commands = [
            (1, 'forward'), (2, 'forward'),
            (3, 'backward'), (4, 'backward')
        ]
        self._run_motor_sequence(motor_commands)

    def turning_left(self):
        """Turn left in place"""
        motor_commands = [
            (1, 'backward'), (2, 'backward'),
            (3, 'forward'), (4, 'forward')
        ]
        self._run_motor_sequence(motor_commands)

    def forward_right(self):
        """Move forward and right"""
        motor_commands = [(2, 'forward'), (3, 'forward')]
        self._run_motor_sequence(motor_commands)

    def forward_left(self):
        """Move forward and left"""
        motor_commands = [(1, 'forward'), (4, 'forward')]
        self._run_motor_sequence(motor_commands)

    def backward_right(self):
        """Move backward and right"""
        motor_commands = [(1, 'backward'), (4, 'backward')]
        self._run_motor_sequence(motor_commands)

    def backward_left(self):
        """Move backward and left"""
        motor_commands = [(2, 'backward'), (3, 'backward')]
        self._run_motor_sequence(motor_commands)

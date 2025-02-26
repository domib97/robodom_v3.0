import smbus
import time
import math
import os

class MPU9250:
    # MPU9250 I2C address
    MPU9250_ADDRESS = 0x68
    AK8963_ADDRESS = 0x0C

    # MPU9250 registers
    WHO_AM_I_MPU9250 = 0x75
    USER_CTRL = 0x6A
    PWR_MGMT_1 = 0x6B
    PWR_MGMT_2 = 0x6C
    INT_PIN_CFG = 0x37
    INT_ENABLE = 0x38

    # AK8963 registers
    WHO_AM_I_AK8963 = 0x00
    AK8963_ST1 = 0x02
    AK8963_XOUT_L = 0x03
    AK8963_CNTL1 = 0x0A
    AK8963_CNTL2 = 0x0B
    AK8963_ASAX = 0x10

    # Aachen-specific calibration
    AACHEN_DECLINATION = 2.0  # degrees East
    AACHEN_FIELD_STRENGTH = 48000  # nT
    AACHEN_INCLINATION = 66.0  # degrees

    def __init__(self, bus_num=1):
        self.bus = smbus.SMBus(bus_num)
        self.mag_calibration = [0, 0, 0]

        # Initialize calibration values
        self.mag_x_min = float('inf')
        self.mag_x_max = float('-inf')
        self.mag_y_min = float('inf')
        self.mag_y_max = float('-inf')
        self.mag_z_min = float('inf')
        self.mag_z_max = float('-inf')

        # Aachen-specific calibration flags
        self.is_calibrated = False
        self.samples_collected = 0
        self.REQUIRED_SAMPLES = 100  # Number of samples needed for calibration

    def initialize(self):
        who_am_i = self.read_byte(self.MPU9250_ADDRESS, self.WHO_AM_I_MPU9250)
        print(f"MPU9250 WHO_AM_I = 0x{who_am_i:02X}")
        if who_am_i not in [0x71, 0x73]:
            raise RuntimeError("Error: MPU9250 not detected!")

        self.init_mpu9250()
        time.sleep(0.1)

        mag_who_am_i = 0
        for i in range(5):
            mag_who_am_i = self.read_byte(self.AK8963_ADDRESS, self.WHO_AM_I_AK8963)
            print(f"Attempt {i + 1} - AK8963 WHO_AM_I = 0x{mag_who_am_i:02X}")
            if mag_who_am_i == 0x48:
                break
            time.sleep(0.1)

        if mag_who_am_i != 0x48:
            raise RuntimeError("Error: AK8963 not detected!")

        self.init_ak8963()
        print(f"\nAachen Magnetic Parameters:")
        print(f"Declination: {self.AACHEN_DECLINATION}° East")
        print(f"Field Strength: {self.AACHEN_FIELD_STRENGTH} nT")
        print(f"Inclination: {self.AACHEN_INCLINATION}°")

    def init_mpu9250(self):
        # Reset MPU9250
        self.write_byte(self.MPU9250_ADDRESS, self.PWR_MGMT_1, 0x80)
        time.sleep(0.1)

        self.write_byte(self.MPU9250_ADDRESS, self.PWR_MGMT_1, 0x00)
        time.sleep(0.1)

        self.write_byte(self.MPU9250_ADDRESS, self.USER_CTRL, 0x00)
        self.write_byte(self.MPU9250_ADDRESS, self.INT_PIN_CFG, 0x22)
        self.write_byte(self.MPU9250_ADDRESS, self.INT_ENABLE, 0x00)
        self.write_byte(self.MPU9250_ADDRESS, self.PWR_MGMT_2, 0x00)

        time.sleep(0.1)
        print("MPU9250 initialized")

    def init_ak8963(self):
        self.write_byte(self.AK8963_ADDRESS, self.AK8963_CNTL2, 0x01)
        time.sleep(0.1)

        self.write_byte(self.AK8963_ADDRESS, self.AK8963_CNTL1, 0x0F)
        time.sleep(0.1)

        raw_data = self.read_bytes(self.AK8963_ADDRESS, self.AK8963_ASAX, 3)

        for i in range(3):
            self.mag_calibration[i] = (float(raw_data[i] - 128) / 256.0 + 1.0)

        print("Magnetometer Sensitivity Adjustment Values:")
        print(f"X-axis: {self.mag_calibration[0]:.3f}")
        print(f"Y-axis: {self.mag_calibration[1]:.3f}")
        print(f"Z-axis: {self.mag_calibration[2]:.3f}")

        self.write_byte(self.AK8963_ADDRESS, self.AK8963_CNTL1, 0x00)
        time.sleep(0.1)

        # Set continuous measurement mode 2 (100 Hz) with 16-bit output
        self.write_byte(self.AK8963_ADDRESS, self.AK8963_CNTL1, 0x16)
        time.sleep(0.1)

        print("AK8963 initialized")

    def read_mag_data(self):
        if not (self.read_byte(self.AK8963_ADDRESS, self.AK8963_ST1) & 0x01):
            return None

        raw_data = self.read_bytes(self.AK8963_ADDRESS, self.AK8963_XOUT_L, 7)

        if raw_data[6] & 0x08:
            return None

        mag_count = [
            int.from_bytes(raw_data[0:2], byteorder='little', signed=True),
            int.from_bytes(raw_data[2:4], byteorder='little', signed=True),
            int.from_bytes(raw_data[4:6], byteorder='little', signed=True)
        ]

        mag_data = [
            mag_count[i] * 4912.0 / 32760.0 * self.mag_calibration[i]
            for i in range(3)
        ]

        # Update calibration data
        self.update_calibration(mag_data)

        return mag_data

    def update_calibration(self, mag_data):
        """Update calibration values and check field strength"""
        if not self.is_calibrated:
            self.mag_x_min = min(self.mag_x_min, mag_data[0])
            self.mag_x_max = max(self.mag_x_max, mag_data[0])
            self.mag_y_min = min(self.mag_y_min, mag_data[1])
            self.mag_y_max = max(self.mag_y_max, mag_data[1])
            self.mag_z_min = min(self.mag_z_min, mag_data[2])
            self.mag_z_max = max(self.mag_z_max, mag_data[2])

            self.samples_collected += 1
            if self.samples_collected >= self.REQUIRED_SAMPLES:
                self.is_calibrated = True

    def calculate_heading(self, mag_data):
        """Calculate heading with Aachen-specific corrections"""
        x = mag_data[0]
        y = mag_data[1]

        # Apply soft iron correction if calibrated
        if self.is_calibrated:
            x_centered = x - (self.mag_x_max + self.mag_x_min) / 2
            y_centered = y - (self.mag_y_max + self.mag_y_min) / 2

            # Scale correction
            x_scale = (self.mag_x_max - self.mag_x_min) / 2
            y_scale = (self.mag_y_max - self.mag_y_min) / 2
            avg_scale = (x_scale + y_scale) / 2

            if avg_scale != 0:
                x_centered = x_centered * (avg_scale / x_scale)
                y_centered = y_centered * (avg_scale / y_scale)
        else:
            x_centered = x
            y_centered = y

        # Calculate heading
        heading = math.atan2(y_centered, x_centered)

        # Convert to degrees
        heading_deg = math.degrees(heading)

        # Add Aachen's magnetic declination
        heading_deg += self.AACHEN_DECLINATION

        # Normalize to 0-360
        heading_deg = (heading_deg + 360) % 360

        return heading_deg

    def get_calibration_status(self):
        """Return calibration progress"""
        if self.is_calibrated:
            return "Calibrated"
        return f"Calibrating: {(self.samples_collected / self.REQUIRED_SAMPLES * 100):.1f}%"

    def write_byte(self, address, register, value):
        self.bus.write_byte_data(address, register, value)

    def read_byte(self, address, register):
        return self.bus.read_byte_data(address, register)

    def read_bytes(self, address, register, length):
        return self.bus.read_i2c_block_data(address, register, length)

def create_direction_indicator(heading):
    """Create a visual direction indicator with cardinal points"""
    segments = 36  # Every 10 degrees
    segment = int(heading / 10)
    indicator = ['.' for _ in range(segments)]
    indicator[segment] = '█'

    # Add cardinal points
    cardinal_points = {
        0: 'N',
        9: 'E',
        18: 'S',
        27: 'W'
    }

    for pos, point in cardinal_points.items():
        indicator[pos] = point

    return ''.join(indicator) + f" {heading:>6.1f}°"

def main():
    try:
        compass = MPU9250()
        compass.initialize()

        print("\nStarting compass readings (optimized for Aachen)...")
        print("Please rotate the sensor 360° slowly for calibration")

        while True:
            mag_data = compass.read_mag_data()

            if mag_data is None:
                continue

            heading = compass.calculate_heading(mag_data)

            # Clear screen
            os.system('clear' if os.name == 'posix' else 'cls')

            # Print calibration status
            print(f"Calibration Status: {compass.get_calibration_status()}")
            if compass.is_calibrated:
                print(f"\nCalibration Ranges:")
                print(f"X: {compass.mag_x_min:.1f} to {compass.mag_x_max:.1f} μT")
                print(f"Y: {compass.mag_y_min:.1f} to {compass.mag_y_max:.1f} μT")
                print(f"Z: {compass.mag_z_min:.1f} to {compass.mag_z_max:.1f} μT")

            # Print current values
            print(f"\nMagnetic Field (μT):")
            print(f"X: {mag_data[0]:>8.1f}")
            print(f"Y: {mag_data[1]:>8.1f}")
            print(f"Z: {mag_data[2]:>8.1f}")

            # Print heading with visual indicator
            print("\nCompass (Aachen-calibrated):")
            print(create_direction_indicator(heading))

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()

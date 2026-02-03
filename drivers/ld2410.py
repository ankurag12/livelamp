"""
LD2410 mmWave Radar Sensor Driver
Supports both GPIO presence detection and UART data/configuration
"""
from machine import Pin, UART
import time


class LD2410:
    # Frame headers and footers
    FRAME_HEADER = bytes([0xF4, 0xF3, 0xF2, 0xF1])
    FRAME_FOOTER = bytes([0xF8, 0xF7, 0xF6, 0xF5])

    # Command words
    CMD_ENABLE_CONFIG = bytes([0xFF, 0x00, 0x01, 0x00])
    CMD_END_CONFIG = bytes([0xFE, 0x00])
    CMD_READ_PARAM = bytes([0x61, 0x00])

    def __init__(self, tx_pin, rx_pin, presence_pin, uart_id=1, baudrate=256000):
        """
        Initialize LD2410 sensor

        Args:
            tx_pin: ESP32 TX pin (connects to LD2410 RX)
            rx_pin: ESP32 RX pin (connects to LD2410 TX)
            presence_pin: GPIO pin for presence detection
            uart_id: UART peripheral ID (default 1)
            baudrate: UART baud rate (default 256000)
        """
        self.uart = UART(uart_id, baudrate=baudrate, tx=tx_pin, rx=rx_pin)
        self.presence_pin = Pin(presence_pin, Pin.IN)

        self._last_data = {
            "presence": False,
            "target_state": 0,
            "moving_distance": 0,
            "moving_energy": 0,
            "static_distance": 0,
            "static_energy": 0,
            "detection_distance": 0
        }

    def read_presence_gpio(self):
        """
        Read simple presence detection from GPIO pin

        Returns:
            bool: True if presence detected, False otherwise
        """
        return bool(self.presence_pin.value())

    def _send_command(self, command):
        """
        Send command frame to LD2410

        Args:
            command: Command bytes to send
        """
        length = len(command)
        frame = self.FRAME_HEADER + length.to_bytes(2, 'little') + command + self.FRAME_FOOTER
        self.uart.write(frame)

    def _read_frame(self, timeout=1000):
        """
        Read a complete frame from UART

        Args:
            timeout: Read timeout in milliseconds

        Returns:
            bytes or None: Frame data if valid frame received
        """
        start_time = time.ticks_ms()
        buffer = bytearray()

        while time.ticks_diff(time.ticks_ms(), start_time) < timeout:
            if self.uart.any():
                byte = self.uart.read(1)
                if byte:
                    buffer.extend(byte)

                    # Check for complete frame
                    if len(buffer) >= 10:  # Minimum frame size
                        # Look for header
                        header_idx = buffer.find(self.FRAME_HEADER)
                        if header_idx >= 0:
                            # Check if we have length bytes
                            if len(buffer) >= header_idx + 6:
                                length = int.from_bytes(buffer[header_idx+4:header_idx+6], 'little')
                                expected_size = header_idx + 10 + length

                                if len(buffer) >= expected_size:
                                    # Check for footer
                                    if buffer[expected_size-4:expected_size] == self.FRAME_FOOTER:
                                        return bytes(buffer[header_idx:expected_size])
                                    else:
                                        # Invalid frame, remove header and continue
                                        buffer = buffer[header_idx+4:]

        return None

    def read_data(self):
        """
        Read radar data from UART

        Returns:
            dict: Parsed radar data
        """
        # Check for any available data
        if self.uart.any():
            frame = self._read_frame(timeout=100)

            if frame and len(frame) >= 23:
                # Parse basic target data report (0x02 report type)
                data_start = 6  # After header and length

                if frame[data_start] == 0x02 and frame[data_start + 1] == 0xAA:
                    # Valid target data frame
                    target_state = frame[data_start + 2]
                    moving_distance = int.from_bytes(frame[data_start + 3:data_start + 5], 'little')
                    moving_energy = frame[data_start + 5]
                    static_distance = int.from_bytes(frame[data_start + 6:data_start + 8], 'little')
                    static_energy = frame[data_start + 8]
                    detection_distance = int.from_bytes(frame[data_start + 9:data_start + 11], 'little')

                    self._last_data = {
                        "presence": target_state > 0,
                        "target_state": target_state,  # 0=no target, 1=moving, 2=static, 3=both
                        "moving_distance": moving_distance,
                        "moving_energy": moving_energy,
                        "static_distance": static_distance,
                        "static_energy": static_energy,
                        "detection_distance": detection_distance
                    }

        # Also update with GPIO presence
        self._last_data["presence_gpio"] = self.read_presence_gpio()

        return self._last_data

    def enable_config_mode(self):
        """Enter configuration mode"""
        self._send_command(self.CMD_ENABLE_CONFIG)
        time.sleep_ms(50)

    def end_config_mode(self):
        """Exit configuration mode"""
        self._send_command(self.CMD_END_CONFIG)
        time.sleep_ms(50)

    def get_state(self):
        """
        Get current sensor state for API responses

        Returns:
            dict: Current sensor data
        """
        return self._last_data.copy()

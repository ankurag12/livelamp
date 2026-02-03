"""
Neopixel LED Ring Driver
Supports RGB color control for Adafruit 12-LED Neopixel Ring
"""
from machine import Pin
import neopixel


class NeopixelRing:
    def __init__(self, pin, num_leds=12):
        """
        Initialize Neopixel LED ring

        Args:
            pin: GPIO pin number for Neopixel data
            num_leds: Number of LEDs in the ring (default 12)
        """
        self.pin = pin
        self.num_leds = num_leds
        self.np = neopixel.NeoPixel(Pin(pin), num_leds)
        self._color = (0, 0, 0)  # Start off (black)
        self.clear()

    def set_color(self, r, g, b):
        """
        Set all LEDs to the same RGB color

        Args:
            r: Red value 0-255
            g: Green value 0-255
            b: Blue value 0-255
        """
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        self._color = (r, g, b)

        for i in range(self.num_leds):
            self.np[i] = (r, g, b)
        self.np.write()

    def set_color_hex(self, hex_color):
        """
        Set all LEDs using hex color string

        Args:
            hex_color: Hex color string like "#FF5500" or "FF5500"
        """
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        self.set_color(r, g, b)

    def set_pixel(self, index, r, g, b):
        """
        Set individual LED color

        Args:
            index: LED index (0 to num_leds-1)
            r: Red value 0-255
            g: Green value 0-255
            b: Blue value 0-255
        """
        if 0 <= index < self.num_leds:
            self.np[index] = (r, g, b)
            self.np.write()

    def clear(self):
        """Turn off all LEDs"""
        self.set_color(0, 0, 0)

    def off(self):
        """Turn off all LEDs (alias for clear)"""
        self.clear()

    def get_color(self):
        """Get current RGB color as tuple"""
        return self._color

    def get_color_hex(self):
        """Get current color as hex string"""
        return "#{:02x}{:02x}{:02x}".format(self._color[0], self._color[1], self._color[2])

    def get_state(self):
        """Get current state as dict for API responses"""
        return {
            "r": self._color[0],
            "g": self._color[1],
            "b": self._color[2],
            "hex": self.get_color_hex()
        }

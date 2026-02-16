"""
Neopixel LED Ring Driver
Supports RGB and RGBW Neopixels with patterns
"""
from machine import Pin
import neopixel
import math
import random


class NeopixelRing:
    def __init__(self, pin, num_leds=12, rgbw=True):
        """
        Initialize Neopixel LED ring

        Args:
            pin: GPIO pin number for Neopixel data
            num_leds: Number of LEDs in the ring (default 12)
            rgbw: True for RGBW LEDs, False for RGB LEDs (default True)
        """
        self.pin = pin
        self.num_leds = num_leds
        self.rgbw = rgbw

        # RGBW needs 4 bytes per pixel, RGB needs 3
        bpp = 4 if rgbw else 3
        self.np = neopixel.NeoPixel(Pin(pin), num_leds, bpp=bpp)

        self._color = (0, 0, 0)  # RGB color
        self._white = 0  # White channel (0-255)
        self._pattern = 'solid'  # Current pattern

        # Pattern state variables
        self._breathe_phase = 0
        self._fade_current_color = (255, 0, 0)  # Start with red
        self._fade_target_color = (0, 255, 0)   # Fade to green
        self._fade_progress = 0
        self._rainbow_offset = 0
        self._dream_phase = 0
        self._dream_hue = 0
        self._fire_current = (255, 180, 50, 100)  # Current warm color (R, G, B, W)
        self._fire_target = (255, 200, 30, 120)   # Target warm color
        self._fire_progress = 0

        self.clear()

    def _update_leds(self):
        """Internal method to update all LEDs with current RGB and W values"""
        r, g, b = self._color
        for i in range(self.num_leds):
            if self.rgbw:
                self.np[i] = (r, g, b, self._white)
            else:
                self.np[i] = (r, g, b)
        self.np.write()

    def set_color(self, r, g, b):
        """
        Set all LEDs to the same RGB color (keeps W channel unchanged)

        Args:
            r: Red value 0-255
            g: Green value 0-255
            b: Blue value 0-255
        """
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        self._color = (r, g, b)
        if self._pattern == 'solid':
            self._update_leds()

    def set_color_hex(self, hex_color):
        """
        Set all LEDs using hex color string (keeps W channel unchanged)

        Args:
            hex_color: Hex color string like "#FF5500" or "FF5500"
        """
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        self.set_color(r, g, b)

    def set_pixel(self, index, r, g, b, w=None):
        """
        Set individual LED color

        Args:
            index: LED index (0 to num_leds-1)
            r: Red value 0-255
            g: Green value 0-255
            b: Blue value 0-255
            w: White value 0-255 (optional, uses current white if None)
        """
        if 0 <= index < self.num_leds:
            if self.rgbw:
                white = w if w is not None else self._white
                self.np[index] = (r, g, b, white)
            else:
                self.np[index] = (r, g, b)

    def write(self):
        """Write current LED states to hardware"""
        self.np.write()

    def set_white(self, brightness):
        """
        Set white channel brightness (keeps RGB unchanged)

        Args:
            brightness: White brightness 0-255
        """
        if not self.rgbw:
            # Fallback to RGB white for non-RGBW
            self.set_color(brightness, brightness, brightness)
            return

        brightness = max(0, min(255, brightness))
        self._white = brightness
        if self._pattern == 'solid':
            self._update_leds()

    def set_pattern(self, pattern):
        """
        Set LED pattern mode

        Args:
            pattern: Pattern name ('solid', 'chase', 'breathe', 'sparkle', 'rainbow')
        """
        self._pattern = pattern
        if pattern == 'solid':
            self._update_leds()

    def get_pattern(self):
        """Get current pattern name"""
        return self._pattern

    def clear(self):
        """Turn off all LEDs (RGB and W)"""
        self._color = (0, 0, 0)
        self._white = 0
        self._update_leds()

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
            "hex": self.get_color_hex(),
            "white": self._white,
            "pattern": self._pattern
        }

    def render_pattern(self):
        """
        Render one frame of the current pattern
        Call this periodically from main async loop
        """
        if self._pattern == 'solid':
            # Solid pattern - nothing to do, already set
            pass
        elif self._pattern == 'breathe':
            self._render_breathe()
        elif self._pattern == 'fade':
            self._render_fade()
        elif self._pattern == 'rainbow':
            self._render_rainbow()
        elif self._pattern == 'fire':
            self._render_fire()
        elif self._pattern == 'dream':
            self._render_dream()

    def _render_breathe(self):
        """Render breathe pattern - all LEDs pulse with sine wave (30% to 100% brightness)"""
        r, g, b = self._color
        white = self._white

        # Calculate brightness from sine wave (0.3 to 1.0 for 30% minimum)
        brightness = 0.3 + 0.7 * ((math.sin(self._breathe_phase) + 1) / 2)

        for i in range(self.num_leds):
            self.set_pixel(
                i,
                int(r * brightness),
                int(g * brightness),
                int(b * brightness),
                int(white * brightness)
            )

        self.write()
        self._breathe_phase += 0.1
        if self._breathe_phase >= 2 * math.pi:
            self._breathe_phase = 0

    def _render_fire(self):
        """Render fire mode - random warm color transitions (yellows, oranges, warm whites)"""
        # Interpolate between current and target warm color
        r1, g1, b1, w1 = self._fire_current
        r2, g2, b2, w2 = self._fire_target

        t = self._fire_progress / 150.0  # 0.0 to 1.0 (slower than fade)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        w = int(w1 + (w2 - w1) * t)

        # Set all LEDs to interpolated warm color
        for i in range(self.num_leds):
            self.set_pixel(i, r, g, b, w)

        self.write()

        # Increment progress
        self._fire_progress += 1
        if self._fire_progress >= 150:
            # Reached target, pick new target warm color
            self._fire_current = self._fire_target
            # Generate random warm color
            # Warm spectrum: high red, medium-high green, low blue, variable white
            self._fire_target = (
                random.randint(220, 255),      # Red: always high
                random.randint(100, 220),      # Green: medium to high (more = yellow, less = orange)
                random.randint(0, 60),         # Blue: very low (warm tones)
                random.randint(50, 180)        # White: variable (higher = whiter, lower = more colored)
            )
            self._fire_progress = 0

    def _render_dream(self):
        """Render dream mode - breathe effect combined with color cycling"""
        # Calculate breathe brightness (30% to 100%)
        brightness = 0.3 + 0.7 * ((math.sin(self._dream_phase) + 1) / 2)

        # Convert hue to RGB
        hue = self._dream_hue
        c = 1.0  # Chroma
        h = hue / 60.0
        x = c * (1 - abs((h % 2) - 1))

        if 0 <= h < 1:
            rgb = (c, x, 0)
        elif 1 <= h < 2:
            rgb = (x, c, 0)
        elif 2 <= h < 3:
            rgb = (0, c, x)
        elif 3 <= h < 4:
            rgb = (0, x, c)
        elif 4 <= h < 5:
            rgb = (x, 0, c)
        else:
            rgb = (c, 0, x)

        # Apply brightness to color
        r = int(rgb[0] * 255 * brightness)
        g = int(rgb[1] * 255 * brightness)
        b = int(rgb[2] * 255 * brightness)

        # Set all LEDs to same color
        for i in range(self.num_leds):
            self.set_pixel(i, r, g, b, 0)

        self.write()

        # Update phase and hue
        self._dream_phase += 0.08
        if self._dream_phase >= 2 * math.pi:
            self._dream_phase = 0

        self._dream_hue = (self._dream_hue + 0.5) % 360

    def _render_fade(self):
        """Render fade pattern - slow crossfade between random colors"""
        # Interpolate between current and target color
        r1, g1, b1 = self._fade_current_color
        r2, g2, b2 = self._fade_target_color

        t = self._fade_progress / 100.0  # 0.0 to 1.0
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)

        # Set all LEDs to interpolated color
        for i in range(self.num_leds):
            self.set_pixel(i, r, g, b, 0)

        self.write()

        # Increment progress
        self._fade_progress += 1
        if self._fade_progress >= 100:
            # Reached target, pick new target color
            self._fade_current_color = self._fade_target_color
            # Generate random target color
            self._fade_target_color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255)
            )
            self._fade_progress = 0

    def _render_rainbow(self):
        """Render rainbow pattern - rotating rainbow colors"""
        for i in range(self.num_leds):
            # Calculate hue for this LED
            hue = ((i * 360 / self.num_leds) + self._rainbow_offset) % 360

            # Convert HSV to RGB (simplified)
            # H: 0-360, S: 1.0, V: 1.0
            c = 1.0  # Chroma
            h = hue / 60.0
            x = c * (1 - abs((h % 2) - 1))

            if 0 <= h < 1:
                rgb = (c, x, 0)
            elif 1 <= h < 2:
                rgb = (x, c, 0)
            elif 2 <= h < 3:
                rgb = (0, c, x)
            elif 3 <= h < 4:
                rgb = (0, x, c)
            elif 4 <= h < 5:
                rgb = (x, 0, c)
            else:
                rgb = (c, 0, x)

            self.set_pixel(
                i,
                int(rgb[0] * 255),
                int(rgb[1] * 255),
                int(rgb[2] * 255),
                0  # No white for rainbow
            )

        self.write()
        self._rainbow_offset = (self._rainbow_offset + 5) % 360


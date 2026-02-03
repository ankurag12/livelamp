"""
Pump Driver - Simple GPIO on/off control
"""
from machine import Pin


class Pump:
    def __init__(self, pin):
        """
        Initialize pump control

        Args:
            pin: GPIO pin number for pump control
        """
        self.pin = Pin(pin, Pin.OUT)
        self.pin.off()  # Start with pump off
        self._state = False

    def on(self):
        """Turn pump on"""
        self.pin.on()
        self._state = True

    def off(self):
        """Turn pump off"""
        self.pin.off()
        self._state = False

    def toggle(self):
        """Toggle pump state"""
        if self._state:
            self.off()
        else:
            self.on()

    def is_on(self):
        """Check if pump is currently on"""
        return self._state

    def get_state(self):
        """Get current state as dict for API responses"""
        return {"on": self._state}

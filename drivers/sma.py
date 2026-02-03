"""
SMA (Shape Memory Alloy) Wire Driver - PWM control at 25kHz
"""
from machine import Pin, PWM


class SMA:
    def __init__(self, pin, freq=25000):
        """
        Initialize SMA wire PWM control

        Args:
            pin: GPIO pin number for SMA control
            freq: PWM frequency in Hz (default 25kHz for silent operation)
        """
        self.pin = pin
        self.freq = freq
        self.pwm = PWM(Pin(pin), freq=freq)
        self.pwm.duty(0)  # Start with 0% duty cycle (off)
        self._percent = 0

    def set_duty(self, percent):
        """
        Set PWM duty cycle by percentage

        Args:
            percent: Percentage 0-100
        """
        percent = max(0, min(100, percent))
        duty = int(percent * 1023 / 100)
        self.pwm.duty(duty)
        self._percent = percent

    def off(self):
        """Turn SMA off (0% duty cycle)"""
        self.set_duty(0)

    def on(self, percent=100):
        """
        Turn SMA on at specified percentage

        Args:
            percent: Power level as percentage 0-100 (default 100%)
        """
        self.set_duty(percent)

    def get_percent(self):
        """Get current duty cycle as percentage (0-100)"""
        return self._percent

    def get_state(self):
        """Get current state as dict for API responses"""
        return {
            "percent": self._percent,
            "freq": self.freq
        }

    def deinit(self):
        """Deinitialize PWM (cleanup)"""
        self.pwm.deinit()

"""
LiveLamp - Main Entry Point
ESP32-S3 MicroPython firmware for controlling pump, SMA wire, Neopixel ring, and LD2410 sensor
"""
import network
import time
import uasyncio as asyncio
import config
from drivers import Pump, SMA, NeopixelRing, LD2410
from web_server import WebServer


class LiveLamp:
    def __init__(self):
        """Initialize LiveLamp system"""
        print("Initializing LiveLamp...")

        # Initialize hardware drivers
        print("Setting up hardware drivers...")
        self.pump = Pump(config.PIN_PUMP)
        self.sma = SMA(config.PIN_SMA, freq=config.SMA_PWM_FREQ)
        self.leds = NeopixelRing(config.PIN_NEOPIXEL, num_leds=config.NEOPIXEL_COUNT)
        self.radar = LD2410(
            tx_pin=config.PIN_LD2410_TX,
            rx_pin=config.PIN_LD2410_RX,
            presence_pin=config.PIN_LD2410_PRESENCE,
            uart_id=config.LD2410_UART_ID,
            baudrate=config.LD2410_BAUDRATE
        )

        print("Hardware initialized successfully!")

        # WiFi connection
        self.wlan = None
        self.ip_address = None

        # Sensor data and automation control
        self.automation_enabled = False

    def connect_wifi(self):
        """Connect to WiFi network"""
        print(f"Connecting to WiFi: '{config.WIFI_SSID}'...")
        print(f"Password length: {len(config.WIFI_PASSWORD)} chars")

        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)

        # Disconnect if already connected
        if self.wlan.isconnected():
            self.wlan.disconnect()
            time.sleep(1)

        # Setup mDNS
        try:
            self.wlan.config(dhcp_hostname=config.MDNS_HOSTNAME)
            print(f'mDNS enabled: http://{config.MDNS_HOSTNAME}.local')
        except Exception as e:
            print(f'mDNS setup failed: {e}')
            
        # Connect
        self.wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)

        # Wait for connection - use isconnected() instead of status()
        print("Waiting for connection", end='')
        max_wait = 30
        while max_wait > 0:
            if self.wlan.isconnected():
                print(" Connected!")
                break
            max_wait -= 1
            print('.', end='')
            time.sleep(1)

        print()

        # Check if connected
        if not self.wlan.isconnected():
            status = self.wlan.status()
            print(f'WiFi connection failed!')
            print(f'Status code: {status}')
            print('Check .wifi file credentials and ensure router is on 2.4GHz')
            return False

        # Successfully connected
        self.ip_address = self.wlan.ifconfig()[0]
        print(f'WiFi connected! IP: {self.ip_address}')

        return True

    async def sensor_task(self):
        """
        Async task to continuously read sensor data
        This runs concurrently with the web server
        """
        print("Starting sensor reading task...")
        while True:
            try:
                # Read radar sensor data
                self.radar.read_data()

                # Add your sensor-based automation logic here
                # Example:
                # if self.automation_enabled:
                #     radar_data = self.radar.get_state()
                #     if radar_data['presence']:
                #         self.sma.set_duty(50)  # Turn on SMA at 50%
                #     else:
                #         self.sma.off()

                # Sleep to prevent busy loop (adjust as needed)
                await asyncio.sleep_ms(100)

            except Exception as e:
                print(f"Error in sensor task: {e}")
                await asyncio.sleep(1)

    async def pattern_task(self):
        """
        Async task to render LED patterns
        This runs concurrently with the web server and sensor task
        """
        print("Starting LED pattern rendering task...")
        while True:
            try:
                # Render one frame of the current pattern
                self.leds.render_pattern()

                # Sleep based on pattern type for smooth animation
                pattern = self.leds.get_pattern()
                if pattern == 'solid':
                    await asyncio.sleep_ms(100)  # Slow refresh for solid
                elif pattern == 'breathe':
                    await asyncio.sleep_ms(30)  # Breathe speed
                elif pattern == 'fade':
                    await asyncio.sleep_ms(50)  # Slow fade speed
                elif pattern == 'rainbow':
                    await asyncio.sleep_ms(50)  # Rainbow rotation speed
                elif pattern == 'fire':
                    await asyncio.sleep_ms(60)  # Slow warm glow transitions
                elif pattern == 'dream':
                    await asyncio.sleep_ms(30)  # Dream breathe+color speed
                else:
                    await asyncio.sleep_ms(100)  # Default

            except Exception as e:
                print(f"Error in pattern task: {e}")
                await asyncio.sleep(1)

    async def start_tasks(self):
        """Start all async tasks"""
        # Create web server
        web_server = WebServer(self)

        # Run web server, sensor task, and pattern task concurrently
        await asyncio.gather(
            web_server.app.start_server(host=config.WEB_HOST, port=config.WEB_PORT, debug=True),
            self.sensor_task(),
            self.pattern_task()
        )

    def run(self):
        """Main run loop"""
        print("Starting LiveLamp system...")

        # Connect to WiFi
        if not self.connect_wifi():
            print("Cannot start without WiFi connection")
            return

        print("LiveLamp is running!")
        print(f"Access web interface at:")
        print(f"  http://{self.ip_address}")
        print(f"  http://{config.MDNS_HOSTNAME}.local")

        # Start async tasks (web server + sensor reading)
        try:
            asyncio.run(self.start_tasks())
        except KeyboardInterrupt:
            print("\nShutting down...")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup hardware on shutdown"""
        print("Cleaning up...")
        self.pump.off()
        self.sma.off()
        self.leds.off()
        print("Shutdown complete")


# Entry point
if __name__ == "__main__":
    app = LiveLamp()
    app.run()

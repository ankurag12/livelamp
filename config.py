"""
Configuration file for LiveLamp ESP32-S3 Project
Pin assignments and system constants
"""

# ===== GPIO Pin Assignments =====
# Recommended pins for SparkFun Thing Plus ESP32-S3
# These can be overridden when initializing hardware drivers

# Pump control (simple on/off)
PIN_PUMP = 5

# SMA wire PWM control (single pin with PWM)
PIN_SMA = 6
SMA_PWM_FREQ = 25000  # 25kHz for silent operation
SMA_PWM_CHANNEL = 0   # Internal PWM channel (not a physical pin)

# Neopixel LED Ring (12 LEDs - Adafruit #2852)
PIN_NEOPIXEL = 8
NEOPIXEL_COUNT = 12

# LD2410 mmWave Radar Sensor
PIN_LD2410_TX = 17  # ESP32 TX -> LD2410 RX
PIN_LD2410_RX = 18  # ESP32 RX <- LD2410 TX
PIN_LD2410_PRESENCE = 4  # Presence detection GPIO
LD2410_UART_ID = 1
LD2410_BAUDRATE = 256000  # Default LD2410 baudrate

# ===== WiFi Configuration =====
# WiFi credentials are loaded from .wifi file
# Format: first line = SSID, second line = password
try:
    with open('.wifi', 'r') as f:
        lines = f.read().strip().split('\n')
        WIFI_SSID = lines[0].strip()
        WIFI_PASSWORD = lines[1].strip() if len(lines) > 1 else ""
except:
    WIFI_SSID = "your_wifi_ssid"
    WIFI_PASSWORD = "your_wifi_password"
    print("Warning: .wifi file not found, using default credentials")

# ===== Web Server Configuration =====
WEB_PORT = 80
WEB_HOST = "0.0.0.0"
MDNS_HOSTNAME = "livelamp"  # Access via http://livelamp.local

# ===== System Constants =====
# SMA safety timeout (seconds) - matches web UI disable time
SMA_SAFETY_TIMEOUT = 5

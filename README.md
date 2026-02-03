# LiveLamp - ESP32-S3 MicroPython Project

MicroPython firmware for ESP32-S3 to control pump, SMA wire, Neopixel LED ring, and LD2410 radar sensor with a web interface.

## Setup

### 1. Install host tools
```bash
pip install -r requirements.txt
```

### 2. Download microdot library
```bash
curl -L https://raw.githubusercontent.com/miguelgrinberg/microdot/main/src/microdot/microdot.py -o microdot.py
```

### 3. Configure WiFi
Create a `.wifi` file in the project root:
```
your_wifi_ssid
your_wifi_password
```

### 4. Upload to ESP32
```bash
./upload.sh
```

### 5. Access the web interface
After the ESP32 boots, it will print its IP address. You can access the interface at:
- `http://<IP_ADDRESS>` (e.g., http://192.168.1.100)
- `http://livelamp.local` (mDNS - works on most networks)

## Project Structure

```
livelamp/
├── config.py              # Configuration and pin assignments
├── main.py                # Main entry point
├── boot.py                # Auto-run on startup
├── web_server.py          # Web server and REST API
├── drivers/               # Hardware drivers
└── web/                   # Web interface
```

## Pin Configuration

Default pins (configurable in `config.py`):
- Pump: GPIO 5
- SMA Wire: GPIO 6 (25kHz PWM)
- Neopixel: GPIO 8
- LD2410: TX=17, RX=18, Presence=4

You can also customize the mDNS hostname in `config.py` (default: `livelamp.local`).

See `USAGE.md` for web interface details and automation examples.

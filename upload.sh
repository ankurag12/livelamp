#!/bin/bash

# LiveLamp Upload Script
# Uploads all files to ESP32-S3 using mpremote

echo "=== LiveLamp Upload Script ==="

# Check if .wifi file exists
if [ ! -f ".wifi" ]; then
    echo "Error: .wifi file not found!"
    echo "Create a .wifi file with your WiFi credentials:"
    echo "  Line 1: SSID"
    echo "  Line 2: Password"
    exit 1
fi

# Check if microdot.py exists
if [ ! -f "microdot.py" ]; then
    echo "Error: microdot.py not found!"
    echo "Download it with:"
    echo "  curl -L https://raw.githubusercontent.com/miguelgrinberg/microdot/main/src/microdot/microdot.py -o microdot.py"
    exit 1
fi

echo "Uploading files to ESP32..."

# Upload configuration and main files
echo "- Uploading core files..."
mpremote cp config.py :
mpremote cp main.py :
mpremote cp boot.py :
mpremote cp web_server.py :
mpremote cp microdot.py :
mpremote cp .wifi :

# Upload drivers directory recursively
echo "- Uploading drivers..."
mpremote cp -r drivers :

# Upload web directory recursively
echo "- Uploading web interface..."
mpremote cp -r web :

echo ""
echo "=== Upload Complete ==="
echo "Rebooting ESP32..."
mpremote soft-reset

echo ""
echo "Connect to serial monitor to see IP address and debug info:"
echo "  mpremote connect /dev/cu.usbmodem101"
echo ""
echo "If device path is different, find it with:"
echo "  ls /dev/cu.usbmodem*    # macOS"
echo "  ls /dev/ttyUSB*         # Linux"
echo "  ls /dev/ttyACM*         # Linux (alternative)"

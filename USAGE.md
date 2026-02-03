# LiveLamp Usage Guide

## Web Interface

Once running, access the web interface at `http://<ESP32_IP_ADDRESS>`.

### Control Widgets

#### 1. Pump Control
- **Momentary Push Button**: Press and hold to activate the pump
- Releases automatically when you let go
- Use for precise on-demand pump control

#### 2. SMA Wire Control
- **Slider**: Adjust power level from 0-100%
- **Activate Button**: Apply the selected power level to the SMA wire
- **Safety Feature**: Button is disabled for 5 seconds after each activation to prevent overheating
- Current power level is displayed above the slider

#### 3. LED Color Control
- **Color Wheel**: Click to select any RGB color
- Changes apply immediately to all 12 LEDs in the ring
- **Turn Off Button**: Instantly turns off all LEDs (sets to black)
- Current color is shown in the preview box

#### 4. Radar Sensor Display
- **Presence Indicator**: Green when presence detected, red when no presence
- **Target State**: Shows if target is moving, static, both, or none
- **Detection Distance**: Distance to detected target in centimeters
- **Moving Energy**: Energy level of moving target (0-100)
- **Static Energy**: Energy level of static target (0-100)
- Updates automatically every 500ms

## REST API Endpoints

All endpoints return JSON responses.

### Pump
**GET /api/pump**
```json
{
  "on": false
}
```

**POST /api/pump**
Request:
```json
{
  "on": true
}
```
Response:
```json
{
  "on": true
}
```

### SMA Wire
**GET /api/sma**
```json
{
  "percent": 50,
  "freq": 25000
}
```

**POST /api/sma**
Request:
```json
{
  "percent": 75
}
```
Response:
```json
{
  "percent": 75,
  "freq": 25000
}
```

### LEDs
**GET /api/leds**
```json
{
  "r": 255,
  "g": 0,
  "b": 0,
  "hex": "#ff0000"
}
```

**POST /api/leds** (hex format)
Request:
```json
{
  "hex": "#00ff00"
}
```

**POST /api/leds** (RGB format)
Request:
```json
{
  "r": 0,
  "g": 255,
  "b": 0
}
```

Response:
```json
{
  "r": 0,
  "g": 255,
  "b": 0,
  "hex": "#00ff00"
}
```

### Radar Sensor
**GET /api/radar**
```json
{
  "presence": true,
  "presence_gpio": true,
  "target_state": 1,
  "moving_distance": 150,
  "moving_energy": 65,
  "static_distance": 0,
  "static_energy": 0,
  "detection_distance": 150
}
```

**Target State Values:**
- `0`: No target
- `1`: Moving target
- `2`: Static target
- `3`: Both moving and static

## Sensor-Based Automation

The `sensor_task()` async function in `main.py` runs continuously alongside the web server. Use it to implement automation logic based on sensor readings.

### Example 1: Activate SMA on Presence Detection

```python
async def sensor_task(self):
    """Activate SMA wire when presence is detected"""
    print("Starting sensor reading task...")
    while True:
        try:
            # Read radar sensor data
            self.radar.read_data()
            radar_data = self.radar.get_state()

            # Check for presence
            if radar_data['presence'] or radar_data['presence_gpio']:
                # Turn on SMA at 50% when presence detected
                self.sma.set_duty(50)
                # Optional: Change LED color to green
                self.leds.set_color(0, 255, 0)
            else:
                # Turn off SMA when no presence
                self.sma.off()
                # Optional: Change LED color to blue
                self.leds.set_color(0, 0, 255)

            await asyncio.sleep_ms(100)

        except Exception as e:
            print(f"Error in sensor task: {e}")
            await asyncio.sleep(1)
```

### Example 2: Distance-Based SMA Power Control

```python
async def sensor_task(self):
    """Adjust SMA power based on target distance"""
    print("Starting sensor reading task...")
    while True:
        try:
            self.radar.read_data()
            radar_data = self.radar.get_state()

            if radar_data['presence']:
                distance = radar_data['detection_distance']

                # Map distance (0-300cm) to power (0-100%)
                # Closer = more power
                if distance > 0:
                    power = max(0, min(100, int((300 - distance) / 3)))
                    self.sma.set_duty(power)

                    # Visual feedback via LEDs
                    # Red = close, Blue = far
                    r = int(power * 2.55)
                    b = int((100 - power) * 2.55)
                    self.leds.set_color(r, 0, b)
            else:
                self.sma.off()
                self.leds.off()

            await asyncio.sleep_ms(100)

        except Exception as e:
            print(f"Error in sensor task: {e}")
            await asyncio.sleep(1)
```

### Example 3: Moving vs Static Target Behavior

```python
async def sensor_task(self):
    """Different behavior for moving vs static targets"""
    print("Starting sensor reading task...")
    while True:
        try:
            self.radar.read_data()
            radar_data = self.radar.get_state()

            target_state = radar_data['target_state']

            if target_state == 1:  # Moving target
                # Pulse SMA for moving targets
                self.sma.set_duty(30)
                self.leds.set_color(255, 165, 0)  # Orange
                self.pump.on()  # Activate pump

            elif target_state == 2:  # Static target
                # Steady SMA for static targets
                self.sma.set_duty(60)
                self.leds.set_color(0, 255, 255)  # Cyan
                self.pump.off()

            elif target_state == 3:  # Both
                # Max power for both
                self.sma.set_duty(100)
                self.leds.set_color(255, 0, 255)  # Magenta
                self.pump.on()

            else:  # No target
                self.sma.off()
                self.leds.off()
                self.pump.off()

            await asyncio.sleep_ms(100)

        except Exception as e:
            print(f"Error in sensor task: {e}")
            await asyncio.sleep(1)
```

### Example 4: Enable/Disable Automation via API

Add an automation toggle endpoint:

In `web_server.py`, add:

```python
@self.app.route('/api/automation', methods=['GET'])
async def get_automation(request):
    return {'enabled': self.livelamp.automation_enabled}

@self.app.route('/api/automation', methods=['POST'])
async def set_automation(request):
    data = request.json
    if data and 'enabled' in data:
        self.livelamp.automation_enabled = data['enabled']
        return {'enabled': self.livelamp.automation_enabled}
    return {'error': 'Invalid request'}, 400
```

In `main.py` `sensor_task()`:

```python
async def sensor_task(self):
    """Automation that can be toggled on/off"""
    print("Starting sensor reading task...")
    while True:
        try:
            # Always read sensor data
            self.radar.read_data()

            # Only run automation if enabled
            if self.automation_enabled:
                radar_data = self.radar.get_state()

                if radar_data['presence']:
                    self.sma.set_duty(50)
                else:
                    self.sma.off()
            # Otherwise, manual control via web interface only

            await asyncio.sleep_ms(100)

        except Exception as e:
            print(f"Error in sensor task: {e}")
            await asyncio.sleep(1)
```

Then control from web interface:
```javascript
// Enable automation
fetch('/api/automation', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({enabled: true})
});
```

## Tips

- **Sensor Update Rate**: Adjust `asyncio.sleep_ms(100)` in `sensor_task()` to change how often sensors are polled (100ms = 10 times per second)
- **SMA Safety**: Always monitor SMA wire temperature to prevent overheating
- **LED Brightness**: Neopixels can be bright - reduce RGB values if needed (e.g., `set_color(50, 0, 0)` instead of `255, 0, 0`)
- **Pump Protection**: Add logic to prevent pump from running dry or for too long
- **Memory**: If running low on memory, increase `await asyncio.sleep_ms()` value or reduce polling frequency

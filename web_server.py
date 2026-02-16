"""
Web Server with REST API using microdot
Handles HTTP requests for controlling hardware and serving web interface
"""
from microdot import Microdot, Response
import json


class WebServer:
    def __init__(self, livelamp):
        """
        Initialize web server with microdot

        Args:
            livelamp: LiveLamp instance with hardware drivers
        """
        self.livelamp = livelamp
        self.app = Microdot()
        self._setup_routes()

    def _setup_routes(self):
        """Setup all HTTP routes"""

        # Serve main web interface
        @self.app.route('/')
        async def index(request):
            try:
                with open('web/index.html', 'r') as f:
                    html = f.read()
                return Response(html, headers={'Content-Type': 'text/html'})
            except:
                return Response('<h1>LiveLamp</h1><p>Web interface not found</p>', status_code=404)

        # Pump API endpoints
        @self.app.route('/api/pump', methods=['GET'])
        async def get_pump(request):
            return self.livelamp.pump.get_state()

        @self.app.route('/api/pump', methods=['POST'])
        async def control_pump(request):
            data = request.json
            if data and 'on' in data:
                if data['on']:
                    self.livelamp.pump.on()
                else:
                    self.livelamp.pump.off()
                return self.livelamp.pump.get_state()
            return {'error': 'Invalid request'}, 400

        # SMA API endpoints
        @self.app.route('/api/sma', methods=['GET'])
        async def get_sma(request):
            return self.livelamp.sma.get_state()

        @self.app.route('/api/sma', methods=['POST'])
        async def control_sma(request):
            data = request.json
            if data and 'percent' in data:
                percent = data['percent']
                self.livelamp.sma.set_duty(percent)
                return self.livelamp.sma.get_state()
            return {'error': 'Invalid request'}, 400

        # LED API endpoints
        @self.app.route('/api/leds', methods=['GET'])
        async def get_leds(request):
            return self.livelamp.leds.get_state()

        @self.app.route('/api/leds', methods=['POST'])
        async def control_leds(request):
            data = request.json
            if data:
                if 'hex' in data:
                    self.livelamp.leds.set_color_hex(data['hex'])
                elif 'r' in data and 'g' in data and 'b' in data:
                    self.livelamp.leds.set_color(data['r'], data['g'], data['b'])
                else:
                    return {'error': 'Invalid color format'}, 400
                return self.livelamp.leds.get_state()
            return {'error': 'Invalid request'}, 400

        @self.app.route('/api/leds/white', methods=['POST'])
        async def control_leds_white(request):
            data = request.json
            if data and 'brightness' in data:
                brightness = data['brightness']
                self.livelamp.leds.set_white(brightness)
                return {'white': brightness}
            return {'error': 'Invalid request'}, 400

        # Radar API endpoints
        @self.app.route('/api/radar', methods=['GET'])
        async def get_radar(request):
            # Read latest data
            self.livelamp.radar.read_data()
            return self.livelamp.radar.get_state()

    def start(self, host='0.0.0.0', port=80):
        """
        Start the web server

        Args:
            host: Server host address
            port: Server port
        """
        print(f"Starting web server on {host}:{port}")
        self.app.run(host=host, port=port, debug=True)

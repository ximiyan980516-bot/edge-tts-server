from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import asyncio
import edge_tts
import io
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # CORS headers
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')

        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        text = params.get('text', [''])[0]
        voice = params.get('voice', ['zh-CN-XiaoxiaoNeural'])[0]
        rate = params.get('rate', ['+0%'])[0]
        pitch = params.get('pitch', ['+0Hz'])[0]

        if not text:
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Missing text'}).encode())
            return

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_data = loop.run_until_complete(synthesize(text, voice, rate, pitch))
            loop.close()

            self.send_header('Content-Type', 'audio/mpeg')
            self.send_header('Content-Length', str(len(audio_data)))
            self.send_header('Cache-Control', 'public, max-age=86400')
            self.end_headers()
            self.wfile.write(audio_data)
        except Exception as e:
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

async def synthesize(text, voice, rate, pitch):
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    buf = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buf.write(chunk["data"])
    return buf.getvalue()

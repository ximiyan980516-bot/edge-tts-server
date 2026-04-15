from flask import Flask, request, Response
from flask_cors import CORS
import asyncio
import edge_tts
import io

app = Flask(__name__)
CORS(app)

@app.route('/tts')
def tts():
    text = request.args.get('text', '')
    voice = request.args.get('voice', 'zh-CN-XiaoxiaoNeural')
    rate = request.args.get('rate', '+0%')
    pitch = request.args.get('pitch', '+0Hz')

    if not text:
        return 'Missing text', 400

    try:
        audio_data = asyncio.run(synthesize(text, voice, rate, pitch))
        return Response(audio_data, mimetype='audio/mpeg')
    except Exception as e:
        print(f"TTS Error: {e}")
        return str(e), 500

async def synthesize(text, voice, rate, pitch):
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    buf = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buf.write(chunk["data"])
    return buf.getvalue()

@app.route('/')
def index():
    return 'Edge TTS Server is running'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

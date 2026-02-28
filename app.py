import os, requests, binascii, re
from flask import Flask, render_template, Response, jsonify

app = Flask(__name__)

ARCHIVE_ID = os.environ.get("ARCHIVE_ID", "").strip()
VIDEO_FILES = os.environ.get("VIDEO_FILES", "").strip().split(',')
HEADERS = {'User-Agent': 'TJS-Plus-Final-v1'}

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/list-vids')
def list_vids(): return jsonify([f for f in VIDEO_FILES if f])

@app.route('/stream/<filename>')
def stream_video(filename):
    def generate():
        url = f"https://archive.org{ARCHIVE_ID}/{filename}"
        with requests.get(url, headers=HEADERS, stream=True) as r:
            hex_cache = ""
            first_chunk = True
            for chunk in r.iter_content(chunk_size=131072):
                if chunk:
                    # 1. Clean the text (Remove ALL non-hex characters)
                    text = chunk.decode('utf-8', errors='ignore')
                    clean = re.sub(r'[^0-9a-fA-F]', '', text)
                    hex_cache += clean
                    
                    # 2. Debug Log (Check Render Logs for this!)
                    if first_chunk and len(hex_cache) >= 16:
                        print(f"DEBUG: First 16 hex chars: {hex_cache[:16]}")
                        first_chunk = False

                    # 3. Decode and Yield
                    if len(hex_cache) >= 2:
                        usable = (len(hex_cache) // 2) * 2
                        yield binascii.unhexlify(hex_cache[:usable])
                        hex_cache = hex_cache[usable:]

    return Response(generate(), mimetype='video/mp4')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

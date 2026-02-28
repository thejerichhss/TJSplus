import os, requests, binascii, re
from flask import Flask, render_template, Response, jsonify

app = Flask(__name__)

ARCHIVE_ID = os.environ.get("ARCHIVE_ID", "").strip()
VIDEO_FILES = os.environ.get("VIDEO_FILES", "").strip().split(',')

BASE_URL = f"https://archive.org{ARCHIVE_ID}/"
HEADERS = {'User-Agent': 'Mozilla/5.0 (TJS-Plus-Private)'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/list-vids')
def list_vids():
    if not VIDEO_FILES or VIDEO_FILES == ['']:
        return jsonify([])
    return jsonify(VIDEO_FILES)
    
@app.route('/stream/<filename>')
def stream_video(filename):
    def generate():
        url = f"https://archive.org{ARCHIVE_ID}/{filename}"
        with requests.get(url, headers=HEADERS, stream=True) as r:
            hex_cache = ""
            for chunk in r.iter_content(chunk_size=262144): # 256KB for speed
                if chunk:
                    # 1. Convert bytes to text
                    text_chunk = chunk.decode('utf-8', errors='ignore')
                    # 2. STRIP EVERYTHING except 0-9 and a-f
                    clean_hex = re.sub(r'[^0-9a-fA-F]', '', text_chunk)
                    hex_cache += clean_hex
                    
                    # 3. Decode only complete pairs
                    if len(hex_cache) >= 2:
                        usable_len = (len(hex_cache) // 2) * 2
                        yield binascii.unhexlify(hex_cache[:usable_len])
                        hex_cache = hex_cache[usable_len:]

    # Force the browser to see it as a standard MP4
    return Response(generate(), mimetype='video/mp4')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

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
        url = BASE_URL + filename
        with requests.get(url, headers=HEADERS, stream=True) as r:
            hex_cache = ""
            for chunk in r.iter_content(chunk_size=131072): # 128KB
                if chunk:
                    clean_text = chunk.decode('utf-8', errors='ignore')
                    # Keep only hex characters
                    hex_cache += re.sub(r'[^0-9a-fA-F]', '', clean_text)
                    
                    if len(hex_cache) >= 2:
                        usable = (len(hex_cache) // 2) * 2
                        yield binascii.unhexlify(hex_cache[:usable])
                        hex_cache = hex_cache[usable:]

    return Response(generate(), mimetype='video/mp4')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

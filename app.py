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
        url = f"https://archive.org/{ARCHIVE_ID}/{filename}"
        # Using a smaller initial chunk to trigger the player faster
        with requests.get(url, headers=HEADERS, stream=True) as r:
            hex_cache = ""
            for chunk in r.iter_content(chunk_size=65536): # 64KB chunks
                if chunk:
                    text = chunk.decode('utf-8', errors='ignore')
                    # Aggressive cleaning for the new True Hex format
                    hex_cache += re.sub(r'[^0-9a-fA-F]', '', text)
                    
                    if len(hex_cache) >= 2:
                        usable = (len(hex_cache) // 2) * 2
                        yield binascii.unhexlify(hex_cache[:usable])
                        hex_cache = hex_cache[usable:]
    return Response(generate(), mimetype='video/mp4')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

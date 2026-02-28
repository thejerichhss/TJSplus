import os, requests, base64, re
from flask import Flask, render_template, Response, jsonify

app = Flask(__name__)

ARCHIVE_ID = os.environ.get("ARCHIVE_ID", "").strip()
VIDEO_FILES = os.environ.get("VIDEO_FILES", "").strip().split(',')
HEADERS = {'User-Agent': 'TJS-Plus-B64-v1'}

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/list-vids')
def list_vids(): return jsonify([f for f in VIDEO_FILES if f])

@app.route('/stream/<filename>')
def stream_video(filename):
    url = f"https://archive.org/{ARCHIVE_ID}/{filename}"
    def generate():
        with requests.get(url, headers=HEADERS, stream=True) as r:
            b64_cache = ""
            for chunk in r.iter_content(chunk_size=262144):
                if chunk:
                    text = chunk.decode('utf-8', errors='ignore')
                    # Strip any newlines or illegal characters
                    b64_cache += re.sub(r'[^a-zA-Z0-9+/=]', '', text)
                    while len(b64_cache) >= 4:
                        usable = (len(b64_cache) // 4) * 4
                        yield base64.b64decode(b64_cache[:usable])
                        b64_cache = b64_cache[usable:]
    return Response(generate(), mimetype='video/mp4')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

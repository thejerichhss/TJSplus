import os, requests, binascii, re
from flask import Flask, render_template, Response, jsonify

app = Flask(__name__)

ARCHIVE_ID = os.environ.get("ARCHIVE_ID", "").strip()
VIDEO_FILES = os.environ.get("VIDEO_FILES", "").strip().split(',')
HEADERS = {'User-Agent': 'TJS-Plus-v3'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/list-vids')
def list_vids():
    return jsonify([f for f in VIDEO_FILES if f])

@app.route('/stream/<filename>')
def stream_video(filename):
    url = f"https://archive.org/{ARCHIVE_ID}/{filename}"
    
    # Pre-fetch headers to get content length for the browser
    head = requests.head(url, headers=HEADERS)
    hex_size = int(head.headers.get('content-length', 0))
    video_size = hex_size // 2 

    def generate():
        with requests.get(url, headers=HEADERS, stream=True) as r:
            hex_cache = ""
            for chunk in r.iter_content(chunk_size=131072):
                if chunk:
                    text = chunk.decode('utf-8', errors='ignore')
                    # Strip any newlines or non-hex formatting
                    hex_cache += re.sub(r'[^0-9a-fA-F]', '', text)
                    while len(hex_cache) >= 2:
                        yield binascii.unhexlify(hex_cache[:2])
                        hex_cache = hex_cache[2:]

    return Response(
        generate(),
        mimetype='video/mp4',
        headers={
            'Accept-Ranges': 'bytes',
            'Content-Length': str(video_size)
        }
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

import os, requests, binascii
from flask import Flask, render_template, Response, jsonify

app = Flask(__name__)

ARCHIVE_ID = os.environ.get("ARCHIVE_ID")
BASE = f"https://archive.org{ARCHIVE_ID}/"
META = f"https://archive.org{ARCHIVE_ID}"

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/api/list-vids')
def list_vids():
    if not ARCHIVE_ID: return jsonify([])
    try:
        r = requests.get(META).json()
        return jsonify([f['name'] for f in r['files'] if f['name'].endswith('.txt')])
    except: return jsonify([])

@app.route('/stream/<filename>')
def stream_video(filename):
    if not ARCHIVE_ID: return "System Locked", 403
    
    def generate():
        url = BASE + filename
        with requests.get(url, stream=True) as r:
            hex_cache = ""
            for chunk in r.iter_content(chunk_size=16384):
                hex_cache += chunk.decode('utf-8')
                if len(hex_cache) >= 2:
                    to_decode = hex_cache[:len(hex_cache) // 2 * 2]
                    hex_cache = hex_cache[len(hex_cache) // 2 * 2:]
                    yield binascii.unhexlify(to_decode)
    
    return Response(generate(), mimetype='video/mp4')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

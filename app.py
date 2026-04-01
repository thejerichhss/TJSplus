import os
import requests
import re
from flask import Flask, render_template, Response, jsonify

app = Flask(__name__)

raw_id = os.environ.get("ARCHIVE_ID", "").strip()
ARCHIVE_ID = re.sub(r'[^a-zA-Z0-9\-_]', '', raw_id)
HEADERS = {'User-Agent': 'TJS-Plus-v2'}

def get_archive_files():
    url = f"https://archive.org{ARCHIVE_ID}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return []
        data = r.json()
        if 'files' not in data:
            return []
        return sorted([f['name'] for f in data['files'] if f.get('name', '').lower().endswith('.mp4')])
    except:
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/list-vids')
def list_vids():
    return jsonify(get_archive_files())

@app.route('/stream/<filename>')
def stream_video(filename):
    target_url = f"https://archive.org{ARCHIVE_ID}/{filename}"
    def generate():
        with requests.get(target_url, headers=HEADERS, stream=True) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=262144):
                yield chunk
    return Response(generate(), mimetype='video/mp4')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

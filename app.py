import os, requests
from flask import Flask, render_template, Response, jsonify
from pathlib import Path

app = Flask(__name__) 

ARCHIVE_ID = os.environ.get("ARCHIVE_ID", "").strip() 
VIDEOS_DIR = os.environ.get("VIDEOS_DIR", "./videos")
HEADERS = {'User-Agent': 'TJS-Plus-v1'}

def get_mp4_files():
    """Dynamically discover all .mp4 files in the videos directory"""
    if not os.path.exists(VIDEOS_DIR):
        return []
    return sorted([f.name for f in Path(VIDEOS_DIR).glob("*.mp4")])

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/list-vids')
def list_vids(): return jsonify(get_mp4_files())

@app.route('/stream/<filename>')
def stream_video(filename):
    file_path = os.path.join(VIDEOS_DIR, filename)
    
    # Security check: ensure the file is in the videos directory
    if not os.path.abspath(file_path).startswith(os.path.abspath(VIDEOS_DIR)):
        return "Forbidden", 403
    
    if not os.path.exists(file_path):
        return "Not Found", 404
    
    def generate():
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(262144)
                if not chunk:
                    break
                yield chunk
    
    return Response(generate(), mimetype='video/mp4')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
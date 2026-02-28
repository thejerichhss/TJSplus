import os, requests
from flask import Flask, render_template, Response, jsonify

app = Flask(__name__)

raw_id = os.environ.get("ARCHIVE_ID", "").strip()

ARCHIVE_ID = re.sub(r'[^a-zA-Z0-9_-]+$', '', raw_id)

HEADERS = {'User-Agent': 'TJS-Plus-v1'}

def get_archive_files():
    """Fetch file list from Internet Archive Metadata API"""
    metadata_url = f"https://archive.org{ARCHIVE_ID}"
    try:
        response = requests.get(metadata_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Filter for .mp4 files in the 'files' list
        return sorted([
            f['name'] for f in data.get('files', []) 
            if f.get('name', '').lower().endswith('.mp4')
        ])
    except Exception as e:
        print(f"Error fetching metadata: {e}")
        return []

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/api/list-vids')
def list_vids(): 
    return jsonify(get_archive_files())

@app.route('/stream/<filename>')
def stream_video(filename):
    target_url = f"https://archive.org/{ARCHIVE_ID}/{filename}"
    
    def generate():
        # Proxy the stream from IA to the user
        with requests.get(target_url, headers=HEADERS, stream=True) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=262144):
                yield chunk

    return Response(generate(), mimetype='video/mp4')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

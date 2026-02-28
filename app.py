import os, requests, binascii, re
from flask import Flask, render_template, Response, jsonify

app = Flask(__name__)

# Pull from Render Environment Variables
ARCHIVE_ID = os.environ.get("ARCHIVE_ID")
BASE_URL = f"https://archive.org{ARCHIVE_ID}/"
META_URL = f"https://archive.org{ARCHIVE_ID}"
HEADERS = {'User-Agent': 'Mozilla/5.0 (TJS-Plus-Reassembler)'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/list-vids')
def list_vids():
    if not ARCHIVE_ID:
        return jsonify([])
    try:
        # Try Metadata API first
        r = requests.get(META_URL, headers=HEADERS, timeout=10).json()
        files = [f['name'] for f in r.get('files', []) if f['name'].endswith('.txt')]
        
        # Fallback: Scrape the download page if Metadata is empty
        if not files:
            page = requests.get(BASE_URL, headers=HEADERS, timeout=10).text
            files = re.findall(r'href="([^"]+\.txt)"', page)
            
        return jsonify(list(set(files)))
    except Exception as e:
        print(f"Scrape Error: {e}")
        return jsonify([])

@app.route('/stream/<filename>')
def stream_video(filename):
    def generate():
        target_url = BASE_URL + filename
        with requests.get(target_url, headers=HEADERS, stream=True) as r:
            hex_cache = ""
            for chunk in r.iter_content(chunk_size=32768):
                if chunk:
                    # Convert raw bytes from Archive.org to string characters
                    hex_cache += chunk.decode('utf-8', errors='ignore')
                    
                    # Hex needs pairs (2 characters = 1 byte)
                    if len(hex_cache) >= 2:
                        usable_len = (len(hex_cache) // 2) * 2
                        to_decode = hex_cache[:usable_len]
                        hex_cache = hex_cache[usable_len:]
                        
                        try:
                            yield binascii.unhexlify(to_decode)
                        except Exception:
                            continue # Skip corrupted hex pairs

    return Response(generate(), mimetype='video/mp4')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

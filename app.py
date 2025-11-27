"""
Sora 2 Video Generator - Flask Backend
"""

import os
import base64
import re
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from openai import OpenAI

import dotenv
dotenv.load_dotenv()


app = Flask(__name__, static_folder='static')
CORS(app)

client = None

def get_client():
    global client
    api_key = os.environ.get('OPENAI_API_KEY', '')
    if api_key and api_key != 'sk-your-api-key-here':
        if client is None:
            client = OpenAI(api_key=api_key)
        return client
    return None

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/check-key', methods=['GET'])
def check_api_key():
    if get_client() is None:
        return jsonify({"configured": False})
    return jsonify({"configured": True})

def parse_data_url(data_url):
    """Parse a data URL and return (mime_type, bytes_data)"""
    # Format: data:image/png;base64,iVBORw0KGgo...
    match = re.match(r'data:([^;]+);base64,(.+)', data_url)
    if match:
        mime_type = match.group(1)
        base64_data = match.group(2)
        bytes_data = base64.b64decode(base64_data)
        return mime_type, bytes_data
    return None, None

@app.route('/api/generate', methods=['POST'])
def generate_video():
    """Start video generation with Sora 2"""
    openai_client = get_client()
    if openai_client is None:
        return jsonify({"error": "API key not configured"}), 401
    
    data = request.json
    prompt = data.get('prompt', '')
    model = data.get('model', 'sora-2')
    resolution = data.get('resolution', '1920x1080')
    duration = data.get('duration', "5")
    input_reference_data = data.get('input_reference')  # Optional reference image (base64 data URL)
    
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    
    try:
        # Build the video create parameters
        create_params = {
            "model": model,
            "prompt": prompt,
            "size": resolution,
            "seconds": str(duration),
        }
        
        # Add input_reference if provided (for image-to-video generation)
        # Convert base64 data URL to bytes tuple format required by OpenAI
        if input_reference_data:
            mime_type, image_bytes = parse_data_url(input_reference_data)
            if image_bytes:
                # Get file extension from mime type
                ext = mime_type.split('/')[-1] if mime_type else 'png'
                if ext == 'jpeg':
                    ext = 'jpg'
                # Format: tuple of (filename, file_content, content_type) - single file, not array
                create_params["input_reference"] = (f"reference.{ext}", image_bytes, mime_type)
        
        video = openai_client.videos.create(**create_params)
        
        return jsonify({
            "success": True,
            "id": video.id,
            "status": video.status,
            "progress": getattr(video, 'progress', 0),
        })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/status/<video_id>', methods=['GET'])
def check_status(video_id):
    """Check video generation status"""
    openai_client = get_client()
    if openai_client is None:
        return jsonify({"error": "API key not configured"}), 401
    
    try:
        video = openai_client.videos.retrieve(video_id)
        return jsonify({
            "id": video.id,
            "status": video.status,
            "progress": getattr(video, 'progress', 0),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/download/<video_id>', methods=['GET'])
def download_video(video_id):
    """Download completed video content"""
    openai_client = get_client()
    if openai_client is None:
        return jsonify({"error": "API key not configured"}), 401
    
    try:
        content = openai_client.videos.download_content(video_id)
        return Response(
            content.read(),
            mimetype='video/mp4',
            headers={'Content-Disposition': f'attachment; filename={video_id}.mp4'}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    
    print("=" * 50)
    print("Sora 2 Video Generator")
    print("=" * 50)
    if get_client() is not None:
        print("✓ API Key configured")
    else:
        print("⚠ Set OPENAI_API_KEY environment variable")
    print("http://localhost:5000")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

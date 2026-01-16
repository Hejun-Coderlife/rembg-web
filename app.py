from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from rembg import remove
from PIL import Image
import io
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Enable CORS for frontend

# Create uploads directory if it doesn't exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('outputs', exist_ok=True)

@app.route('/')
def index():
    html_path = os.path.join(os.path.dirname(__file__), 'index.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/api/remove-background', methods=['POST'])
def remove_background():
    try:
        # Check if file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read image file
        input_image = file.read()
        
        # Remove background using rembg
        output_image = remove(input_image)
        
        # Convert to base64 for sending to frontend
        import base64
        output_base64 = base64.b64encode(output_image).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{output_base64}'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port)

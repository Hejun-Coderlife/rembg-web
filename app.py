from flask import Flask, request, jsonify
from flask_cors import CORS
from rembg import new_session, remove
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Enable CORS for frontend

# Create uploads directory if it doesn't exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('outputs', exist_ok=True)

# Initialize rembg session
rembg_session = new_session('u2net')  # General-purpose model

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
            return jsonify({'success': False, 'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Read image file (no size limit)
        input_image = file.read()
        
        if not input_image or len(input_image) == 0:
            return jsonify({'success': False, 'error': 'Empty image file'}), 400
        
        # Remove background using rembg
        output_image = remove(input_image, session=rembg_session)
        
        if not output_image or len(output_image) == 0:
            return jsonify({'success': False, 'error': 'Background removal produced no output'}), 500
        
        # Convert to base64 for sending to frontend
        import base64
        output_base64 = base64.b64encode(output_image).decode('utf-8')
        
        print("Returning success response")
        response = jsonify({
            'success': True,
            'image': f'data:image/png;base64,{output_base64}'
        })
        return response
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in remove_background: {error_details}")  # Log for debugging
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port)

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from rembg import new_session, remove
from PIL import Image
import io
import os
import gc

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Enable CORS for frontend

# Create uploads directory if it doesn't exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('outputs', exist_ok=True)

# Initialize rembg session lazily (only when needed)
rembg_session = None

def get_rembg_session():
    global rembg_session
    if rembg_session is None:
        rembg_session = new_session('u2netp')  # Lighter model for free tier
    return rembg_session

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
        
        # Check file size (limit to 5MB to prevent memory issues)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > 5 * 1024 * 1024:  # 5MB limit
            return jsonify({'success': False, 'error': 'Image too large. Please use images under 5MB.'}), 400
        
        # Read image file
        input_image = file.read()
        
        if not input_image or len(input_image) == 0:
            return jsonify({'success': False, 'error': 'Empty image file'}), 400
        
        print(f"Processing image: {len(input_image)} bytes")  # Log for debugging
        
        # Resize image if too large to save memory (max 1024px on longest side)
        try:
            img = Image.open(io.BytesIO(input_image))
            original_size = (img.width, img.height)
            if img.width > 1024 or img.height > 1024:
                print(f"Resizing image from {original_size} to max 1024px")
                img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                buffer = io.BytesIO()
                img.save(buffer, format='PNG', optimize=True)
                input_image = buffer.getvalue()
                print(f"Resized image: {len(input_image)} bytes")
                del img, buffer
                gc.collect()
        except Exception as resize_error:
            print(f"Resize warning: {str(resize_error)}, using original image")
            # Continue with original image if resize fails
        
        # Remove background using rembg (reuse session to save memory)
        try:
            print("Getting rembg session...")
            session = get_rembg_session()
            print("Removing background...")
            output_image = remove(input_image, session=session)
            print(f"Background removed: {len(output_image) if output_image else 0} bytes")
        except MemoryError:
            return jsonify({'success': False, 'error': 'Out of memory. Image too large or complex.'}), 500
        except Exception as model_error:
            print(f"Model error: {str(model_error)}")
            return jsonify({'success': False, 'error': f'Background removal failed: {str(model_error)}'}), 500
        
        # Clean up memory
        del input_image
        gc.collect()
        
        if not output_image or len(output_image) == 0:
            return jsonify({'success': False, 'error': 'Background removal produced no output'}), 500
        
        # Convert to base64 for sending to frontend
        import base64
        try:
            print("Encoding to base64...")
            output_base64 = base64.b64encode(output_image).decode('utf-8')
            print(f"Encoded: {len(output_base64)} characters")
        except Exception as encode_error:
            print(f"Encoding error: {str(encode_error)}")
            return jsonify({'success': False, 'error': f'Encoding failed: {str(encode_error)}'}), 500
        
        del output_image
        gc.collect()
        
        print("Returning success response")
        response = jsonify({
            'success': True,
            'image': f'data:image/png;base64,{output_base64}'
        })
        return response
    
    except MemoryError:
        return jsonify({'success': False, 'error': 'Out of memory. Please try a smaller image.'}), 500
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

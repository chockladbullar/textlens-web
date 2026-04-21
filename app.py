import os
import base64
import io
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from PIL import Image, ImageOps, ImageFilter
import pytesseract
from pdf2image import convert_from_bytes

app = Flask(__name__, static_folder='static')

def preprocess_image(image):
    """
    Improves OCR accuracy by cleaning up the image.
    """
    # 1. Convert to grayscale
    image = image.convert('L')
    
    # 2. Increase contrast and normalize
    image = ImageOps.autocontrast(image)
    
    # 3. Upscale if the image is too small (Tesseract loves 300DPI equivalent)
    # If width is less than 2000px, we scale it up
    if image.width < 2000:
        scale_factor = 2
        image = image.resize((image.width * scale_factor, image.height * scale_factor), Image.Resampling.LANCZOS)
    
    # 4. Optional: Sharpening to make characters stand out
    image = image.filter(ImageFilter.SHARPEN)
    
    return image

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/ocr', methods=['POST'])
def ocr_process():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data'}), 400

        file_bytes = base64.b64decode(data['image'])
        is_pdf = data.get('is_pdf', False)
        lang = data.get('lang', 'aze')

        # Custom configuration: 
        # --psm 3: Fully automatic page segmentation, but no orientation and script detection. (Default)
        # --oem 3: Default OCR engine mode
        custom_config = r'--oem 3 --psm 3'

        extracted_text = ""
        
        if is_pdf:
            # Increase DPI to 300 for better PDF extraction
            images = convert_from_bytes(file_bytes, dpi=300, first_page=1, last_page=5)
            for i, img in enumerate(images):
                img = preprocess_image(img)
                page_text = pytesseract.image_to_string(img, lang=lang, config=custom_config)
                extracted_text += f"--- Page {i+1} ---\n{page_text}\n\n"
        else:
            image = Image.open(io.BytesIO(file_bytes))
            image = preprocess_image(image)
            extracted_text = pytesseract.image_to_string(image, lang=lang, config=custom_config)

        return jsonify({'text': extracted_text.strip()})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

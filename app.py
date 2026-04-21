import os
import base64
import io
from flask import Flask, request, jsonify, send_from_directory
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes

# We specify 'static' as the folder where your index.html lives
app = Flask(__name__, static_folder='static')

@app.route('/')
def serve_index():
    # This tells Flask to look for index.html inside your /static folder
    return send_from_directory('static', 'index.html')

@app.route('/ocr', methods=['POST'])
def ocr_process():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No data provided'}), 400

        # Decode base64 data
        file_bytes = base64.b64decode(data['image'])
        is_pdf = data.get('is_pdf', False)
        lang = data.get('lang', 'aze')

        extracted_text = ""

        if is_pdf:
            # Convert PDF pages to images (processing first 5 pages for stability)
            try:
                images = convert_from_bytes(file_bytes, first_page=1, last_page=5)
                for i, img in enumerate(images):
                    page_text = pytesseract.image_to_string(img, lang=lang)
                    extracted_text += f"--- Page {i+1} ---\n{page_text}\n\n"
            except Exception as pdf_err:
                return jsonify({'error': f'PDF processing failed: {str(pdf_err)}'}), 500
        else:
            # Handle standard image
            image = Image.open(io.BytesIO(file_bytes))
            extracted_text = pytesseract.image_to_string(image, lang=lang)

        return jsonify({'text': extracted_text.strip()})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Using the port Render provides, or defaulting to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

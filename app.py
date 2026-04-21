from flask import Flask, request, Response, send_from_directory
import json
import base64
import tempfile
import os
import subprocess
from pathlib import Path

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/ocr', methods=['POST'])
def ocr():
    body = request.get_json()
    file_data = base64.b64decode(body['image'])
    lang = body.get('lang', 'aze')
    is_pdf = body.get('is_pdf', False)

    def generate():
        all_text = []

        if is_pdf:
            try:
                from pdf2image import convert_from_bytes
                yield f"data: {json.dumps({'type': 'status', 'message': 'Converting PDF to images...'})}\n\n"
                pages = convert_from_bytes(file_data, dpi=200)
                total = len(pages)
                yield f"data: {json.dumps({'type': 'total', 'total': total})}\n\n"

                for i, page in enumerate(pages):
                    yield f"data: {json.dumps({'type': 'progress', 'page': i+1, 'total': total})}\n\n"
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                        page.save(f.name, 'PNG')
                        tmp_path = f.name
                    out_path = tmp_path + '_out'
                    try:
                        subprocess.run(['tesseract', tmp_path, out_path, '-l', lang],
                                       capture_output=True, text=True)
                        txt_file = Path(out_path + '.txt')
                        if txt_file.exists():
                            text = txt_file.read_text().strip()
                            if text:
                                all_text.append(f"--- Page {i+1} ---\n{text}")
                    finally:
                        try: os.unlink(tmp_path)
                        except: pass
                        try: os.unlink(out_path + '.txt')
                        except: pass
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                return
        else:
            yield f"data: {json.dumps({'type': 'status', 'message': 'Reading image...'})}\n\n"
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                f.write(file_data)
                tmp_path = f.name
            out_path = tmp_path + '_out'
            try:
                subprocess.run(['tesseract', tmp_path, out_path, '-l', lang],
                               capture_output=True, text=True)
                txt_file = Path(out_path + '.txt')
                if txt_file.exists():
                    all_text.append(txt_file.read_text().strip())
            finally:
                try: os.unlink(tmp_path)
                except: pass
                try: os.unlink(out_path + '.txt')
                except: pass

        yield f"data: {json.dumps({'type': 'done', 'text': chr(10).join(all_text)})}\n\n"

    return Response(generate(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

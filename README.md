# TextLens OCR

Azerbaijani OCR web app powered by Tesseract. Upload an image or PDF and extract text in Azerbaijani or English.

## Deploy to Render

1. Fork or push this repo to GitHub
2. Go to [render.com](https://render.com) and create a free account
3. Click **New** → **Web Service**
4. Connect your GitHub repo
5. Render will detect `render.yaml` and configure everything automatically
6. Click **Deploy** — done

The build installs Tesseract and the Azerbaijani language pack automatically.

## Local development

```bash
pip install -r requirements.txt
apt-get install tesseract-ocr tesseract-ocr-aze poppler-utils
python app.py
```

# Use a lightweight Python image
FROM python:3.10-slim

# Install system dependencies for OCR and PDF processing
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-aze \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
# This will copy the 'static' folder and 'app.py' into the container
COPY . .

# Render will pass the PORT environment variable
ENV PORT=5000

# Start the application using gunicorn for better performance
CMD gunicorn --bind 0.0.0.0:$PORT app:app

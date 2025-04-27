from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import os
import uuid
import socket
import json
import logging
import sys

# === Embedded Logger Setup ===
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def log_event(service_name, message):
    log = {
        "service": service_name,
        "host": socket.gethostname(),
        "message": message
    }
    logger.info(json.dumps(log))

# === Flask app ===
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

PREDICTION_SERVICE_URL = os.environ.get('PREDICTION_SERVICE_URL', 'http://127.0.0.1:5001')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    
    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    log_event("web-service", f"Image saved for prediction: {filepath}")
    
    try:
        with open(filepath, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{PREDICTION_SERVICE_URL}/predict", files=files)
        
        if response.status_code == 200:
            result_data = response.json()
            prediction = result_data['prediction']
            severity_map = {
                0: "No DR",
                1: "Mild DR",
                2: "Moderate DR",
                3: "Severe DR",
                4: "Proliferative DR"
            }
            result_text = severity_map.get(prediction['class'], "Unknown")
            confidence = round(prediction['confidence'] * 100, 2)
            show_clinics = prediction['class'] > 0

            log_event("web-service", f"Prediction: {result_text} with {confidence}% confidence")
            
            rendered = render_template('index.html', 
                                       result=result_text,
                                       confidence=confidence,
                                       image_path=f"/static/uploads/{filename}",
                                       disease=show_clinics)

            # Schedule file deletion after render
            #os.remove(filepath)
            #log_event("web-service", f"Deleted uploaded file: {filepath}")
            return rendered

        else:
            log_event("web-service", f"Prediction service error: {response.status_code}")
            return render_template('index.html', error="Prediction service error")
    
    except Exception as e:
        log_event("web-service", f"Frontend error: {str(e)}")
        return render_template('index.html', error=f"Error: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

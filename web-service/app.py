import os
import uuid
import socket
import json
import logging
from flask import Flask, render_template, request, jsonify
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def setup_logger():
    log_dir = '/var/log/app'
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger('web-service')
    logger.setLevel(logging.INFO)
    logger.handlers = []

    file_handler = logging.FileHandler(f'{log_dir}/web-service.log', mode='a')
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_record = {
                "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
                "service": "web-service",
                "level": record.levelname.lower(),
                "message": record.getMessage(),
                "host": socket.gethostname()
            }
            return json.dumps(log_record)

    formatter = JSONFormatter()
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("Logger configured successfully")
    return logger

logger = setup_logger()

PREDICTION_SERVICE_URL = os.environ.get('PREDICTION_SERVICE_URL', 'http://prediction-service:5001')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    logger.info("Accessed index page")
    return render_template('index.html')

@app.route('/health')
def health():
    logger.info("Health check requested")
    return jsonify(status='ok'), 200

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        logger.warning("No file uploaded")
        return render_template('index.html', error="No file uploaded")

    file = request.files['file']
    if file.filename == '':
        logger.warning("No file selected")
        return render_template('index.html', error="No file selected")

    if not allowed_file(file.filename):
        logger.warning(f"Invalid file type: {file.filename}")
        return render_template('index.html', error="Invalid file type (.jpg, .jpeg, .png only)")

    try:
        filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        logger.info(f"Saved uploaded image: {filename}")

        with open(filepath, 'rb') as f:
            response = requests.post(
                f"{PREDICTION_SERVICE_URL}/predict",
                files={'file': f},
                timeout=10
            )

        if response.status_code == 200:
            result_data = response.json()
            prediction = result_data.get('prediction', {})

            severity_map = {
                0: "No DR",
                1: "Mild DR",
                2: "Moderate DR",
                3: "Severe DR",
                4: "Proliferative DR"
            }

            result_class = prediction.get('class', -1)
            confidence = round(prediction.get('confidence', 0.0) * 100, 2)
            result_text = severity_map.get(result_class, "Unknown")

            logger.info(
                f"Prediction successful - Result: {result_text}, Confidence: {confidence}%, File: {filename}"
            )

            return render_template(
                'index.html',
                result=result_text,
                confidence=confidence,
                image_path=f"/static/uploads/{filename}",
                disease=result_class > 0
            )

        else:
            error_msg = f"Prediction service error: {response.status_code} - {response.text}"
            logger.error(error_msg)
            return render_template('index.html', error="Prediction service error")

    except requests.exceptions.Timeout:
        logger.error("Prediction service timeout")
        return render_template('index.html', error="Prediction service timeout")

    except requests.exceptions.RequestException as e:
        logger.error(f"Prediction service connection error: {str(e)}")
        return render_template('index.html', error="Service unavailable")

    except Exception as e:
        logger.error(f"Unexpected error during prediction: {str(e)}", exc_info=True)
        return render_template('index.html', error="An unexpected error occurred")

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    logger.info("Starting web service")
    app.run(host='0.0.0.0', port=5000)

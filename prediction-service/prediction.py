import os
import socket
import json
import logging
import numpy as np
from flask import Flask, request, jsonify
from PIL import Image
import tensorflow as tf

# Initialize Flask app
app = Flask(__name__)

# Logger setup
def setup_logger():
    # Create logs directory if not exists
    log_dir = '/var/log/app'
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger('prediction-service')
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    logger.handlers = []
    
    # File handler for JSON logs
    file_handler = logging.FileHandler(f'{log_dir}/prediction-service.log', mode='a')
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # JSON formatter
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_record = {
                "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
                "service": "prediction-service",
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
    
    # Test the logger
    logger.info("Logger configured successfully")
    return logger

logger = setup_logger()

# Model loading
MODEL_PATH = 'retina_ensemble_model.h5'
model = None

def load_model():
    global model
    try:
        logger.info("Loading model...")
        model = tf.keras.models.load_model(MODEL_PATH)
        logger.info(f"Model loaded successfully from {MODEL_PATH}")
        logger.info(f"Model summary: {model.summary()}")
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}", exc_info=True)
        model = None

@app.route('/')
def home():
    logger.info("Root endpoint accessed")
    return jsonify({
        "status": "Prediction Service Running",
        "model_loaded": model is not None,
        "model_path": MODEL_PATH
    })

@app.route('/health')
def health():
    logger.info("Health check requested")
    health_status = {
        "status": "healthy",
        "model_loaded": model is not None,
        "service": "prediction-service"
    }
    return jsonify(health_status), 200

@app.route('/predict', methods=['POST'])
def predict():
    global model
    if model is None:
        logger.warning("Model not loaded - attempting to load")
        load_model()
    if model is None:
        logger.error("Model still not loaded after attempt")
        return jsonify({'error': 'Model not loaded'}), 500

    if 'file' not in request.files:
        logger.warning("No file provided in request")
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        logger.warning("Empty filename provided")
        return jsonify({'error': 'Empty filename'}), 400

    try:
        logger.info(f"Processing file: {file.filename}")
        
        # Process image
        image = Image.open(file.stream).convert("RGB")
        image = image.resize((224, 224))
        image_array = np.array(image) / 255.0
        image_array = np.expand_dims(image_array, axis=0)
        logger.debug("Image processed successfully")

        # Make prediction
        logger.info("Making prediction...")
        predictions = model.predict(image_array)
        pred_class = int(np.argmax(predictions[0]))
        confidence = float(predictions[0][pred_class])
        logger.debug(f"Raw prediction output: {predictions}")

        severity_map = {
            0: "No DR",
            1: "Mild DR",
            2: "Moderate DR",
            3: "Severe DR",
            4: "Proliferative DR"
        }

        result = {
            "prediction": {
                "class": pred_class,
                "severity": severity_map.get(pred_class, "Unknown"),
                "confidence": round(confidence, 4),
                "model": MODEL_PATH
            }
        }

        logger.info(
            f"Prediction successful - Class: {pred_class} ({severity_map.get(pred_class, 'Unknown')}), "
            f"Confidence: {confidence:.2%}, "
            f"File: {file.filename}"
        )
        return jsonify(result)
        
    except IOError as e:
        logger.error(f"Image processing error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Invalid image file'}), 400
        
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Prediction failed',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    # Load model before starting service
    load_model()
    
    if model is None:
        logger.critical("Failed to load model - service may not function properly")
    
    logger.info(f"Starting prediction service on port 5001")
    try:
        app.run(host='0.0.0.0', port=5001)
    except Exception as e:
        logger.critical(f"Service failed to start: {str(e)}", exc_info=True)
        raise
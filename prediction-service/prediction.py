from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
from PIL import Image
import os
import socket
import json
import logging
import sys

# === Embedded Logger Setup ===
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(message)s')  # raw JSON format
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
MODEL_PATH = 'retina_ensemble_model.h5'
model = None

def load_model():
    global model
    log_event("prediction-service", "Loading retinopathy model...")
    model = tf.keras.models.load_model(MODEL_PATH)
    log_event("prediction-service", "Model loaded successfully")

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Prediction Service Running", 
                   "message": "Use /predict endpoint for retinopathy detection"})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

@app.route('/predict', methods=['POST'])
def predict():
    global model
    if model is None:
        load_model()
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        log_event("prediction-service", f"Received image: {file.filename}")
        img = Image.open(file.stream)
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        if len(img_array.shape) == 3:
            img_array = np.expand_dims(img_array, axis=0)
        
        predictions = model.predict(img_array)
        prediction_class = int(np.argmax(predictions, axis=1)[0])
        confidence = float(predictions[0][prediction_class])
        
        severity_map = {
            0: "No DR",
            1: "Mild DR",
            2: "Moderate DR",
            3: "Severe DR",
            4: "Proliferative DR"
        }
        
        result = {
            'prediction': {
                'class': prediction_class,
                'severity': severity_map.get(prediction_class, "Unknown"),
                'confidence': confidence
            }
        }

        log_event("prediction-service", f"Prediction result: {result}")
        return jsonify(result)
    
    except Exception as e:
        log_event("prediction-service", f"Error during prediction: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    load_model()
    app.run(host='0.0.0.0', port=5001, debug=True)

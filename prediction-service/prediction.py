from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
from PIL import Image
import os

app = Flask(__name__)
MODEL_PATH = 'retina_ensemble_model.h5'
model = None

# Load the model at startup
def load_model():
    global model
    print("Loading retinopathy model...")
    model = tf.keras.models.load_model(MODEL_PATH)
    print("Model loaded successfully")

# Add a root route for health checks
@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Prediction Service Running", 
                   "message": "Use /predict endpoint for retinopathy detection"})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

@app.route('/predict', methods=['POST'])
def predict():
    # Initialize model if not already loaded
    global model
    if model is None:
        load_model()
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        # Process the image
        img = Image.open(file.stream)
        img = img.resize((224, 224))  # Adjust size according to your model's requirements
        img_array = np.array(img) / 255.0
        
        # Add batch dimension if needed
        if len(img_array.shape) == 3:
            img_array = np.expand_dims(img_array, axis=0)
        
        # Make prediction
        predictions = model.predict(img_array)
        
        # Process prediction results
        prediction_class = np.argmax(predictions, axis=1)[0]
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
                'class': int(prediction_class),
                'severity': severity_map.get(prediction_class, "Unknown"),
                'confidence': confidence
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Load model at startup
    load_model()
    app.run(host='0.0.0.0', port=5001, debug=True)

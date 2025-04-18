from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import os
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Get backend URL from environment or use default for local testing
PREDICTION_SERVICE_URL = os.environ.get('PREDICTION_SERVICE_URL', 'http://prediction-service:5001')

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
    
    # Generate unique filename
    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Send file to prediction service
    try:
        files = {'file': open(filepath, 'rb')}
        response = requests.post(f"{PREDICTION_SERVICE_URL}/predict", files=files)
        
        if response.status_code == 200:
            result_data = response.json()
            prediction = result_data['prediction']
            
            # Map the prediction class to a text result
            severity_map = {
                0: "No DR",
                1: "Mild DR",
                2: "Moderate DR",
                3: "Severe DR",
                4: "Proliferative DR"
            }
            
            result_text = severity_map.get(prediction['class'], "Unknown")
            confidence = round(prediction['confidence'] * 100, 2)
            
            # Set disease flag for clinic locator if DR is detected
            show_clinics = prediction['class'] > 0
            
            return render_template('index.html', 
                                  result=result_text,
                                  confidence=confidence,
                                  image_path=f"/static/uploads/{filename}",
                                  disease=show_clinics)
        else:
            return render_template('index.html', error="Prediction service error")
    except Exception as e:
        return render_template('index.html', error=f"Error: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
import os
import pandas as pd

# Create Flask app
app = Flask(__name__)

# Create Blueprint
dpmodel_bp = Blueprint('dpmodel', __name__)

# Configure CORS for the entire app
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

# Add CORS headers to blueprint responses
@dpmodel_bp.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

EXPECTED_FEATURES = [
    'gender', 'age', 'currentSmoker', 'cigsPerDay', 'BPMeds',
    'prevalentStroke', 'prevalentHyp', 'diabetes', 'sysBP',
    'diaBP', 'BMI', 'BP_ratio', 'hypertension', 'BMI_category',
    'smokingCategory', 'diabetes_smoker_interaction', 'stroke_hypertension_interaction'
]

# Load the model
try:
    model_path = os.path.join(os.getcwd(), 'aimodels/DP/dp_model.h5')
    dp_model = tf.keras.models.load_model(model_path)
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model: {str(e)}")
    raise RuntimeError("Model failed to load")

def calculate_bmi_category(bmi):
    if bmi < 18.5:
        return 0  # Underweight
    elif bmi < 25:
        return 1  # Normal
    elif bmi < 30:
        return 2  # Overweight
    else:
        return 3  # Obese

def get_risk_level(risk_percentage):
    if risk_percentage < 30:
        return 'Low'
    elif risk_percentage < 60:
        return 'Moderate'
    else:
        return 'High'

@dpmodel_bp.route('/predictData', methods=['POST', 'OPTIONS'])
def predict_health_risk():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    try:
        request_data = request.get_json()
        
        if not request_data or 'data' not in request_data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        input_data = request_data['data'][0]

        # Process the input data
        processed_data = {
            'gender': int(float(input_data.get('gender', 0))),
            'age': int(float(input_data.get('age', 0))),
            'currentSmoker': int(float(input_data.get('currentSmoker', 0))),
            'cigsPerDay': float(input_data.get('cigsPerDay', 0.0)),
            'BPMeds': int(float(input_data.get('BPMeds', 0))),
            'prevalentStroke': int(float(input_data.get('prevalentStroke', 0))),
            'prevalentHyp': int(float(input_data.get('prevalentHyp', 0))),
            'diabetes': int(float(input_data.get('diabetes', 0))),
            'sysBP': float(input_data.get('sysBP', 0.0)),
            'diaBP': float(input_data.get('diaBP', 0.0)),
            'BMI': float(input_data.get('BMI', 0.0)),
        }

        # Calculate derived features
        processed_data['BP_ratio'] = processed_data['sysBP'] / processed_data['diaBP'] if processed_data['diaBP'] != 0 else 0.0
        processed_data['hypertension'] = 1 if (processed_data['sysBP'] >= 140 or processed_data['diaBP'] >= 90) else 0
        processed_data['BMI_category'] = calculate_bmi_category(processed_data['BMI'])

        # Smoking category
        if processed_data['currentSmoker']:
            if processed_data['cigsPerDay'] <= 10:
                processed_data['smokingCategory'] = 1
            elif processed_data['cigsPerDay'] <= 20:
                processed_data['smokingCategory'] = 2
            else:
                processed_data['smokingCategory'] = 3
        else:
            processed_data['smokingCategory'] = 0

        # Interaction features
        processed_data['diabetes_smoker_interaction'] = processed_data['diabetes'] * processed_data['currentSmoker']
        processed_data['stroke_hypertension_interaction'] = processed_data['prevalentStroke'] * processed_data['hypertension']

        # Create DataFrame for model input
        input_df = pd.DataFrame([{feature: processed_data.get(feature, 0) for feature in EXPECTED_FEATURES}])

        # Get prediction from the model
        prediction = dp_model.predict(input_df)
        risk_score = float(prediction[0][0])
        risk_percentage = min(max(risk_score * 100, 0), 100)
        risk_level = get_risk_level(risk_percentage)

        response = jsonify({
            'success': True,
            'result': {
                'riskScore': round(risk_percentage, 1),
                'riskLevel': risk_level,
                'confidence': round(risk_percentage/100, 2)
            },
            'processedData': processed_data
        })
        
        return response

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        error_response = jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        })
        return error_response, 500

# Register blueprint
app.register_blueprint(dpmodel_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
from flask import Blueprint, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import os
import pandas as pd

dpmodel_bp = Blueprint('dpmodel', __name__)

# Configure CORS for the blueprint
CORS(dpmodel_bp, resources={
    r"/predictData": {
        "origins": ["http://localhost:3000"],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

# Keep all 18 features for the model
EXPECTED_FEATURES = [
    'gender', 'age', 'currentSmoker', 'cigsPerDay', 'BPMeds',
    'prevalentStroke', 'prevalentHyp', 'diabetes', 'sysBP',
    'diaBP', 'BMI', 'heartRate', 'BP_ratio', 'hypertension',
    'smokingCategory', 'age_category', 'totChol', 'glucose'
]

# Load the model
try:
    model_path = os.path.join(os.getcwd(), 'aimodels/DP/dp_model.h5')
    dp_model = tf.keras.models.load_model(model_path)
    print("Model loaded successfully")
    print("Model input shape:", dp_model.input_shape)
    print("Model output shape:", dp_model.output_shape)
except Exception as e:
    print(f"Error loading model: {str(e)}")
    dp_model = None

@dpmodel_bp.route('/predictData', methods=['POST'])
def predict_health_risk():
    print("Received request")
    try:
        request_data = request.get_json()
        print("Request data:", request_data)
        
        if not request_data or 'data' not in request_data or not request_data['data']:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        input_data = request_data['data'][0]
        
        # Initial data processing with default values for hidden fields
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
            'heartRate': float(input_data.get('heartRate', 70.0)),
            # Add hidden fields with default values
            'totChol': 200.0,  # Average normal cholesterol level
            'glucose': 100.0   # Average normal glucose level
        }

        # Calculate derived features
        if processed_data['diaBP'] != 0:
            processed_data['BP_ratio'] = processed_data['sysBP'] / processed_data['diaBP']
        else:
            processed_data['BP_ratio'] = 0.0

        # Calculate hypertension
        processed_data['hypertension'] = 1 if (processed_data['sysBP'] >= 140 or processed_data['diaBP'] >= 90) else 0

        # Calculate smoking category
        if processed_data['currentSmoker']:
            if processed_data['cigsPerDay'] <= 10:
                processed_data['smokingCategory'] = 1
            elif processed_data['cigsPerDay'] <= 20:
                processed_data['smokingCategory'] = 2
            else:
                processed_data['smokingCategory'] = 3
        else:
            processed_data['smokingCategory'] = 0

        # Calculate age category
        processed_data['age_category'] = int(processed_data['age'] / 10)

        # Create DataFrame with all expected features including hidden ones
        input_df = pd.DataFrame([{feature: processed_data.get(feature, 0) for feature in EXPECTED_FEATURES}])
        print("Model input shape:", input_df.shape)
        print("Model input features:", list(input_df.columns))

        if dp_model is not None:
            prediction = dp_model.predict(input_df)
            risk_score = float(prediction[0][0])
        else:
            risk_score = 0.5

        # Determine risk level
        risk_level = 'High' if risk_score > 0.7 else 'Moderate' if risk_score > 0.3 else 'Low'

        # Calculate disease-specific risks
        heart_disease_risk = risk_score
        stroke_risk = risk_score * 0.8  # Example multiplier
        hypertension_risk = risk_score * 0.9  # Example multiplier

        return jsonify({
            'success': True,
            'result': {
                'riskScore': risk_score,
                'riskLevel': risk_level,
                'confidence': 0.85,
                'diseases': {
                    'heartDisease': heart_disease_risk,
                    'stroke': stroke_risk,
                    'hypertension': hypertension_risk
                }
            },
            'processedData': processed_data
        })

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500
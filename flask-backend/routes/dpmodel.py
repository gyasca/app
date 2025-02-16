from flask import Blueprint, request, jsonify
from extensions import db
from datetime import datetime
import tensorflow as tf
import numpy as np
import os
import pandas as pd
import logging
from flask_cors import cross_origin

# Create Blueprint
dpmodel_bp = Blueprint('dpmodel', __name__)

# Define the HealthPrediction model
class HealthPrediction(db.Model):
    __tablename__ = 'health_predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    gender = db.Column(db.Integer)
    age = db.Column(db.Integer)
    current_smoker = db.Column(db.Integer)
    cigs_per_day = db.Column(db.Float)
    bp_meds = db.Column(db.Integer)
    prevalent_stroke = db.Column(db.Integer)
    prevalent_hyp = db.Column(db.Integer)
    diabetes = db.Column(db.Integer)
    sys_bp = db.Column(db.Float)
    dia_bp = db.Column(db.Float)
    bmi = db.Column(db.Float)
    risk_score = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    confidence = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    
@dpmodel_bp.route('/history/<int:user_id>', methods=['GET'])
def get_prediction_history(user_id):
    try:
        predictions = HealthPrediction.query.filter_by(user_id=user_id).order_by(HealthPrediction.created_at.desc()).all()
        return jsonify({
            'success': True,
            'predictions': [{
                'id': p.id,
                'risk_score': p.risk_score,
                'risk_level': p.risk_level,
                'created_at': p.created_at.isoformat(),
                'age': p.age,
                'gender': p.gender,
                'current_smoker': p.current_smoker,
                'cigs_per_day': p.cigs_per_day,
                'bp_meds': p.bp_meds,
                'prevalent_stroke': p.prevalent_stroke,
                'prevalent_hyp': p.prevalent_hyp,
                'diabetes': p.diabetes,
                'sys_bp': p.sys_bp,
                'dia_bp': p.dia_bp,
                'bmi': p.bmi
            } for p in predictions]
        })
    except Exception as e:
        logging.error(f"Error fetching prediction history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dpmodel_bp.route('/predictData', methods=['POST','OPTIONS'])
@cross_origin(origins=['http://localhost:3000'])
def predict_health_risk():

    try:
        print("Received request method:", request.method)  # Debug log
        print("Received headers:", dict(request.headers))  # Debug log
        
        request_data = request.get_json()
        print("Received data:", request_data)  # Debug log
        
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

        print("Processed data:", processed_data)  # Debug log

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

        # Save prediction to database
        prediction_record = HealthPrediction(
            gender=processed_data['gender'],
            age=processed_data['age'],
            current_smoker=processed_data['currentSmoker'],
            cigs_per_day=processed_data['cigsPerDay'],
            bp_meds=processed_data['BPMeds'],
            prevalent_stroke=processed_data['prevalentStroke'],
            prevalent_hyp=processed_data['prevalentHyp'],
            diabetes=processed_data['diabetes'],
            sys_bp=processed_data['sysBP'],
            dia_bp=processed_data['diaBP'],
            bmi=processed_data['BMI'],
            risk_score=risk_percentage,
            risk_level=risk_level,
            confidence=round(risk_percentage/100,2)
        )
        
        try:
            db.session.add(prediction_record)
            db.session.commit()
            prediction_id = prediction_record.id
        except Exception as db_error:
            db.session.rollback()
            logging.error(f"Database error: {str(db_error)}")
            prediction_id = None

        response = jsonify({
            'success': True,
            'result': {
                'riskScore': round(risk_percentage, 1),
                'riskLevel': risk_level,
                'confidence': round(risk_percentage/100, 2)
            },
            'processedData': processed_data,
            'recordId': prediction_id
        })
        
        return jsonify({
            'success': True,
            'result': {
                'riskScore': round(risk_percentage, 1),
                'riskLevel': risk_level,
                'confidence': round(risk_percentage/100, 2)
            },
            'processedData': processed_data,
            'recordId': prediction_id
        })
       

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        error_response = jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        })
        error_response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        return error_response, 500
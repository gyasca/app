# Gregory Achilles Chua 220502T

from flask import Blueprint, request, jsonify
from ultralytics import YOLO
from io import BytesIO
from PIL import Image
import os
from datetime import datetime
from extensions import db
from models.oral_analysis_history import OralAnalysisHistory


# Define the Blueprint
history_bp = Blueprint('history', __name__)

@history_bp.route('/oha/save-results', methods=['POST'])
def save_results():
    data = request.json  # Expecting JSON data with the prediction details
    user_id = data['user_id']
    original_image_path = data['original_image_path']
    condition_count = data['condition_count']
    predictions = data['predictions']  # This is already a JSON list

    try:
        # Create a new entry with the full JSON predictions
        oral_history = OralAnalysisHistory(
            user_id=user_id,
            original_image_path=original_image_path,
            condition_count=condition_count,
            predictions=predictions  # Store full predictions JSON here
        )
        
        db.session.add(oral_history)
        db.session.commit()

        return jsonify({'message': 'Results saved successfully'}), 200

    except Exception as e:
        print(f"Error saving history: {str(e)}")
        return jsonify({'error': str(e)}), 500


from flask import Blueprint, request, jsonify
from ultralytics import YOLO
from io import BytesIO
from PIL import Image
import os

# Define the Blueprint
ohamodel_bp = Blueprint('ohamodel', __name__)

# Load YOLOv8 model (Replace with your model path if needed)
model_path = os.path.join(os.getcwd(), 'aimodels/oha/best.pt')
model = YOLO(model_path)

@ohamodel_bp.route('/predict', methods=['POST'])
def predict():
    # Check if an image is included in the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        print(f"Received file: {file.filename}")  # Debugging line
        # Convert the image to the format YOLOv8 expects
        img = Image.open(file.stream)
        
        # Run inference on the image using YOLOv8
        results = model(img)  # Run inference on the image
        print(f"Results: {results}")  # Debugging line
        
        # Extract predictions from the results
        predictions = []
        for result in results:
            # Access bounding boxes and labels (assuming results is a list)
            for box in result.boxes:
                # Convert the box object into a list or array format
                box_values = box.xywh[0].cpu().numpy()  # Accessing box as tensor and converting to NumPy array
                prediction = {
                    'class': int(box.cls.cpu().item()),  # Ensure class is an integer
                    'confidence': float(box.conf.cpu().item()),  # Ensure confidence is a float
                    'x_center': float(box_values[0]),  # Extract the x-center
                    'y_center': float(box_values[1]),  # Extract the y-center
                    'width': float(box_values[2]),  # Extract the width
                    'height': float(box_values[3]),  # Extract the height
                }
                predictions.append(prediction)

        # Return the predictions in a JSON format
        return jsonify({'predictions': predictions})

    except Exception as e:
        print(f"Error: {e}")  # Debugging line
        return jsonify({'error': str(e)}), 500

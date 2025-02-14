from flask import Flask, request, jsonify, Blueprint, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import numpy as np
from PIL import Image, ImageDraw
import os
import tensorflow as tf
import json

# Define the Blueprint
foodmodel_bp = Blueprint('foodmodel', __name__)

# Load the pre-trained model
model_path = os.path.join(os.getcwd(), 'aimodels/food/food_classifier_model.keras')
model = tf.keras.models.load_model(model_path)

ingredients_model_path = os.path.join(os.getcwd(), 'aimodels/food/ingredient_detection_best.pt')
ingredients_model = YOLO(ingredients_model_path)

# Ensure uploads directory exists
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Utility function to check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@foodmodel_bp.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Endpoint to handle image upload and prediction
@foodmodel_bp.route('/identify-food', methods=['POST'])
def detect_food():
    # Check if uploads directory exists
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    if 'image' not in request.files:
        return jsonify({"error": "No image part"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        try:
            file.save(filepath)  # Save the uploaded file
            food_data = process_image(filepath)  # Process the image

            if "error" in food_data:
                return jsonify({"error": food_data["error"]}), 500

            return jsonify({
                "name": food_data['name'],
                "ingredients": food_data['ingredients'],  # Include detected ingredients
                "image": f"/uploads/{filename}"  # Relative path
            })

        except Exception as e:
            return jsonify({"error": f"Error processing the image: {str(e)}"}), 500
    else:
        return jsonify({"error": "Invalid file type"}), 400

# Image processing and prediction function
def process_image(filepath):
    # Open image using PIL
    img = Image.open(filepath)

    # Preprocess image for model input (assuming the model expects 224x224 images)
    # Resize image to match input size of the model
    img = img.resize((128, 128))
    img_array = np.array(img) / 255.0  # Normalize the image

    # Expand dimensions to match the model input shape (batch_size, height, width, channels)
    img_array = np.expand_dims(img_array, axis=0)

    # Get prediction from the model
    predictions = model.predict(img_array)

    # Get prediction from the YOLO ingredients detection model
    try:
        ingredients = predict_ingredients(filepath)
        ingredients = parse_ingredients_json(ingredients)

        print(ingredients)

    except Exception as e:
        return {"error": f"Error during ingredients prediction: {str(e)}"}
    
    # Map prediction to food label
    food_name = map_prediction_to_data(predictions)

    return {
        "name": food_name,
        "ingredients": ingredients
    }

# Map model prediction to food name and macronutrient data (dummy data)
def map_prediction_to_data(predictions):

    # Get the index of the highest probability
    predicted_class_index = np.argmax(predictions)

    food_labels = [
        "Chicken Rice",  # Index 0
        "Char Kway Teow",  # Index 1
        "Nasi Lemak",  # Index 2
        # Add all your class names here
    ]

    food_name = food_labels[predicted_class_index]

    return food_name

def parse_ingredients_json(json_data):
    if isinstance(json_data, str):
        json_data = json.loads(json_data)

    ingredient_count = {}

    for ingredient in json_data:
        if ingredient['name'] in ingredient_count:
            ingredient_count[ingredient['name']] += 1
        else:
            ingredient_count[ingredient['name']] = 1
        
    return ingredient_count

def predict_ingredients(filepath):
    results = ingredients_model.predict(
    source=filepath,
    conf=0.5,
    device="cpu"
    )

    return results[0].to_json()

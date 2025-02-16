from flask import Blueprint, request, jsonify
from io import BytesIO
import os
import pandas as pd


print("Model Path:", os.path.exists('/Users/charmchua/Desktop/Y3S2/AAP/app/flask-backend/aimodels/DP/dp_model.keras'))



# Define the Blueprint
dpmodel_bp = Blueprint('dpmodel', __name__)






import tensorflow as tf
import keras.utils as image #load image only from file

from PIL import Image
import io    

import numpy as np


# Load the DP model
model_path = os.path.join(os.getcwd(), 'aimodels/DP/dp_model.h5')
dp_model = tf.keras.models.load_model(model_path)

@dpmodel_bp.route("/predictData", methods=["POST"])
def predictData():
    try:
        # Parse the incoming JSON payload
        input_data = request.json.get("data")
        if not input_data:
            return jsonify({"error": "No input data provided"}), 400

        # Convert input data to a Pandas DataFrame
        df = pd.DataFrame(input_data)

        # Preprocess the data (if necessary)
        # Example: Normalize or scale features if required by your model
        preprocessed_data = df.to_numpy()  # Convert to NumPy array for TensorFlow model input

        # Ensure the data shape matches the model's expected input shape
        if len(preprocessed_data.shape) == 1:
            preprocessed_data = np.expand_dims(preprocessed_data, axis=0)  # Add batch dimension

        # Make predictions
        predictions = dp_model.predict(preprocessed_data)

        # Format the predictions
        result = [
            {"row": i, "predictions": prediction.tolist()}
            for i, prediction in enumerate(predictions)
        ]

        return jsonify({"result": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


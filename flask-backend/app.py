from flask import Flask, jsonify, request
from flask_cors import CORS
from extensions import db
from sqlalchemy import inspect
import logging
from config import Config
from flask import send_from_directory
import os
from nanoid import generate  # Import nanoid

app = Flask(__name__)

# Configurations
app.config.from_object(Config)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize extensions
db.init_app(app)
cors = CORS()
cors.init_app(app)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Import and register Blueprints
from routes.user import user_bp
app.register_blueprint(user_bp, url_prefix='/user')

from routes.ohamodel import ohamodel_bp
app.register_blueprint(ohamodel_bp, url_prefix='/ohamodel')

from routes.dpmodel import dpmodel_bp
app.register_blueprint(dpmodel_bp, url_prefix='/dpmodel')

# Import models here for Alembic
from models import *

# Function to dynamically check and create all tables
def create_all_tables():
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            if 'users' not in inspector.get_table_names():
                logging.info('Creating tables...')
                db.create_all()
            else:
                logging.info('Tables already exist.')
        except Exception as e:
            logging.error(f"Error during table creation: {e}")

# Call the function to check and create tables
create_all_tables()

@app.route('/uploads/<filename>', methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "profilePhoto" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["profilePhoto"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Generate a unique ID for the file
    file_extension = os.path.splitext(file.filename)[1]  # Get the file extension
    unique_filename = f"{generate(size=10)}{file_extension}"  # Generate a 10-character unique ID

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
    file.save(file_path)

    # Construct the full URL dynamically
    file_url = f"{request.host_url}uploads/{unique_filename}"

    return jsonify({"filePath": file_url})


@app.route("/delete/<filename>", methods=["DELETE"])
def delete_file(filename):
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    try:
        os.remove(file_path)
        return jsonify({"message": "File deleted successfully"}), 200
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Start the application
if __name__ == '__main__':
    app.run(debug=True, port=3001)

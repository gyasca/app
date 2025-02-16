from flask import Flask, request, jsonify
from flask_cors import CORS
from extensions import db
from flask_jwt_extended import JWTManager
from sqlalchemy import inspect
import logging
from config import Config
from database.init_db import init_db
from routes.skin_analysis import skin_analysis_bp
from models.skin_analysis import SkinAnalysis
from migrations.create_skin_analyses import create_skin_analyses_table
from migrations.add_annotated_image import add_annotated_image_column



app = Flask(__name__)
cors = CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message')
    
    # Your chat logic here
    response = {
        'message': f"I received your message: {message}"
    }
    
    return jsonify(response)
# Configurations
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://aap:aap@localhost/aap'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.secret_key = 'supersecretkey'
app.config.from_object(Config)


# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)
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

from routes.dpmodel import dpmodel_bp
app.register_blueprint(dpmodel_bp, url_prefix='/dpmodel')

from routes.acnemodel import acnemodel_bp
app.register_blueprint(acnemodel_bp, url_prefix='/acnemodel')

app.register_blueprint(skin_analysis_bp, url_prefix='/skin-analysis')

# Import models here for Alembic
from models import *

# Function to dynamically check and create all tables
def create_all_tables():
    with app.app_context():
        try:
            # Get the list of existing tables in the database
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()

            # Get all models registered with SQLAlchemy
            mappers = db.Model.registry.mappers
            required_tables = [mapper.class_.__tablename__ for mapper in mappers]

            # Check if any required table is missing
            if not all(table in existing_tables for table in required_tables):
                logging.info('Creating missing tables...')
                logging.info(f'Expected tables: {required_tables}')
                logging.info(f'Existing tables: {existing_tables}')
                db.create_all()
            else:
                logging.info('All required tables exist.')
        except Exception as e:
            logging.error(f"Error during table creation: {e}")

# Call the function to check and create tables
create_all_tables()

# Start the application
if __name__ == '__main__':
    app.run(debug=True, port=3001)



# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# from config import Config

# # Initialize the app
# app = Flask(__name__)
# app.config.from_object(Config)

# # Initialize database and migrations
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)

# # Register blueprints
# from routes.auth import auth_bp
# app.register_blueprint(auth_bp, url_prefix='/auth')

# if __name__ == "__main__":
#     app.run(debug=True)
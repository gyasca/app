from flask import Flask
from flask_cors import CORS
from extensions import db
from sqlalchemy import inspect
import logging
from config import Config

app = Flask(__name__)

CORS(app, resources={
    r"/dpmodel/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
# Configure app
app.config.from_object(Config)
db.init_app(app)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Import and register Blueprints
from routes.user import user_bp
from routes.ohamodel import ohamodel_bp
from routes.dpmodel import dpmodel_bp

app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(ohamodel_bp, url_prefix='/ohamodel')
app.register_blueprint(dpmodel_bp, url_prefix='/dpmodel')

# Import models
from models import *

def create_all_tables():
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            mappers = db.Model.registry.mappers
            required_tables = [mapper.class_.__tablename__ for mapper in mappers]
            
            if not all(table in existing_tables for table in required_tables):
                logging.info('Creating missing tables...')
                db.create_all()
            else:
                logging.info('All required tables exist.')
        except Exception as e:
            logging.error(f"Error during table creation: {e}")
            raise

create_all_tables()

if __name__ == '__main__':
    app.run(debug=True, port=3001)
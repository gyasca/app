from flask import Flask
from flask_cors import CORS
from extensions import db
from sqlalchemy import inspect
import logging
from config import Config


app = Flask(__name__)


# Configurations
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://aap:aap@localhost/aap'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.secret_key = 'supersecretkey'
app.config.from_object(Config)


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
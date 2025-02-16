import os

class Config:
    # SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    SECRET_KEY = 'blahblah123'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://aap:aap@localhost/aap'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'blahblah123'  # Ensure you have a secret key
    JWT_TOKEN_LOCATION = "headers"  # Define where the JWT token is expected
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"
    JWT_ACCESS_TOKEN_EXPIRES = False  # Set expiration policy as needed
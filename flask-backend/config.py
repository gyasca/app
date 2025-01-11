import os

class Config:
    # SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    SECRET_KEY = 'blahblah123'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://aap:aap@localhost/aap'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
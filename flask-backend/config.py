import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://aap:aap@localhost/aap'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
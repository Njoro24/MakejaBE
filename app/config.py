import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'dev'  
    SQLALCHEMY_DATABASE_URI = 'postgresql://makeja_user:makeja_pass@localhost/makeja_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

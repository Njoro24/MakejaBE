from flask import Flask

print("=== APP/__init__.py LOADING ===")

from flask import Flask
from flask_cors import CORS
# ... other imports

def create_app(config_name=None):
    print("=== CREATE_APP FUNCTION CALLED ===")
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return {'message': 'Flask app is running'}, 200
    
    print("=== ROUTES REGISTERED ===")
    return app

print("=== APP/__init__.py LOADED ===")

def create_app(config_name=None):
    print("=== STARTING CREATE_APP ===")
    app = Flask(__name__)
    print("=== FLASK APP CREATED ===")
    
    @app.route('/')
    def home():
        print("=== HOME ROUTE CALLED ===")
        return {'message': 'Flask app is running'}, 200
    
    print("=== ROUTES REGISTERED ===")
    return app
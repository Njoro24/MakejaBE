from flask import Flask

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
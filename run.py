from app import create_app, db
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

# Create the Flask app using the factory function
app = create_app()

# Initialize extensions
migrate = Migrate(app, db)
jwt = JWTManager(app)

if __name__ == '__main__':
    app.run(debug=True)

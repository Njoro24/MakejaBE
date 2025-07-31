from app import create_app, db

def deploy():
    app = create_app()
    with app.app_context():
        print("Creating all tables...")
        db.create_all()
        print("Tables created!")

if __name__ == '__main__':
    deploy()
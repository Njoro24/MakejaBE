from app import create_app
from app.db import db
from app.models.user import User

app = create_app()

with app.app_context():
    user = User(
        first_name="Darwin",  
        last_name="Osteen",   
        email="darwin@example.com",  
        is_email_verified=True,
        is_verified=True,
        is_admin=True  
    )
    user.set_password("StrongPassword@123")  

    db.session.add(user)
    db.session.commit()
    print("Admin user created successfully.")

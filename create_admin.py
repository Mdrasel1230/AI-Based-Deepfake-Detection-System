from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_admin_user():
    with app.app_context():
        # Check if admin user already exists
        admin = User.query.filter_by(is_admin=True).first()
        
        if not admin:
            # Create admin user
            admin = User(
                username="admin",
                email="admin@example.com",
                password_hash=generate_password_hash("admin123"),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully.")
            print("Username: admin")
            print("Email: admin@example.com")
            print("Password: admin123")
        else:
            print("Admin user already exists.")
            print(f"Username: {admin.username}")
            print(f"Email: {admin.email}")

if __name__ == "__main__":
    create_admin_user()
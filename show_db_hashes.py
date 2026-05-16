from app import create_app
from models import User

app = create_app()

with app.app_context():
    users = User.query.all()
    print("\n" + "="*50)
    print("USER DATABASE: PASSWORD HASHES")
    print("="*50)
    
    if not users:
        print("No users found in the database. Please register a user first.")
    else:
        for user in users:
            print(f"Username : {user.username}")
            print(f"Role     : {user.role}")
            print(f"Hash     : {user.password_hash}")
            print("-" * 50)
    print("\n")

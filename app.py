import os
from flask import Flask, redirect, url_for
from dotenv import load_dotenv
from models import db, User, Movie
from auth import auth_bp, bcrypt
from movies import movies_bp
from bookings import bookings_bp
from admin import admin_bp
from security import configure_security_headers, csrf, limiter
from flask_login import LoginManager
from datetime import timedelta

load_dotenv()

def create_app():
    app = Flask(__name__)
    # Security: Environment Variables
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default-dev-secret-change-me')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///cinevault.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Security: Session Management Hardening
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    
    db.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    
    configure_security_headers(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    app.register_blueprint(auth_bp)
    app.register_blueprint(movies_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(admin_bp)
    
    with app.app_context():
        db.create_all()
        # Seed some movies if empty
        if not Movie.query.first():
            movies = [
                Movie(title="Inception", description="A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.", genre="Sci-Fi", year=2010),
                Movie(title="The Dark Knight", description="When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.", genre="Action", year=2008),
                Movie(title="Interstellar", description="A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.", genre="Sci-Fi", year=2014)
            ]
            db.session.bulk_save_objects(movies)
            db.session.commit()
            
    return app

if __name__ == '__main__':
    app = create_app()
    # Security: Run with HTTPS / TLS context
    cert_path = 'cert.pem'
    key_path = 'key.pem'
    if os.path.exists(cert_path) and os.path.exists(key_path):
        app.run(debug=True, ssl_context=(cert_path, key_path))
    else:
        print("Warning: SSL certificates not found. Running in HTTP mode.")
        print("Please run: openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes")
        app.run(debug=True)

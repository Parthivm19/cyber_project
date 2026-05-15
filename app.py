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
                Movie(title="Inception", description="A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.", genre="Sci-Fi", year=2010, image_url="https://image.tmdb.org/t/p/w500/8Z01I6E39E2sE1H2BqUvEksG3y0.jpg"),
                Movie(title="The Dark Knight", description="When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.", genre="Action", year=2008, image_url="https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg"),
                Movie(title="Interstellar", description="A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.", genre="Sci-Fi", year=2014, image_url="https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg"),
                Movie(title="The Matrix", description="A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.", genre="Sci-Fi", year=1999, image_url="https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg"),
                Movie(title="Pulp Fiction", description="The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.", genre="Crime", year=1994, image_url="https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPbOYKQmG_1.jpg"),
                Movie(title="Spider-Man: Across the Spider-Verse", description="Miles Morales catapults across the Multiverse, where he encounters a team of Spider-People charged with protecting its very existence.", genre="Animation", year=2023, image_url="https://image.tmdb.org/t/p/w500/8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg"),
                Movie(title="Oppenheimer", description="The story of American scientist, J. Robert Oppenheimer, and his role in the development of the atomic bomb.", genre="Drama", year=2023, image_url="https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg"),
                Movie(title="Dune: Part Two", description="Paul Atreides unites with Chani and the Fremen while on a warpath of revenge against the conspirators who destroyed his family.", genre="Sci-Fi", year=2024, image_url="https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2JGjjcNsV.jpg")
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

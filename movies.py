from flask import Blueprint, render_template, request, jsonify
from models import Movie
from markupsafe import escape
from gemini import get_movie_recommendation
from flask_login import login_required

movies_bp = Blueprint('movies', __name__)

@movies_bp.route('/')
def index():
    return render_template('base.html')

@movies_bp.route('/movies')
def list_movies():
    query = request.args.get('q', '')
    if query:
        # Security: Jinja escapes this in the template, but we can escape here too
        safe_query = escape(query)
        # Security: ORM prevents SQL Injection
        movies = Movie.query.filter(Movie.title.ilike(f'%{safe_query}%')).all()
    else:
        movies = Movie.query.all()
    return render_template('movies.html', movies=movies, search=query)

@movies_bp.route('/demo/sqli-safe')
def sqli_safe_demo():
    # Demonstrating safe query vs vulnerable
    query = request.args.get('username', 'admin')
    
    # Safe query via ORM
    from models import User
    user = User.query.filter_by(username=query).first()
    
    if user:
        return f"Found user safely: {escape(user.username)}. Using ORM prevented any SQL injection."
    return "User not found."

@movies_bp.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'POST':
        user_input = request.json.get('message', '')
        # Security: Sanitize user input before passing to AI
        safe_input = escape(user_input)
        
        movies = Movie.query.all()
        ai_response = get_movie_recommendation(safe_input, movies)
        
        return jsonify({'response': ai_response})
    return render_template('chatbot.html')

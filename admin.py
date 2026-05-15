from flask import Blueprint, render_template, abort, session, redirect, url_for, flash, request
from flask_login import login_required
from models import db, Movie, Booking, User
from forms import MovieForm
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Security: Role-Based Access Control (RBAC)
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    users_count = User.query.count()
    movies_count = Movie.query.count()
    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    movies = Movie.query.all()
    form = MovieForm()
    return render_template('admin/dashboard.html', users_count=users_count, movies_count=movies_count, bookings=bookings, movies=movies, form=form)

@admin_bp.route('/add_movie', methods=['POST'])
@login_required
@admin_required
def add_movie():
    form = MovieForm()
    if form.validate_on_submit():
        new_movie = Movie(
            title=form.title.data,
            description=form.description.data,
            genre=form.genre.data,
            year=form.year.data,
            image_url=form.image_url.data
        )
        db.session.add(new_movie)
        db.session.commit()
        flash('Movie added successfully!', 'success')
    else:
        flash('Failed to add movie. Check inputs.', 'danger')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/delete_movie/<int:movie_id>', methods=['POST'])
@login_required
@admin_required
def delete_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash(f'Movie {movie.title} deleted securely.', 'success')
    return redirect(url_for('admin.dashboard'))

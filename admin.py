from flask import Blueprint, render_template, abort, session
from flask_login import login_required
from models import Movie, Booking, User
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
    bookings = Booking.query.all()
    return render_template('admin/dashboard.html', users_count=users_count, movies_count=movies_count, bookings=bookings)

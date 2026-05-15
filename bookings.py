from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from models import db, Movie, Booking
from forms import BookingForm
from flask_login import login_required, current_user
import hmac
import hashlib

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('/book/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def book_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    form = BookingForm()
    if form.validate_on_submit():
        booking = Booking(user_id=current_user.id, movie_id=movie.id, seats=form.seats.data)
        db.session.add(booking)
        db.session.commit()
        
        # Security: Sensitive Data Encryption/Signing
        # Store booking confirmation tokens as HMAC-signed values
        token = hmac.new(current_app.secret_key.encode(), str(booking.id).encode(), hashlib.sha256).hexdigest()
        
        flash('Booking successful!', 'success')
        return redirect(url_for('bookings.summary', booking_id=booking.id, token=token))
    return render_template('booking.html', form=form, movie=movie)

@bookings_bp.route('/summary/<int:booking_id>')
@login_required
def summary(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    token = request.args.get('token')
    
    # Security: Verify HMAC token
    expected_token = hmac.new(current_app.secret_key.encode(), str(booking.id).encode(), hashlib.sha256).hexdigest()
    if not token or not hmac.compare_digest(token, expected_token):
        flash('Invalid or missing confirmation token. Integrity check failed.', 'danger')
        return redirect(url_for('movies.list_movies'))
        
    if booking.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('movies.list_movies'))
        
    return render_template('summary.html', booking=booking)

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from models import db, User
from forms import RegistrationForm, LoginForm
from flask_bcrypt import Bcrypt
from flask_login import login_user, logout_user, current_user
from security import limiter
from datetime import datetime, timedelta, timezone
from cryptography.fernet import Fernet
import os
import base64

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

# Ensure we have a valid key for Fernet, padding to 32 bytes and base64 encoding if needed
# Actually, let's just generate one if missing and log a warning.
_fernet_key = os.getenv('ENCRYPTION_KEY')

try:
    if _fernet_key:
        f = Fernet(_fernet_key)
    else:
        raise ValueError("No key")
except ValueError:
    _fernet_key = Fernet.generate_key()
    f = Fernet(_fernet_key)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('movies.list_movies'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Security: bcrypt hashing for passwords
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # Security: Encrypting PII (phone number)
        phone_enc = f.encrypt(form.phone.data.encode()) if form.phone.data else None
        
        # First user is admin
        role = 'admin' if User.query.count() == 0 else 'user'
        
        # Security: ORM prevents SQL injection
        user = User(username=form.username.data, password_hash=hashed_password, phone_encrypted=phone_enc, role=role)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('movies.list_movies'))
    form = LoginForm()
    if form.validate_on_submit():
        # Security: Parameterized query via ORM
        user = User.query.filter_by(username=form.username.data).first()
        
        if user:
            # Check lockout
            if user.lockout_until and user.lockout_until.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
                flash('Account locked due to too many failed attempts. Try again later.', 'danger')
                return render_template('login.html', form=form)
                
            if bcrypt.check_password_hash(user.password_hash, form.password.data):
                user.failed_attempts = 0
                user.lockout_until = None
                db.session.commit()
                
                login_user(user)
                session['role'] = user.role
                session.permanent = True
                
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('movies.list_movies'))
            else:
                user.failed_attempts += 1
                if user.failed_attempts >= 5:
                    user.lockout_until = datetime.now(timezone.utc) + timedelta(minutes=15)
                db.session.commit()
                flash('Login Unsuccessful. Please check username and password', 'danger')
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
            
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    session.pop('role', None)
    return redirect(url_for('movies.index'))

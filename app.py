import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

# Configuration
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

@login_manager.user_loader
def load_user(user_id):
    from models import Admin
    return Admin.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/introduction')
def introduction():
    return render_template('introduction.html')

@app.route('/visuals/<int:gallery_id>')
def visuals(gallery_id):
    return render_template('visuals.html', gallery_id=gallery_id)

@app.route('/rates')
def rates():
    return render_template('rates.html')

@app.route('/answers')
def answers():
    return render_template('answers.html')

@app.route('/wishlist')
def wishlist():
    return render_template('wishlist.html')

@app.route('/bookings', methods=['GET', 'POST'])
def bookings():
    if request.method == 'POST':
        from models import BookingRequest
        try:
            booking = BookingRequest(
                name=request.form['name'],
                email=request.form['email'],
                date=datetime.strptime(request.form['date'], '%Y-%m-%d'),
                duration=request.form['duration'],
                message=request.form['message']
            )
            db.session.add(booking)
            db.session.commit()
            flash('Your booking request has been submitted successfully.')
            return redirect(url_for('bookings'))
        except Exception as e:
            flash('There was an error processing your request.')
            return redirect(url_for('bookings'))
    return render_template('bookings.html')

@app.route('/tours')
def tours():
    return render_template('tours.html')

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        from models import Admin
        username = request.form.get('username')
        password = request.form.get('password')
        user = Admin.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        flash('Invalid username or password')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    from models import BookingRequest
    bookings = BookingRequest.query.order_by(BookingRequest.created_at.desc()).all()
    return render_template('admin/dashboard.html', bookings=bookings)

@app.route('/admin/bookings/<int:booking_id>/update', methods=['POST'])
@login_required
def update_booking_status(booking_id):
    from models import BookingRequest
    booking = BookingRequest.query.get_or_404(booking_id)
    new_status = request.form.get('status')
    if new_status in ['pending', 'approved', 'rejected']:
        booking.status = new_status
        db.session.commit()
        flash('Booking status updated successfully.')
    return redirect(url_for('admin_dashboard'))

with app.app_context():
    import models
    db.create_all()
    
    # Create admin user if it doesn't exist
    from models import Admin
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='admin')
        admin.set_password('admin123')  # Default password, should be changed
        db.session.add(admin)
        db.session.commit()

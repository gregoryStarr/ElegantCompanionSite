import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from flask_mail import Mail, Message

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
mail = Mail()

# Configuration
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

db.init_app(app)
mail.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

@login_manager.user_loader
def load_user(user_id):
    from models import Admin
    return Admin.query.get(int(user_id))

# Email functions
def send_booking_confirmation(booking):
    msg = Message(
        'Booking Request Received',
        recipients=[booking.email]
    )
    msg.body = f'''Dear {booking.name},

Thank you for your booking request. We have received your request for the following:

Date: {booking.date.strftime('%B %d, %Y')}
Duration: {booking.duration}

We will review your request and get back to you shortly.

Best regards,
Venus'''
    
    mail.send(msg)

def send_booking_status_update(booking):
    status_messages = {
        'approved': 'We are pleased to inform you that your booking request has been approved.',
        'rejected': 'We regret to inform you that we are unable to accommodate your booking request at this time.',
        'pending': 'Your booking request is currently under review.'
    }
    
    msg = Message(
        f'Booking Status Update - {booking.status.title()}',
        recipients=[booking.email]
    )
    msg.body = f'''Dear {booking.name},

{status_messages.get(booking.status, '')}

Booking Details:
Date: {booking.date.strftime('%B %d, %Y')}
Duration: {booking.duration}

Best regards,
Venus'''
    
    mail.send(msg)

def send_gallery_access_code(client):
    msg = Message(
        'Private Gallery Access Code',
        recipients=[client.email]
    )
    msg.body = f'''Dear Valued Client,

Your private gallery access code is: {client.access_code}

This code is unique to you and should not be shared with anyone.

Best regards,
Venus'''
    
    mail.send(msg)

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
            
            try:
                send_booking_confirmation(booking)
                flash('Your booking request has been submitted successfully. Please check your email for confirmation.')
            except Exception as e:
                flash('Your booking request has been submitted, but there was an error sending the confirmation email.')
            
            return redirect(url_for('bookings'))
        except Exception as e:
            flash('There was an error processing your request.')
            return redirect(url_for('bookings'))
    return render_template('bookings.html')

@app.route('/tours')
def tours():
    return render_template('tours.html')

# Private Gallery Routes
@app.route('/private-gallery/access', methods=['GET', 'POST'])
def private_gallery_access():
    if request.method == 'POST':
        from models import VerifiedClient
        email = request.form.get('email')
        access_code = request.form.get('access_code')
        
        client = VerifiedClient.query.filter_by(email=email, access_code=access_code).first()
        if client:
            client.last_access = datetime.utcnow()
            db.session.commit()
            session['private_gallery_access'] = True
            session['client_email'] = email
            return redirect(url_for('private_gallery'))
        flash('Invalid email or access code')
    return render_template('private_access.html')

@app.route('/private-gallery')
def private_gallery():
    if not session.get('private_gallery_access'):
        return redirect(url_for('private_gallery_access'))
    return render_template('private_gallery.html')

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
        old_status = booking.status
        booking.status = new_status
        db.session.commit()
        
        if old_status != new_status:
            try:
                send_booking_status_update(booking)
                flash('Booking status updated successfully and notification email sent.')
            except Exception as e:
                flash('Booking status updated successfully but there was an error sending the notification email.')
        else:
            flash('Booking status updated successfully.')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/verified-clients')
@login_required
def verified_clients():
    from models import VerifiedClient
    clients = VerifiedClient.query.order_by(VerifiedClient.created_at.desc()).all()
    return render_template('admin/verified_clients.html', clients=clients)

@app.route('/admin/verified-clients/add', methods=['POST'])
@login_required
def add_verified_client():
    from models import VerifiedClient
    import random
    import string
    
    email = request.form.get('email')
    if not email:
        flash('Email is required')
        return redirect(url_for('verified_clients'))
    
    existing_client = VerifiedClient.query.filter_by(email=email).first()
    if existing_client:
        flash('Client already exists')
        return redirect(url_for('verified_clients'))
    
    # Generate random access code
    access_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    client = VerifiedClient(email=email, access_code=access_code)
    
    try:
        db.session.add(client)
        db.session.commit()
        send_gallery_access_code(client)
        flash('Client added successfully and access code sent via email')
    except Exception as e:
        db.session.rollback()
        flash('Error adding client')
    
    return redirect(url_for('verified_clients'))

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

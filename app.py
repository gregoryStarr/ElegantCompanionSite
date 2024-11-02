import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

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

with app.app_context():
    import models
    db.create_all()

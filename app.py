from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plant_monitoring_system.db'
db = SQLAlchemy(app)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    soil_moisture = db.Column(db.Float, nullable=False)

app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'your_fallback_secret_key')

@app.route('/user/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                session['user'] = user.username
                return redirect(url_for('dashboard'))
            flash('Invalid username or password')
    except SQLAlchemyError as e:
        logger.error(f'SQLAlchemy error during login: {e}')
        flash('Database error during login.', 'error')
    except Exception as e:
        logger.error(f'Unexpected error during login: {e}')
        flash('An unexpected error occurred during login.', 'error')
    return render_template('login.html')

@app.route('/user/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/user/signup', methods=['GET', 'POST'])
def signup():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists.')
                return redirect(url_for('signup'))
            hashed_password = generate_password_hash(password, method='sha256')
            user = User(username=username, password_hash=hashed_password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
    except SQLAlchemyError as e:
        logger.error(f'SQLAlchemy error during signup: {e}')
        flash('Database error during sign up.', 'error')
    except Exception as e:
        logger.error(f'Unexpected error during sign up: {e}')
        flash('An error occurred during sign up.', 'error')
    return render_template('signup.html')

@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    try:
        if 'user' not in session:
            return redirect(url_for('login'))
        sensor_data_entries = SensorData.query.order_by(SensorData.recorded_at.desc()).all()
    except SQLAlchemyError as e:
        logger.error(f'Error fetching dashboard data from the database: {e}')
        flash('Database error.', 'error')
        sensor_data_entries = []
    except Exception as e:
        logger.error(f'Unexpected error while fetching dashboard data: {e}')
        flash('An error occurred while fetching dashboard data.', 'error')
        sensor_data_entries = []
    return render_template('dashboard.html', sensor_data=sensor_data_entries)

@app.route('/api/sensor_data', methods=['POST'])
def receive_sensor_data():
    try:
        data = request.json
        required_keys = ['temperature', 'humidity', 'soil_moisture']
        if not all(k in data for k in required_keys):
            return json.dumps({'success': False, 'error': 'Missing data'}), 400, {'ContentType': 'application/json'}
        sensor_data = SensorData(temperature=data['temperature'], humidity=data['humidity'], soil_moisture=data['soil_moisture'])
        db.session.add(sensor_data)
        db.session.commit()
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except SQLAlchemyError as e:
        logger.error(f'Database error updating sensor data: {e}')
        return json.dumps({'success': False, 'error': 'Database error updating sensor data'}), 500, {'ContentType': 'application/json'}
    except Exception as e:
        logger.error(f'Error updating sensor data: {e}')
        return json.dumps({'success': False, 'error': f'Error updating sensor data: {e}'}), 500, {'ContentType': 'application/json'}

if __name__ == '__main__':
    try:
        db.create_all()
    except Exception as e:
        logger.error(f'Error during database initialization: {e}')
    app.run(debug=True, port=5000)
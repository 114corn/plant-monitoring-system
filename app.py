from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, verify_password_hash
import os
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plant_monitoring_system.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

class PlantSensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    soil_moisture = db.Column(db.Float, nullable=False)

app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'your_fallback_secret_key')

@app.route('/user/login', methods=['GET', 'POST'])
def login_user():
    try:
        if request.method == 'POST':
            username_entered = request.form['username']
            password_entered = request.form['password']
            user = User.query.filter_by(username=username_entered).first()
            if user and verify_password_hash(user.password_hash, password_entered):
                session['user_name'] = user.username
                return redirect(url_for('dashboard_view'))
            flash('Invalid username or password')
    except Exception as e:
        flash(f'An unexpected error occurred during login: {e}', 'error')
    return render_template('login.html')

@app.route('/user/logout')
def logout_user():
    session.pop('user_name', None)
    return redirect(url_for('login_user'))

@app.route('/user/signup', methods=['GET', 'POST'])
def signup_user():
    try:
        if request.method == 'POST':
            new_username = request.form['username']
            new_password = request.form['password']
            existing_user = User.query.filter_by(username=new_username).first()
            if existing_user:
                flash('Username already exists.')
                return redirect(url_for('signup_user'))
            hashed_new_password = generate_password_hash(new_password, method='sha256')
            new_user = User(username=new_username, password_hash=hashed_new_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login_user'))
    except Exception as e:
        flash(f'An error occurred during sign up: {e}', 'error')
    return render_template('signup.html')

@app.route('/')
def index():
    try:
        if 'user_name' not in session:
            return redirect(url_for('login_user'))
    except Exception as e:
        flash(f'An unexpected error occurred: {e}', 'error')
    return render_template('index.html')

@app.route('/dashboard')
def dashboard_view():
    try:
        if 'user_name' not in session:
            return redirect(url_for('login_user'))
        sensor_records = PlantSensorData.query.order_by(PlantSensorData.timestamp.desc()).all()
    except Exception as e:
        flash(f'An error occurred while fetching dashboard data: {e}', 'error')
        sensor_records = []
    return render_template('dashboard.html', sensor_data=sensor_records)

@app.route('/api/sensor_data', methods=['POST'])
def post_sensor_data():
    try:
        received_data = request.json
        required_keys = ['temperature', 'humidity', 'soil_moisture']
        if not all(key in received_data for key in required_keys):
            return json.dumps({'success': False, 'error': 'Missing data'}), 400, {'ContentType': 'application/json'}
        new_sensor_data = PlantSensorData(temperature=received_data['temperature'], humidity=received_data['humidity'], soil_moisture=received_data['soil_moisture'])
        db.session.add(new_sensor_data)
        db.session.commit()
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except Exception as e:
        return json.dumps({'success': False, 'error': 'Error updating sensor data: {}'.format(e)}), 500, {'ContentType': 'application/json'}

if __name__ == '__main__':
    try:
        db.create_all()
    except Exception as e:
        print(f'Error during database initialization: {e}')
    app.run(debug=True, port=5000)
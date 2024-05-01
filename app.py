from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plant_monitoring.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    moisture = db.Column(db.Float, nullable=False)

app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                session['username'] = user.username
                return redirect(url_for('dashboard'))
            flash('Invalid username or password')
    except Exception as e:
        flash('An error occurred during login: {}'.format(e))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            if User.query.filter_by(username=username).first():
                flash('Username already exists.')
                return redirect(url_for('signup'))
            hashed_password = generate_password_hash(password, method='sha256')
            new_user = User(username=username, password_hash=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    except Exception as e:
        flash('An error occurred during signup: {}'.format(e))
    return render_template('signup.html')

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    try:
        if 'username' not in session:
            return redirect(url_for('login'))
        sensor_data = SensorData.query.order_by(SensorData.timestamp.desc()).all()
    except Exception as e:
        flash('An error occurred while fetching dashboard data: {}'.format(e))
        sensor_data = []
    return render_template('dashboard.html', sensor_data=sensor_data)

@app.route('/api/sensor_data', methods=['POST'])
def update_sensor_data():
    try:
        data = request.json
        if not all(k in data for k in ('temperature', 'humidity', 'moisture')):
            return json.dumps({'success':False, 'error':'Missing data'}), 400, {'ContentType':'application/json'}
        new_data = SensorData(temperature=data['temperature'], humidity=data['humidity'], moisture=data['moisture'])
        db.session.add(new_data)
        db.session.commit()
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
    except Exception as e:
        return json.dumps({'success':False, 'error':'Error updating sensor data: {}'.format(e)}), 500, {'ContentType':'application/json'}

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, port=5000)
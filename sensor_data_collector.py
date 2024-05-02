import time
import sqlite3
import os
import csv
from datetime import datetime
import RPi.GPIO as GPIO

SOIL_MOISTURE_PIN = int(os.getenv('SOIL_MOISTURE_PIN'))
TEMPERATURE_PIN = int(os.getenv('TEMPERATURE_PIN'))
LIGHT_SENSOR_PIN = int(os.getenv('LIGHT_SENSOR_PIN'))

DATABASE = 'sensor_data.db'
CSV_FILE = 'sensor_data.csv'

def init_sensors():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SOIL_MOISTURE_PIN, GPIO.IN)
    GPIO.setup(TEMPERATURE_PIN, GPIO.IN)
    GPIO.setup(LIGHT_SENSOR_PIN, GPIO.IN)

def read_sensor_data():
    try:
        soil_moisture = GPIO.input(SOIL_MOISTURE_PIN)
        temperature = read_temperature_sensor()
        light = GPIO.input(LIGHT_SENSOR_PIN)
        return (soil_moisture, temperature, light)
    except Exception as e:
        print(f"Error reading sensor data: {e}")
        return (None, None, None) # Return a tuple of Nones in case of error

def read_temperature_sensor():
    return 25

class DatabaseManager:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None

    def __enter__(self):
        try:
            self.conn = sqlite3.connect(self.db_file)
            return self.conn.cursor()
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.conn:
                self.conn.commit()
                self.conn.close()
        except Exception as e:
            print(f"Error closing database connection: {e}")

def init_database():
    try:
        with DatabaseManager(DATABASE) as cur:
            if cur is not None:
                cur.execute('''CREATE TABLE IF NOT EXISTS sensor_data
                            (timestamp TEXT, soil_moisture INTEGER, temperature INTEGER, light INTEGER)''')
            else:
                print("Failed to initialize database.")
    except Exception as e:
        print(f"Error initializing database: {e}")

def save_to_database(data):
    try:
        with DatabaseManager(DATABASE) as cur:
            if cur is not None:
                cur.execute('''INSERT INTO sensor_data (timestamp, soil_moisture, temperature, light)
                            VALUES (?, ?, ?, ?)''', (datetime.now(), data[0], data[1], data[2]))
            else:
                print("Failed to save data to database.")
    except Exception as e:
        print(f"Error saving data to database: {e}")

def save_to_csv(data):
    try:
        with open(CSV_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([datetime.now()] + list(data))
    except Exception as e:
        print(f"Error saving data to CSV: {e}")

def main():
    init_sensors()
    init_database()
    
    try:
        while True:
            data = read_sensor_data()
            if all(d is not None for d in data):
                save_to_database(data)
                save_to_csv(data)
            else:
                print("Error: Sensor data read failed. Skipping data save.")
            time.sleep(60)
    except KeyboardInterrupt:
        print("Stopping sensor data collection.")
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()
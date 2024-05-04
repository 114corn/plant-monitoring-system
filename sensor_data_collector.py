import time
import sqlite3
import os
import csv
from datetime import datetime
import RPi.GPIO as GPIO

SOIL_MOISTURE_PIN_KEY = 'SOIL_MOISTURE_PIN'
TEMPERATURE_PIN_KEY = 'TEMPERATURE_PIN'
LIGHT_SENSOR_PIN_KEY = 'LIGHT_SENSOR_PIN'

DATABASE_FILENAME = 'sensor_data.db'
CSV_FILENAME = 'sensor_data.csv'

def init_sensors():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(int(os.getenv(SOIL_MOISTURE_PIN_KEY)), GPIO.IN)
    GPIO.setup(int(os.getenv(TEMPERATURE_PIN_KEY)), GPIO.IN)
    GPIO.setup(int(os.getenv(LIGHT_SENSOR_PIN_KEY)), GPIO.IN)

def read_sensor_data():
    try:
        soil_moisture = GPIO.input(int(os.getenv(SOIL_MOISTURE_PIN_KEY)))
        temperature = read_temperature_sensor()
        light = GPIO.input(int(os.getenv(LIGHT_SENSOR_PIN_KEY)))
        return soil_moisture, temperature, light
    except Exception as error:
        print(f"Error reading sensor data: {error}")
        return None, None, None

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
        except Exception as error:
            print(f"Error connecting to database: {error}")
            return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.commit()
            self.conn.close()

def init_database():
    try:
        with DatabaseManager(DATABASE_FILENAME) as cur:
            if cur:
                cur.execute('''
                CREATE TABLE IF NOT EXISTS sensor_data
                (timestamp TEXT, soil_moisture INTEGER, temperature INTEGER, light INTEGER)
                ''')
    except Exception as error:
        print(f"Error initializing database: {error}")

def save_to_database(data):
    try:
        with DatabaseManager(DATABASE_FILENAME) as cur:
            if cur:
                cur.execute('''
                INSERT INTO sensor_data (timestamp, soil_moisture, temperature, light)
                VALUES (?, ?, ?, ?)
                ''', (datetime.now(), *data))
    except Exception as error:
        print(f"Error saving data to database: {error}")

def save_to_csv(data):
    try:
        with open(CSV_FILENAME, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([datetime.now()] + list(data))
    except Exception as error:
        print(f"Error saving data to CSV: {error}")

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
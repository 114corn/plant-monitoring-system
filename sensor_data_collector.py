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
        return None

def read_temperature_sensor():
    return 25

def save_to_database(data):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS sensor_data
                (timestamp TEXT, soil_moisture INTEGER, temperature INTEGER, light INTEGER)''')
    cur.execute('''INSERT INTO sensor_data (timestamp, soil_moisture, temperature, light)
                VALUES (?, ?, ?, ?)''', (datetime.now(), data[0], data[1], data[2]))
    conn.commit()
    conn.close()

def save_to_csv(data):
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now()] + list(data))

def main():
    init_sensors()
    
    try:
        while True:
            data = read_sensor_data()
            if data:
                save_to_database(data)
                save_to_csv(data)
            time.sleep(60)
    except KeyboardInterrupt:
        print("Stopping sensor data collection.")
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()
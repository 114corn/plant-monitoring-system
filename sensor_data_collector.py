import time
import sqlite3
import os
import csv
from datetime import datetime
import RPi.GPIO as GPIO
import Adafruit_DHT  # Import the DHT library

# Environment Variables - Update as per your sensor types
DHT_SENSOR_TYPE = Adafruit_DHT.DHT22  # Replace DHT22 with DHT11 if you are using that
DHT_PIN = int(os.getenv(TEMPERATURE_PIN_KEY)) # Assuming TEMP_PIN is for DHT sensor

SOIL_MOISTURE_PIN_KEY = 'SOIL_MOISTURE_PIN'
LIGHT_SENSOR_PIN_KEY = 'LIGHT_SENSOR_PIN'

DATABASE_FILENAME = 'sensor_data.db'
CSV_FILENAME = 'sensor_data.csv'

# Alert thresholds
MOISTURE_THRESHOLD = 30  # Adjust based on your plant's needs
TEMP_THRESHOLD_LOW = 18  # Minimum temperature in Celsius
TEMP_THRESHOLD_HIGH = 27  # Maximum temperature in Celsius
LIGHT_THRESHOLD = 200  # Light intensity threshold (example value, adjust as needed)

def read_temperature_sensor():
    """Reads temperature and humidity from the DHT sensor."""
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR_TYPE, DHT_PIN)
    if humidity is not None and temperature is not None:
        return temperature
    else:
        print("Failed to retrieve data from humidity and temperature sensor")
        return None

def check_alerts(soil_moisture, temperature, light):
    """Check if the readings are outside of thresholds and print alerts."""
    if soil_moisture < MOISTURE_THRESHOLD:
        print("Alert: Soil moisture is below threshold!")
    if temperature < TEMP_THRESHOLD_LOW or temperature > TEMP_THRESHOLD_HIGH:
        print("Alert: Temperature is outside of the comfortable range!")
    if light < LIGHT_THRESHOLD:
        print("Alert: Light intensity is below threshold!")

def main():
    try:
        while True:
            data = read_sensor_data()
            if all(d is not None for d in data):
                save_to_database(data)
                save_to_csv(data)
                check_alerts(*data)  # Unpack data directly into the alert checking function
            else:
                print("Error: Sensor data read failed. Skipping data save.")
            time.sleep(60)
    except KeyboardInterrupt:
        print("Stopping sensor data collection.")
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()
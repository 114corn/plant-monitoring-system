import os
from dotenv import load_dotenv

load_dotenv()

TEMPERATURE_THRESHOLD = float(os.getenv('TEMPERATURE_THRESHOLD'))
HUMIDITY_THRESHOLD = float(os.getenv('HUMIDITY_THRESHOLD'))
PRESSURE_THRESHOLD = float(os.getenv('PRESSURE_THRESHOLD'))

NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL')
ENABLE_SMS_ALERTS = os.getenv('ENABLE_SMS_ALERTS') == 'True'
SMS_ALERT_NUMBER = os.getenv('SMS_ALERT_NUMBER')

DATABASE_PATH = os.getenv('DATABASE_PATH')

LOG_FILE = os.getenv('LOG_FILE')
LOG_LEVEL = os.getenv('LOG_LEVEL')

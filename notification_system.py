import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import data_analyzer
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
RECIPIENT_PHONE_NUMBER = os.getenv("RECIPIENT_PHONE_NUMBER")
def send_email(subject, message, recipient):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_HOST_USER
    msg['To'] = recipient
    msg['Subject'] = subject
    body = message
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
    server.starttls()
    server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
    text = msg.as_string()
    server.sendmail(EMAIL_HOST_USER, recipient, text)
    server.quit()
def send_sms(body, to=RECIPIENT_PHONE_NUMBER):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(body=body, from_=TWILIO_PHONE_NUMBER, to=to)
def analyze_data_and_alert():
    analysis_result = data_analyzer.analyze()
    if analysis_result.get('watering_needed', False):
        send_email('Watering Reminder', 'Your plant needs watering today.', os.getenv("RECIPIENT_EMAIL"))
        send_sms('Reminder: It\'s time to water your plants.')
    if analysis_result.get('temperature_warning', False):
        send_email('Temperature Warning', 'The temperature is at a critical level!', os.getenv("RECIPIENT_EMAIL"))
        send_sms('Warning: Critical temperature level detected!')
if __name__ == "__main__":
    analyze_data_and_alert()
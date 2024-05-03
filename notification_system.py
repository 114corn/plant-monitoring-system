import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import data_analyzer
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
RECIPIENT_PHONE_NUMBER = os.getenv("RECIPIENT_PHONE_NUMBER")

def send_email(subject, message, recipient):
    try:
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
    except smtplib.SMTPException as e:
        print('Failed to send email: ', e)

def send_sms(body, to=RECIPIENT_PHONE_NUMBER):
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(body=body, from_=TWILIO_PHONE_NUMBER, to=to)
    except TwilioRestException as e:
        print('Failed to send SMS: ', e)

def analyze_data_and_alert():
    try:
        analysis_result = data_analyzer.analyze()
    except Exception as e:
        print('Failed to analyze data: ', e)
        return

    recipient_email = os.getenv("RECIPIENT_EMAIL")
    if analysis_result.get('watering_needed', False):
        if recipient_email:
            send_email('Watering Reminder', 'Your plant needs watering today.', recipient_email)
        send_sms('Reminder: It\'s time to water your plants.')
        
    if analysis_result.get('temperature_warning', False):
        if recipient_email:
            send_email('Temperature Warning', 'The temperature is at a critical level!', recipient_email)
        send_sms('Warning: Critical temperature level detected!')

if __name__ == "__main__":
    analyze_data_and_alert()
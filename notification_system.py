import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import data_analyzer
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from dotenv import load_dotenv

load_dotenv()

class NotificationManager:
    def __init__(self):
        self.email_host = os.getenv("EMAIL_HOST")
        self.email_port = int(os.getenv("EMAIL_PORT", 587))
        self.email_host_user = os.getenv("EMAIL_HOST_USER")
        self.email_host_password = os.getenv("EMAIL_HOST_PASSWORD")
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.recipient_phone_number = os.getenv("RECIPIENT_PHONE_NUMBER")
        self.recipient_email = os.getenv("RECIPIENT_EMAIL")

    def send_email(self, subject, message, recipient):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_host_user
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))

            with smtplib.SMTP(self.email_host, self.email_port) as server:
                server.starttls()
                server.login(self.email_host_user, self.email_host_password)
                server.sendmail(self.email_host_user, recipient, msg.as_string())
        except smtplib.SMTPException as e:
            print('Failed to send email: ', e)

    def send_sms(self, body):
        try:
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            client.messages.create(body=body, from_=self.twilio_phone_number, to=self.recipient_phone_number)
        except TwilioRestException as e:
            print('Failed to send SMS: ', e)

def analyze_data_and_alert(notification_manager):
    try:
        analysis_result = data_analyzer.analyze()
    except Exception as e:
        print('Failed to analyze data: ', e)
        return

    if analysis_result.get('watering_needed', False):
        if notification_manager.recipient_email:
            notification_manager.send_email('Watering Reminder', 'Your plant needs watering today.', notification_manager.recipient_email)
        notification_manager.send_sms('Reminder: It\'s time to water your plants.')
        
    if analysis_result.get('temperature_warning', False):
        if notification_manager.recipient_email:
            notification_manager.send_email('Temperature Warning', 'The temperature is at a critical level!', notification_manager.recipient_email)
        notification_manager.send_sms('Warning: Critical temperature level detected!')

if __name__ == "__main__":
    notification_manager = NotificationManager()
    analyze_data_and_alert(notification_manager)
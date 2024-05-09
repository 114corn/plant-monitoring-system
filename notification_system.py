import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import data_analyzer
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class NotificationManager:
    def __init__(self):
        self.load_environment_variables()

    def load_environment_variables(self):
        self.email_host = os.getenv("EMAIL_HOST")
        self.email_port = int(os.getenv("EMAIL_PORT", 587))
        self.email_host_user = os.getenv("EMAIL_HOST_USER")
        self.email_host_password = os.getenv("EMAIL_HOST_PASSWORD")
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.recipient_phone_number = os.getenv("RECIPIENT_PHONE_NUMBER")
        self.recipient_email = os.getenv("RECIPIENT_EMAIL")

    def setup_email_message(self, subject, message, recipient):
        msg = MIMEMultipart()
        msg['From'] = self.email_host_user
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        return msg

    def send_email(self, subject, message, recipient):
        try:
            msg = self.setup_email_message(subject, message, recipient)

            with smtplib.SMTP(self.email_host, self.email_port) as server:
                self.connect_and_send(server, msg, recipient)
            logging.info(f"Email sent to {recipient} with subject: {subject}")
        except smtplib.SMTPException as e:
            logging.error('Failed to send email: %s', e)

    def connect_and_send(self, server, msg, recipient):
        server.starttls()
        server.login(self.email_host_user, self.email_host_password)
        server.sendmail(self.email_host_user, recipient, msg.as_string())

    def send_sms(self, body):
        try:
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            self.create_sms(client, body)
            logging.info(f"SMS sent to {self.recipient_phone_number}")
        except TwilioRestException as e:
            logging.error('Failed to send SMS: %s', e)

    def create_sms(self, client, body):
        message = client.messages.create(body=body, from_=self.twilio_phone_number, to=self.recipient_phone_number)
        logging.debug(f"Twilio message SID: {message.sid}")

def analyze_data_and_alert(notification_manager):
    try:
        analysis_result = data_analyzer.analyze()
        logging.debug("Data analysis result: %s", analysis_result)
    except Exception as e:
        logging.error('Failed to analyze data: %s', e)
        return

    send_alerts_based_on_analysis(notification_manager, analysis_result)

def send_alerts_based_on_analysis(notification_manager, analysis_result):
    if analysis_result.get('watering_needed', False):
        logging.info("Sending watering needed alerts")
        send_watering_alerts(notification_manager)

    if analysis_result.get('temperature_warning', False):
        logging.info("Sending temperature warning alerts")
        send_temperature_alerts(notification_manager)

def send_watering_alerts(notification_manager):
    message = 'Your plant needs watering today.'
    sms_message = "Reminder: It's time to water your plants."
    notification_manager.send_sms(sms_message)
    if notification_manager.recipient_email:
        notification_manager.send_email('Watering Reminder', message, notification_manager.recipient_email)

def send_temperature_alerts(notification_manager):
    message = 'The temperature is at a critical level!'
    sms_message = 'Warning: Critical temperature level detected!'
    notification_manager.send_sms(sms_message)
    if notification_manager.recipient_email:
        notification_manager.send_email('Temperature Warning', message, notification_manager.recipient_email)

if __name__ == "__main__":
    logging.info("Starting notification manager")
    notification_manager = NotificationManager()
    analyze_data_and_alert(notification_manager)
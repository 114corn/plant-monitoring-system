import os
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def load_environment_variables():
    """Loads required environment variables."""
    load_dotenv()
    variables = {
        'data_file_path': os.getenv('SENSOR_DATA_FILE_PATH'),
        'optimal_moisture_low': float(os.getenv('OPTIMAL_MOISTURE_LOW')),
        'optimal_moisture_high': float(os.getenv('OPTIMAL_MOISTURE_HIGH')),
        'optimal_light_low': float(os.getenv('OPTIMAL_LIGHT_LOW')),
        'optimal_light_high': float(os.getenv('OPTIMAL_LIGHT_HIGH')),
        'email_sender': os.getenv('EMAIL_SENDER'),
        'email_receiver': os.getenv('EMAIL_RECEIVER'),
        'email_password': os.getenv('EMAIL_PASSWORD')
    }
    return variables

def read_sensor_data(file_path):
    """Reads sensor data from a CSV file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The data file {file_path} does not exist.")
    return pd.read_csv(file_path)

def preprocess_data(df):
    """Converts timestamp column to datetime and sets it as index."""
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df.dropna(subset=['timestamp'], inplace=True)
    df.set_index('timestamp', inplace=True)
    return df

def compute_daily_averages(df):
    """Computes daily averages of the data."""
    return df.resample('D').mean()

def detect_outliers(df):
    """Detects outliers in the dataset using the IQR method."""
    q1 = df.quantile(0.25)
    q3 = df.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)
    return df[(df < lower_bound) | (df > upper_bound)]

def plot_daily_averages(df):
    """Plots the daily averages of moisture and light."""
    df.plot(y=['moisture', 'light'])
    plt.title('Daily Averages of Moisture and Light')
    plt.xlabel('Date')
    plt.ylabel('Average Readings')
    plt.show()

def check_environmental_suitability(row, optimal_values):
    """Checks if the environmental conditions are within optimal ranges."""
    warnings = []
    if not optimal_values['optimal_moisture_low'] <= row['moisture'] <= optimal_values['optimal_moisture_high']:
        warnings.append("Suboptimal moisture level")
    if not optimal_values['optimal_light_low'] <= row['light'] <= optimal_values['optimal_light_high']:
        warnings.append("Suboptimal light condition")
    return warnings

def send_summary_email(body, env_vars):
    """Sends an email with the summary report."""
    message = MIMEMultipart("alternative")
    message["Subject"] = "Plant Environment Monitoring System Summary"
    message["From"] = env_vars['email_sender']
    message["To"] = env_vars['email_receiver']

    # Turn these into plain/html MIMEText objects
    part = MIMEText(body, "plain")
    message.attach(part)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:  # Using Gmail's SMTP server as example
        server.login(env_vars['email_sender'], env_vars['email_password'])
        server.sendmail(
            env_vars['email_sender'], env_vars['email_receiver'], message.as_string()
        )

def compile_summary(daily_averages):
    """Compiles a summary of the daily averages and any warnings."""
    summary_lines = []
    for timestamp, row in daily_averages.iterrows():
        line = f"On {timestamp.date()}, the average moisture level was {row['moisture']:0.2f} and the light level was {row['light']:0.2f}."
        if 'warnings' in row and row['warnings']:
            line += f" Warnings: {', '.join(row['warnings'])}"
        else:
            line += " Conditions within optimal ranges."
        summary_lines.append(line)
    return "\n".join(summary_lines)

if __name__ == "__main__":
    env_vars = load_environment_variables()
    
    try:
        sensor_data = read_sensor_data(env_vars['data_file_path'])
        sensor_data = preprocess_data(sensor_data)
        daily_averages = compute_daily_averages(sensor_data)
        outliers = detect_outliers(sensor_data)
        
        plot_daily_averages(daily_averages)
        
        daily_averages['warnings'] = daily_averages.apply(check_environmental_suitability, args=(env_vars,), axis=1)

        summary = compile_summary(daily_averages)
        print(summary)  # Optional: Print the summary in console as well
        send_summary_email(summary, env_vars)
    except Exception as e:
        print(f"An error occurred: {e}")
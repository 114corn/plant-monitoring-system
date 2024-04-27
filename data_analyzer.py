import os
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt

load_dotenv()
data_file_path = os.getenv('SENSOR_DATA_FILE_PATH')
optimal_moisture_low = float(os.getenv('OPTIMAL_MOISTURE_LOW'))
optimal_moisture_high = float(os.getenv('OPTIMAL_MOISTURE_HIGH'))
optimal_light_low = float(os.getenv('OPTIMAL_LIGHT_LOW'))
optimal_light_high = float(os.getenv('OPTIMAL_LIGHT_HIGH'))

if not os.path.exists(data_file_path):
    raise FileNotFoundError(f"The data file {data_file_path} does not exist.")

sensor_data = pd.read_csv(data_file_path)

sensor_data['timestamp'] = pd.to_datetime(sensor_data['timestamp'])
sensor_data.set_index('timestamp', inplace=True)

daily_averages = sensor_data.resample('D').mean()

q1 = sensor_data.quantile(0.25)
q3 = sensor_data.quantile(0.75)
iqr = q3 - q1
lower_bound = q1 - (1.5 * iqr)
upper_bound = q3 + (1.5 * iqr)
outliers = sensor_data[(sensor_data < lower_bound) | (sensor_data > upper_bound)]

daily_averages.plot(y=['moisture', 'light'])
plt.title('Daily Averages of Moisture and Light')
plt.xlabel('Date')
plt.ylabel('Average Readings')
plt.show()

def check_environmental_suitability(row):
    warnings = []
    if row['moisture'] < optimal_moisture_low or row['moisture'] > optimal_moisture_high:
        warnings.append("Suboptimal moisture level")

    if row['light'] < optimal_light_low or row['light'] > optimal_light_high:
        warnings.append("Suboptimal light condition")

    return warnings

daily_averages['warnings'] = daily_averages.apply(check_environmental_suitability, axis=1)

for timestamp, row in daily_averages.iterrows():
    if row['warnings']:
        print(f"On {timestamp.date()}, there were suboptimal conditions: {', '.join(row['warnings'])}")
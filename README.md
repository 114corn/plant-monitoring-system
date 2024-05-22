# Plant Monitoring System

## Overview

This repository contains a Python script designed for interfacing with soil moisture, temperature, and light sensors via GPIO pins on a Raspberry Pi or compatible microcontroller. The script periodically collects and organizes sensor data, offering storage options in CSV format or a local SQLite database.

## Features

- **Sensor Integration**: Supports soil moisture, temperature, and light sensors.
- **Data Collection**: Periodically collects environmental data.
- **Data Storage**: Saves data in CSV format or SQLite database.
- **Easy Setup**: Includes functions for initializing sensors.
- **Error Handling**: Manages common issues like sensor disconnections and data corruption.

## Getting Started

1. **Clone the repository**:
   ```sh
   git clone https://github.com/114corn/plant-monitoring-system.git
   cd plant-monitoring-system
   ```

2. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

3. **Run the script**:
   ```sh
   python monitor.py
   ```

## Applications

Ideal for monitoring environmental conditions in agricultural, educational, or hobbyist projects.

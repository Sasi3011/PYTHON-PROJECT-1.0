"""
Sensor simulator for Smart Irrigation System
Simulates realistic sensor data for soil moisture, temperature, and humidity
"""
import random
import logging

logger = logging.getLogger(__name__)

def simulate_sensor_data():
    """
    Simulates sensor data with realistic values
    
    Returns:
        dict: Dictionary containing simulated sensor data
            - soil_moisture: 30-90% (percentage)
            - temperature: 15-40°C (celsius)
            - humidity: 40-90% (percentage)
    """
    try:
        # Generate random sensor values within realistic ranges
        soil_moisture = round(random.uniform(30.0, 90.0), 1)  # 30-90%
        temperature = round(random.uniform(15.0, 40.0), 1)    # 15-40°C
        humidity = round(random.uniform(40.0, 90.0), 1)       # 40-90%
        
        # Create sensor data dictionary
        sensor_data = {
            'soil_moisture': soil_moisture,
            'temperature': temperature,
            'humidity': humidity
        }
        
        logger.debug(f"Simulated sensor data: {sensor_data}")
        return sensor_data
        
    except Exception as e:
        logger.error(f"Error simulating sensor data: {str(e)}")
        # Return fallback values if simulation fails
        return {
            'soil_moisture': 60.0,
            'temperature': 25.0,
            'humidity': 65.0
        }

"""
Script to add new irrigation data to the MongoDB database
"""
import os
import sys
import django
import datetime

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sis.settings')
django.setup()

from django.conf import settings
from sis.core.models import IrrigationLog, SensorData, WeatherData, IrrigationDecision

def add_irrigation_log(user, crop_type, soil_type, latitude, longitude, 
                      soil_moisture, temp, humidity, 
                      weather_temp, weather_humidity, rain_prob,
                      water_amount, duration, status):
    """Add a new irrigation log to the database"""
    
    # Create embedded documents
    sensor_data = SensorData(
        soil_moisture=soil_moisture,
        temperature=temp,
        humidity=humidity
    )
    
    weather_data = WeatherData(
        temperature=weather_temp,
        humidity=weather_humidity,
        rain_probability=rain_prob
    )
    
    decision = IrrigationDecision(
        water_amount=water_amount,
        duration=duration,
        status=status
    )
    
    # Create and save the log
    log = IrrigationLog(
        user=user,
        crop_type=crop_type,
        soil_type=soil_type,
        latitude=latitude,
        longitude=longitude,
        sensor_data=sensor_data,
        weather_data=weather_data,
        decision=decision
    )
    
    log.save()
    return log

def main():
    """Main function"""
    print("Adding new irrigation data to MongoDB...")
    
    # Check if MongoDB is available
    if not getattr(settings, 'MONGODB_AVAILABLE', False):
        print("MongoDB is not available. Please check your connection settings.")
        return
    
    # Add a new irrigation log
    log = add_irrigation_log(
        user="user_input",
        crop_type="tomato",
        soil_type="loam",
        latitude=12.9716,
        longitude=77.5946,
        soil_moisture=65.5,
        temp=28.3,
        humidity=70.2,
        weather_temp=30.1,
        weather_humidity=65.0,
        rain_prob=20.0,
        water_amount=1.2,
        duration=2.5,
        status="Active"
    )
    
    print(f"Added new irrigation log with ID: {log.id}")
    print("Data added successfully!")

if __name__ == "__main__":
    main()

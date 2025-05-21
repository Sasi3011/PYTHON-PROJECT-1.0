"""
Script to seed the database with sample data for the Smart Irrigation System
"""
import os
import sys
import django
import datetime
import random

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sis.settings')
django.setup()

# Import models
from django.conf import settings

# Check if MongoDB is available
if not getattr(settings, 'MONGODB_AVAILABLE', False):
    print("MongoDB is not available. Please check your connection settings.")
    sys.exit(1)

# Import models
from sis.core.models import Crop, Soil, IrrigationLog, SensorData, WeatherData, IrrigationDecision

def create_crops():
    """Create sample crop data"""
    crops_data = [
        {
            'name': 'tomato',
            'ideal_moisture': [60, 80],
            'ideal_temp': [18, 29],
            'base_water_lph': 0.8
        },
        {
            'name': 'potato',
            'ideal_moisture': [65, 75],
            'ideal_temp': [15, 25],
            'base_water_lph': 0.7
        },
        {
            'name': 'corn',
            'ideal_moisture': [55, 75],
            'ideal_temp': [20, 30],
            'base_water_lph': 0.9
        },
        {
            'name': 'lettuce',
            'ideal_moisture': [70, 85],
            'ideal_temp': [15, 22],
            'base_water_lph': 0.6
        },
        {
            'name': 'wheat',
            'ideal_moisture': [50, 70],
            'ideal_temp': [18, 24],
            'base_water_lph': 0.5
        }
    ]
    
    # Delete existing crops
    Crop.objects.all().delete()
    
    # Create new crops
    for crop_data in crops_data:
        Crop.objects.create(**crop_data)
    
    print(f"Created {len(crops_data)} crops")

def create_soils():
    """Create sample soil data"""
    soils_data = [
        {
            'name': 'clay',
            'absorption_rate': 0.3
        },
        {
            'name': 'sandy',
            'absorption_rate': 0.8
        },
        {
            'name': 'loam',
            'absorption_rate': 0.6
        },
        {
            'name': 'silt',
            'absorption_rate': 0.5
        }
    ]
    
    # Delete existing soils
    Soil.objects.all().delete()
    
    # Create new soils
    for soil_data in soils_data:
        Soil.objects.create(**soil_data)
    
    print(f"Created {len(soils_data)} soils")

def create_irrigation_logs():
    """Create sample irrigation logs"""
    # Get all crops and soils
    crops = list(Crop.objects.all())
    soils = list(Soil.objects.all())
    
    if not crops or not soils:
        print("No crops or soils found. Please run create_crops() and create_soils() first.")
        return
    
    # Delete existing logs
    IrrigationLog.objects.all().delete()
    
    # Create 20 sample logs
    logs_count = 20
    users = ['farmer1', 'farmer2', 'admin', 'technician']
    statuses = ['Active', 'Pending', 'Completed', 'Cancelled']
    
    for i in range(logs_count):
        # Random crop and soil
        crop = random.choice(crops)
        soil = random.choice(soils)
        
        # Random location (around a central point)
        base_lat, base_lon = 12.9716, 77.5946  # Bangalore, India
        lat = base_lat + (random.random() - 0.5) * 0.1
        lon = base_lon + (random.random() - 0.5) * 0.1
        
        # Random timestamp within the last 30 days
        days_ago = random.randint(0, 30)
        timestamp = datetime.datetime.utcnow() - datetime.timedelta(days=days_ago)
        
        # Create sensor data
        sensor_data = SensorData(
            soil_moisture=random.uniform(40, 90),
            temperature=random.uniform(15, 35),
            humidity=random.uniform(30, 90)
        )
        
        # Create weather data
        weather_data = WeatherData(
            temperature=random.uniform(15, 35),
            humidity=random.uniform(30, 90),
            rain_probability=random.uniform(0, 100)
        )
        
        # Create irrigation decision
        decision = IrrigationDecision(
            water_amount=random.uniform(0.5, 2.0),
            duration=random.uniform(0.5, 3.0),
            status=random.choice(statuses)
        )
        
        # Create irrigation log
        IrrigationLog.objects.create(
            timestamp=timestamp,
            user=random.choice(users),
            crop_type=crop.name,
            soil_type=soil.name,
            latitude=lat,
            longitude=lon,
            sensor_data=sensor_data,
            weather_data=weather_data,
            decision=decision
        )
    
    print(f"Created {logs_count} irrigation logs")

if __name__ == '__main__':
    print("Seeding database with sample data...")
    create_crops()
    create_soils()
    create_irrigation_logs()
    print("Database seeding completed!")

"""
Script to view both API data and database data from the Smart Irrigation System
"""
import requests
import json
import sys
import os
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sis.settings')
django.setup()

# Import models if MongoDB is available
from django.conf import settings

if getattr(settings, 'MONGODB_AVAILABLE', False):
    from sis.core.models import Crop, Soil, IrrigationLog
    from sis.core.models_location import LocationSearch

# API Base URL
BASE_URL = "http://localhost:8000/api"

def get_api_data(endpoint):
    """Get data from an API endpoint"""
    url = f"{BASE_URL}/{endpoint}/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error accessing {url}: {e}")
        return None

def print_formatted_data(data, title):
    """Print data in a formatted way"""
    print(f"\n{'=' * 50}")
    print(f"{title}")
    print(f"{'=' * 50}")
    print(json.dumps(data, indent=2))
    print(f"{'=' * 50}\n")

def get_database_crops():
    """Get crop data from the database"""
    if not getattr(settings, 'MONGODB_AVAILABLE', False):
        return []
        
    try:
        crops = Crop.objects.all()
        return [
            {
                'name': crop.name,
                'ideal_moisture': crop.ideal_moisture,
                'ideal_temp': crop.ideal_temp,
                'base_water_lph': crop.base_water_lph
            }
            for crop in crops
        ]
    except Exception as e:
        print(f"Error retrieving crops: {str(e)}")
        return []

def get_database_soils():
    """Get soil data from the database"""
    if not getattr(settings, 'MONGODB_AVAILABLE', False):
        return []
        
    try:
        soils = Soil.objects.all()
        return [
            {
                'name': soil.name,
                'absorption_rate': soil.absorption_rate
            }
            for soil in soils
        ]
    except Exception as e:
        print(f"Error retrieving soils: {str(e)}")
        return []

def get_database_irrigation_logs():
    """Get irrigation log data from the database"""
    if not getattr(settings, 'MONGODB_AVAILABLE', False):
        return []
        
    try:
        logs = IrrigationLog.objects.all().order_by('-timestamp')[:5]  # Get first 5 logs
        return [
            {
                'timestamp': str(log.timestamp),
                'user': log.user,
                'crop_type': log.crop_type,
                'soil_type': log.soil_type,
                'location': [log.latitude, log.longitude],
                'sensor_data': {
                    'soil_moisture': log.sensor_data.soil_moisture,
                    'temperature': log.sensor_data.temperature,
                    'humidity': log.sensor_data.humidity
                },
                'weather_data': {
                    'temperature': log.weather_data.temperature,
                    'humidity': log.weather_data.humidity,
                    'rain_probability': log.weather_data.rain_probability
                },
                'decision': {
                    'water_amount': log.decision.water_amount,
                    'duration': log.decision.duration,
                    'status': log.decision.status
                }
            }
            for log in logs
        ]
    except Exception as e:
        print(f"Error retrieving irrigation logs: {str(e)}")
        return []

def main():
    """Main function"""
    print("\n" + "=" * 80)
    print("SMART IRRIGATION SYSTEM DATA VIEWER")
    print("=" * 80)
    
    print("\n" + "*" * 80)
    print("API DATA (In-memory data used by the API endpoints)")
    print("*" * 80)
    
    # Get irrigation history from API
    history_data = get_api_data("irrigation/history")
    if history_data:
        print_formatted_data(history_data, "API: IRRIGATION HISTORY")
    
    # Get crop and soil data from API
    crop_data = get_api_data("crops")
    if crop_data:
        print_formatted_data(crop_data, "API: CROP AND SOIL DATA")
    
    # Get location history from API
    location_data = get_api_data("locations/history")
    if location_data:
        print_formatted_data(location_data, "API: LOCATION HISTORY")
    
    print("\n" + "*" * 80)
    print("DATABASE DATA (MongoDB data stored in the database)")
    print("*" * 80)
    
    # Get crop data from database
    db_crops = get_database_crops()
    print_formatted_data({"crops": db_crops}, "DATABASE: CROPS")
    
    # Get soil data from database
    db_soils = get_database_soils()
    print_formatted_data({"soils": db_soils}, "DATABASE: SOILS")
    
    # Get irrigation logs from database
    db_logs = get_database_irrigation_logs()
    print_formatted_data({"logs": db_logs}, "DATABASE: IRRIGATION LOGS (First 5)")
    
    # Add location search history
    if getattr(settings, 'MONGODB_AVAILABLE', False):
        try:
            location_searches = LocationSearch.objects.order_by('-timestamp')[:5]
            location_data = [
                {
                    'timestamp': str(search.timestamp),
                    'user': search.user,
                    'location_name': search.location_name,
                    'coordinates': [search.latitude, search.longitude],
                    'search_query': search.search_query
                }
                for search in location_searches
            ]
            print_formatted_data({"location_searches": location_data}, "DATABASE: LOCATION SEARCHES (First 5)")
        except Exception as e:
            print(f"Error retrieving location searches: {str(e)}")
    
    print("\nNOTE: The application is now using MongoDB to store data.")
    print("Any input you provide will be stored in the MongoDB database.")
    print("Existing data in the database is displayed above.")

if __name__ == "__main__":
    main()

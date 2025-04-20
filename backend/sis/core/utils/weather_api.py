"""
Weather API integration for Smart Irrigation System
Fetches real-time weather data from OpenWeatherMap API
"""
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def get_weather_data(latitude, longitude):
    """
    Fetches real-time weather data from OpenWeatherMap API
    
    Args:
        latitude (float): Latitude coordinate
        longitude (float): Longitude coordinate
        
    Returns:
        dict: Dictionary containing weather data
            - temperature: Temperature in Celsius
            - humidity: Humidity percentage
            - rain_probability: Probability of rain (percentage)
            
    Raises:
        Exception: If API request fails
    """
    try:
        # Get API key from settings
        api_key = settings.OPENWEATHERMAP_API_KEY
        if not api_key:
            logger.error("OpenWeatherMap API key not configured")
            raise ValueError("OpenWeatherMap API key not configured")
        
        # Build API URL
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&units=metric"
        
        # Make API request
        logger.debug(f"Fetching weather data for coordinates: {latitude}, {longitude}")
        response = requests.get(url, timeout=10)
        
        # Check if request was successful
        if response.status_code != 200:
            logger.error(f"OpenWeatherMap API error: {response.status_code} - {response.text}")
            raise Exception(f"OpenWeatherMap API error: {response.status_code}")
        
        # Parse response data
        data = response.json()
        
        # Extract relevant weather information
        temperature = data['main']['temp']
        humidity = data['main']['humidity']
        
        # Calculate rain probability based on weather conditions
        # OpenWeatherMap doesn't directly provide rain probability, so we estimate it
        weather_id = data['weather'][0]['id']
        if weather_id < 300:  # Thunderstorm
            rain_probability = 90.0
        elif weather_id < 400:  # Drizzle
            rain_probability = 70.0
        elif weather_id < 600:  # Rain
            rain_probability = 80.0
        elif weather_id < 700:  # Snow
            rain_probability = 50.0
        elif weather_id < 800:  # Atmosphere (fog, haze, etc.)
            rain_probability = 30.0
        elif weather_id == 800:  # Clear
            rain_probability = 0.0
        elif weather_id < 900:  # Clouds
            cloud_percent = data['clouds']['all']
            rain_probability = min(cloud_percent, 40.0)  # Max 40% for just clouds
        else:
            rain_probability = 20.0  # Default
        
        # Create weather data dictionary
        weather_data = {
            'temperature': round(temperature, 1),
            'humidity': round(humidity, 1),
            'rain_probability': round(rain_probability, 1)
        }
        
        logger.debug(f"Weather data: {weather_data}")
        return weather_data
        
    except Exception as e:
        logger.error(f"Error fetching weather data: {str(e)}")
        raise

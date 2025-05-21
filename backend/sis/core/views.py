"""
API views for Smart Irrigation System (Using MongoDB database)
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import JsonResponse
import json
import csv
from datetime import datetime
import logging
import random
from django.conf import settings

from .utils.sensor_simulator import simulate_sensor_data
from .utils.weather_api import get_weather_data

# Import MongoDB models if available
if getattr(settings, 'MONGODB_AVAILABLE', False):
    from .models import Crop, Soil, IrrigationLog, SensorData, WeatherData, IrrigationDecision as IrrigationDecisionModel

logger = logging.getLogger(__name__)

# Function to get crops from MongoDB or fallback to hardcoded data
def get_crops():
    if getattr(settings, 'MONGODB_AVAILABLE', False):
        try:
            # Get crops from MongoDB
            crops_dict = {}
            for crop in Crop.objects.all():
                crops_dict[crop.name] = {
                    'name': crop.name,
                    'ideal_moisture': crop.ideal_moisture,
                    'ideal_temp': crop.ideal_temp,
                    'base_water_lph': crop.base_water_lph
                }
            return crops_dict
        except Exception as e:
            logger.error(f"Error fetching crops from MongoDB: {str(e)}")
    
    # Fallback to hardcoded data
    return {
        "turmeric": {
            "name": "turmeric",
            "ideal_moisture": [65, 75],
            "ideal_temp": [25, 30],
            "base_water_lph": 1.2
        },
        "tomato": {
            "name": "tomato",
            "ideal_moisture": [60, 70],
            "ideal_temp": [20, 28],
            "base_water_lph": 0.9
        },
        "potato": {
            "name": "potato",
            "ideal_moisture": [55, 65],
            "ideal_temp": [18, 24],
            "base_water_lph": 0.8
        },
        "rice": {
            "name": "rice",
            "ideal_moisture": [80, 90],
            "ideal_temp": [24, 32],
            "base_water_lph": 1.5
        }
    }

# Function to get soils from MongoDB or fallback to hardcoded data
def get_soils():
    if getattr(settings, 'MONGODB_AVAILABLE', False):
        try:
            # Get soils from MongoDB
            soils_dict = {}
            for soil in Soil.objects.all():
                soils_dict[soil.name] = {
                    'name': soil.name,
                    'absorption_rate': soil.absorption_rate
                }
            return soils_dict
        except Exception as e:
            logger.error(f"Error fetching soils from MongoDB: {str(e)}")
    
    # Fallback to hardcoded data
    return {
        "Red Soil": {
            "name": "Red Soil",
            "absorption_rate": 0.8
        },
        "Black Soil": {
            "name": "Black Soil",
            "absorption_rate": 0.7
        },
        "Alluvial Soil": {
            "name": "Alluvial Soil",
            "absorption_rate": 0.9
        },
        "Loamy Soil": {
            "name": "Loamy Soil",
            "absorption_rate": 0.85
        }
    }

# Function to get irrigation history from MongoDB or fallback to in-memory storage
def get_irrigation_history():
    if getattr(settings, 'MONGODB_AVAILABLE', False):
        try:
            # Get irrigation logs from MongoDB
            history = []
            for log in IrrigationLog.objects.order_by('-timestamp')[:50]:
                history.append({
                    'id': str(log.id),
                    'timestamp': log.timestamp.isoformat(),
                    'user': log.user,
                    'crop_type': log.crop_type,
                    'soil_type': log.soil_type,
                    'latitude': log.latitude,
                    'longitude': log.longitude,
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
                })
            return history
        except Exception as e:
            logger.error(f"Error fetching irrigation history from MongoDB: {str(e)}")
    
    # Fallback to in-memory storage
    return []

# Initialize in-memory history storage as fallback
IRRIGATION_HISTORY = []

def calculate_irrigation_decision(crop_data, soil_data, sensor_data, weather_data):
    """
    Simplified decision engine for demo purposes
    """
    try:
        # Extract relevant data
        base_water = crop_data['base_water_lph']
        ideal_moisture_min = crop_data['ideal_moisture'][0]
        ideal_moisture_max = crop_data['ideal_moisture'][1]
        ideal_temp_min = crop_data['ideal_temp'][0]
        ideal_temp_max = crop_data['ideal_temp'][1]
        
        soil_absorption = soil_data['absorption_rate']
        
        current_moisture = sensor_data['soil_moisture']
        current_temp = sensor_data['temperature']
        
        rain_probability = weather_data['rain_probability']
        
        # Initialize water amount with base value
        water_amount = base_water
        
        # Apply rule-based adjustments
        if current_moisture < ideal_moisture_min:
            water_amount *= 1.2  # Increase by 20%
        elif current_moisture > ideal_moisture_max:
            water_amount *= 0.8  # Decrease by 20%
            
        if current_temp > ideal_temp_max:
            water_amount *= 1.1  # Increase by 10%
            
        if rain_probability > 60.0:
            water_amount *= 0.5  # Decrease by 50%
            
        water_amount /= soil_absorption
        
        # Calculate duration
        duration = 2.0
        if current_moisture < ideal_moisture_min:
            duration = 3.0
        
        # Determine status
        if rain_probability > 80.0:
            status = "Pending"
        elif current_moisture > ideal_moisture_max * 1.2:
            status = "Cancelled"
        else:
            status = "Active"
        
        return {
            'water_amount': round(water_amount, 2),
            'duration': round(duration, 1),
            'status': status
        }
        
    except Exception as e:
        logger.error(f"Error calculating irrigation decision: {str(e)}")
        return {
            'water_amount': 1.0,
            'duration': 2.0,
            'status': 'Pending'
        }

class IrrigationDecisionView(APIView):
    """
    API view for making irrigation decisions
    POST: Process inputs and return irrigation decision
    """
    permission_classes = [AllowAny]  # Temporarily set to AllowAny for demo
    
    def post(self, request):
        try:
            # Extract input data
            data = request.data
            
            # Validate required fields
            required_fields = ['crop_type', 'soil_type', 'latitude', 'longitude']
            for field in required_fields:
                if field not in data:
                    return Response(
                        {"error": f"Missing required field: {field}"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Validate numeric fields
            try:
                latitude = float(data['latitude'])
                longitude = float(data['longitude'])
                if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                    return Response(
                        {"error": "Invalid latitude or longitude values"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {"error": "Latitude and longitude must be numeric"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get crops and soils from MongoDB or fallback
            crops = get_crops()
            soils = get_soils()
            
            # Validate crop and soil types
            if data['crop_type'] not in crops:
                return Response(
                    {"error": f"Crop type '{data['crop_type']}' not found"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            if data['soil_type'] not in soils:
                return Response(
                    {"error": f"Soil type '{data['soil_type']}' not found"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            crop = crops[data['crop_type']]
            soil = soils[data['soil_type']]
            
            # Simulate sensor data
            sensor_data = simulate_sensor_data()
            
            # Get weather data or use fallback
            try:
                weather_data = get_weather_data(latitude, longitude)
            except Exception as e:
                logger.error(f"Weather API error: {str(e)}")
                # Fallback weather data
                weather_data = {
                    'temperature': 25.0,
                    'humidity': 60.0,
                    'rain_probability': 10.0
                }
            
            # Calculate irrigation decision
            decision = calculate_irrigation_decision(
                crop_data=crop,
                soil_data=soil,
                sensor_data=sensor_data,
                weather_data=weather_data
            )
            
            # Store in MongoDB if available
            if getattr(settings, 'MONGODB_AVAILABLE', False):
                try:
                    # Create embedded documents
                    sensor_data_doc = SensorData(
                        soil_moisture=sensor_data['soil_moisture'],
                        temperature=sensor_data['temperature'],
                        humidity=sensor_data['humidity']
                    )
                    
                    weather_data_doc = WeatherData(
                        temperature=weather_data['temperature'],
                        humidity=weather_data['humidity'],
                        rain_probability=weather_data['rain_probability']
                    )
                    
                    decision_doc = IrrigationDecisionModel(
                        water_amount=decision['water_amount'],
                        duration=decision['duration'],
                        status=decision['status']
                    )
                    
                    # Create and save the log
                    log = IrrigationLog(
                        user=request.user.username if request.user.is_authenticated else 'guest',
                        crop_type=data['crop_type'],
                        soil_type=data['soil_type'],
                        latitude=latitude,
                        longitude=longitude,
                        sensor_data=sensor_data_doc,
                        weather_data=weather_data_doc,
                        decision=decision_doc
                    )
                    
                    log.save()
                    history_entry = {
                        'id': str(log.id),
                        'timestamp': log.timestamp.isoformat(),
                        'user': log.user,
                        'crop_type': log.crop_type,
                        'soil_type': log.soil_type,
                        'latitude': log.latitude,
                        'longitude': log.longitude,
                        'sensor_data': sensor_data,
                        'weather_data': weather_data,
                        'decision': decision
                    }
                except Exception as e:
                    logger.error(f"Error saving to MongoDB: {str(e)}")
                    # Fallback to in-memory storage
                    history_entry = {
                        'id': str(len(IRRIGATION_HISTORY) + 1),
                        'timestamp': datetime.now().isoformat(),
                        'user': request.user.username if request.user.is_authenticated else 'guest',
                        'crop_type': data['crop_type'],
                        'soil_type': data['soil_type'],
                        'latitude': latitude,
                        'longitude': longitude,
                        'sensor_data': sensor_data,
                        'weather_data': weather_data,
                        'decision': decision
                    }
                    IRRIGATION_HISTORY.insert(0, history_entry)
            else:
                # Fallback to in-memory storage
                history_entry = {
                    'id': str(len(IRRIGATION_HISTORY) + 1),
                    'timestamp': datetime.now().isoformat(),
                    'user': request.user.username if request.user.is_authenticated else 'guest',
                    'crop_type': data['crop_type'],
                    'soil_type': data['soil_type'],
                    'latitude': latitude,
                    'longitude': longitude,
                    'sensor_data': sensor_data,
                    'weather_data': weather_data,
                    'decision': decision
                }
                IRRIGATION_HISTORY.insert(0, history_entry)
            
            # Prepare response
            response_data = {
                'id': history_entry['id'],
                'timestamp': history_entry['timestamp'],
                'sensor_data': sensor_data,
                'weather_data': weather_data,
                'decision': decision
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error processing irrigation decision: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred", "details": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class IrrigationHistoryView(APIView):
    """
    API view for retrieving irrigation history
    GET: Retrieve irrigation history (limit to 50 records, sorted by timestamp)
    """
    permission_classes = [AllowAny]  # Temporarily set to AllowAny for demo
    
    def get(self, request):
        try:
            # Get irrigation history from MongoDB or fallback
            history = get_irrigation_history()
            
            # If MongoDB history is empty but we have in-memory history, use that
            if not history and IRRIGATION_HISTORY:
                history = IRRIGATION_HISTORY[:50]
                
            return Response({"history": history})
            
        except Exception as e:
            logger.error(f"Error retrieving irrigation history: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred", "details": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ExportHistoryCSVView(APIView):
    """
    API view for exporting irrigation history as CSV
    GET: Export irrigation history as CSV
    """
    permission_classes = [AllowAny]  # Temporarily set to AllowAny for demo
    
    def get(self, request):
        try:
            # Create CSV response
            response = JsonResponse({})
            response['Content-Type'] = 'text/csv'
            response['Content-Disposition'] = 'attachment; filename="irrigation_history.csv"'
            
            # Write CSV data
            writer = csv.writer(response)
            writer.writerow([
                'Timestamp', 'Crop Type', 'Soil Type', 'Latitude', 'Longitude',
                'Soil Moisture (%)', 'Sensor Temp (°C)', 'Sensor Humidity (%)',
                'Weather Temp (°C)', 'Weather Humidity (%)', 'Rain Probability (%)',
                'Water Amount (L/h)', 'Duration (h)', 'Status'
            ])
            
            for log in IRRIGATION_HISTORY:
                writer.writerow([
                    log['timestamp'],
                    log['crop_type'],
                    log['soil_type'],
                    log['latitude'],
                    log['longitude'],
                    log['sensor_data']['soil_moisture'],
                    log['sensor_data']['temperature'],
                    log['sensor_data']['humidity'],
                    log['weather_data']['temperature'],
                    log['weather_data']['humidity'],
                    log['weather_data']['rain_probability'],
                    log['decision']['water_amount'],
                    log['decision']['duration'],
                    log['decision']['status']
                ])
            
            return response
            
        except Exception as e:
            logger.error(f"Error exporting irrigation history: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred", "details": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CropSoilDataView(APIView):
    """
    API view for retrieving crop and soil data
    GET: Retrieve available crops and soil types
    """
    permission_classes = [AllowAny]  # Temporarily set to AllowAny for demo
    
    def get(self, request):
        try:
            # Get crops and soils from MongoDB or fallback
            crops = get_crops()
            soils = get_soils()
            
            # Return crop and soil data
            return Response({
                'crops': list(crops.values()),
                'soils': list(soils.values())
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving crop and soil data: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred", "details": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

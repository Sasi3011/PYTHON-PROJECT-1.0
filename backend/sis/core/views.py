"""
API views for Smart Irrigation System (Temporary implementation without MongoDB)
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

from .utils.sensor_simulator import simulate_sensor_data
from .utils.weather_api import get_weather_data

logger = logging.getLogger(__name__)

# Temporary in-memory storage for demo purposes
CROPS = {
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

SOILS = {
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

# In-memory history storage
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
            
            # Validate crop and soil types
            if data['crop_type'] not in CROPS:
                return Response(
                    {"error": f"Crop type '{data['crop_type']}' not found"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            if data['soil_type'] not in SOILS:
                return Response(
                    {"error": f"Soil type '{data['soil_type']}' not found"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            crop = CROPS[data['crop_type']]
            soil = SOILS[data['soil_type']]
            
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
            
            # Create log entry
            log_entry = {
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
            
            # Add to history
            IRRIGATION_HISTORY.append(log_entry)
            
            # Prepare response
            response_data = {
                'id': log_entry['id'],
                'timestamp': log_entry['timestamp'],
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
            # Get query parameters
            limit = int(request.query_params.get('limit', 50))
            crop_type = request.query_params.get('crop_type', None)
            
            # Filter history
            if crop_type:
                filtered_history = [log for log in IRRIGATION_HISTORY if log['crop_type'] == crop_type]
            else:
                filtered_history = IRRIGATION_HISTORY.copy()
            
            # Sort by timestamp (newest first)
            filtered_history.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Apply limit
            filtered_history = filtered_history[:limit]
            
            return Response({'history': filtered_history}, status=status.HTTP_200_OK)
            
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
            # Format response
            crop_data = []
            for crop_name, crop in CROPS.items():
                crop_data.append({
                    'name': crop['name'],
                    'ideal_moisture': crop['ideal_moisture'],
                    'ideal_temp': crop['ideal_temp'],
                    'base_water_lph': crop['base_water_lph']
                })
            
            soil_data = []
            for soil_name, soil in SOILS.items():
                soil_data.append({
                    'name': soil['name'],
                    'absorption_rate': soil['absorption_rate']
                })
            
            return Response({
                'crops': crop_data,
                'soils': soil_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving crop and soil data: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred", "details": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

"""
MongoDB models for Smart Irrigation System
"""
from mongoengine import Document, EmbeddedDocument, fields
import datetime

class SensorData(EmbeddedDocument):
    """Embedded document for sensor data"""
    soil_moisture = fields.FloatField(required=True)  # percentage
    temperature = fields.FloatField(required=True)    # celsius
    humidity = fields.FloatField(required=True)       # percentage

class WeatherData(EmbeddedDocument):
    """Embedded document for weather data"""
    temperature = fields.FloatField(required=True)    # celsius
    humidity = fields.FloatField(required=True)       # percentage
    rain_probability = fields.FloatField(required=True)  # percentage

class IrrigationDecision(EmbeddedDocument):
    """Embedded document for irrigation decision"""
    water_amount = fields.FloatField(required=True)   # liters per hour
    duration = fields.FloatField(required=True)       # hours
    status = fields.StringField(required=True, choices=['Active', 'Pending', 'Completed', 'Cancelled'])

class Crop(Document):
    """Document for crop data"""
    name = fields.StringField(required=True, unique=True)
    ideal_moisture = fields.ListField(fields.FloatField(), required=True)  # [min, max] percentage
    ideal_temp = fields.ListField(fields.FloatField(), required=True)      # [min, max] celsius
    base_water_lph = fields.FloatField(required=True)  # base water need in liters per hour
    
    meta = {
        'collection': 'crops',
        'indexes': ['name']
    }

class Soil(Document):
    """Document for soil data"""
    name = fields.StringField(required=True, unique=True)
    absorption_rate = fields.FloatField(required=True)  # coefficient (0-1)
    
    meta = {
        'collection': 'soils',
        'indexes': ['name']
    }

class IrrigationLog(Document):
    """Document for irrigation log data"""
    timestamp = fields.DateTimeField(default=datetime.datetime.utcnow)
    user = fields.StringField(required=True)
    
    # Input data
    crop_type = fields.StringField(required=True)
    soil_type = fields.StringField(required=True)
    latitude = fields.FloatField(required=True)
    longitude = fields.FloatField(required=True)
    
    # Sensor and weather data
    sensor_data = fields.EmbeddedDocumentField(SensorData, required=True)
    weather_data = fields.EmbeddedDocumentField(WeatherData, required=True)
    
    # Decision data
    decision = fields.EmbeddedDocumentField(IrrigationDecision, required=True)
    
    meta = {
        'collection': 'irrigation_logs',
        'indexes': [
            'timestamp', 
            'crop_type',
            'user',
            ('latitude', 'longitude')
        ],
        'ordering': ['-timestamp']
    }

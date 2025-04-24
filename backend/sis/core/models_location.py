"""
MongoDB models for location search functionality
"""
from mongoengine import Document, fields
import datetime

class LocationSearch(Document):
    """Document for location search data"""
    timestamp = fields.DateTimeField(default=datetime.datetime.utcnow)
    user = fields.StringField(required=True)
    
    # Location data
    location_name = fields.StringField(required=True)
    latitude = fields.FloatField(required=True)
    longitude = fields.FloatField(required=True)
    
    # Search query
    search_query = fields.StringField(required=False)
    
    # Additional data
    additional_data = fields.DictField(required=False)
    
    meta = {
        'collection': 'location_searches',
        'indexes': [
            'timestamp', 
            'user',
            ('latitude', 'longitude')
        ],
        'ordering': ['-timestamp']
    }

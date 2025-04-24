"""
API views for location search functionality
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import HttpResponse
import json
import csv
import requests
from datetime import datetime
import logging
from django.conf import settings

# Import MongoDB model only if MongoDB is available
if getattr(settings, 'MONGODB_AVAILABLE', False):
    from .models_location import LocationSearch
else:
    # Create a dummy in-memory storage if MongoDB is not available
    class DummyLocationSearch:
        _storage = []
        
        @classmethod
        def objects(cls, **kwargs):
            return cls
            
        @classmethod
        def order_by(cls, field):
            return cls._storage
            
        @classmethod
        def limit(cls, count):
            return cls._storage[:count]
            
        @classmethod
        def save(cls, **kwargs):
            cls._storage.append(kwargs)
            return True
    
    LocationSearch = DummyLocationSearch

logger = logging.getLogger(__name__)

class LocationSearchView(APIView):
    """
    API view for searching locations
    GET: Search for locations using a query string
    """
    permission_classes = [AllowAny]  # Temporarily set to AllowAny for demo
    
    def get(self, request):
        try:
            # Get search query from request
            query = request.query_params.get('q', '')
            if not query:
                return Response(
                    {"error": "Search query is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Use Nominatim API for geocoding (OpenStreetMap)
            nominatim_url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': query,
                'format': 'json',
                'limit': 10,
                'addressdetails': 1
            }
            
            headers = {
                'User-Agent': 'SmartIrrigationSystem/1.0'
            }
            
            response = requests.get(nominatim_url, params=params, headers=headers)
            
            if response.status_code != 200:
                return Response(
                    {"error": f"Failed to search places: {response.text}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            results = response.json()
            
            # Format the results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'name': result.get('display_name', ''),
                    'latitude': float(result.get('lat', 0)),
                    'longitude': float(result.get('lon', 0)),
                    'type': result.get('type', ''),
                    'address': result.get('address', {})
                })
            
            # Save the search if a user is authenticated and MongoDB is available
            if request.user.is_authenticated and formatted_results and getattr(settings, 'MONGODB_AVAILABLE', False):
                first_result = formatted_results[0]
                location = LocationSearch(
                    user=request.user.username,
                    location_name=first_result['name'],
                    latitude=first_result['latitude'],
                    longitude=first_result['longitude'],
                    search_query=query,
                    additional_data={
                        'result_count': len(formatted_results)
                    }
                )
                location.save()
            
            return Response(formatted_results)
            
        except Exception as e:
            logger.error(f"Error in location search: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LocationHistoryView(APIView):
    """
    API view for retrieving location search history
    GET: Retrieve location search history
    """
    permission_classes = [AllowAny]  # Temporarily set to AllowAny for demo
    
    def get(self, request):
        try:
            # Check if MongoDB is available
            if not getattr(settings, 'MONGODB_AVAILABLE', False):
                return Response({"history": [], "message": "MongoDB is not available, history cannot be retrieved"})
            
            # Get user from request
            user = request.user.username if request.user.is_authenticated else None
            
            # Get location history
            if user:
                locations = LocationSearch.objects(user=user).order_by('-timestamp').limit(50)
            else:
                # For demo purposes, return all locations if not authenticated
                locations = LocationSearch.objects.order_by('-timestamp').limit(50)
            
            # Format the results
            formatted_results = []
            for location in locations:
                formatted_results.append({
                    'id': str(location.id),
                    'location_name': location.location_name,
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'timestamp': location.timestamp.isoformat(),
                    'search_query': location.search_query
                })
            
            return Response({"history": formatted_results})
            
        except Exception as e:
            logger.error(f"Error retrieving location history: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ExportLocationCSVView(APIView):
    """
    API view for exporting location search history as CSV
    GET: Export location search history as CSV
    """
    permission_classes = [AllowAny]  # Temporarily set to AllowAny for demo
    
    def get(self, request):
        try:
            # Check if MongoDB is available
            if not getattr(settings, 'MONGODB_AVAILABLE', False):
                return Response(
                    {"error": "MongoDB is not available, CSV export cannot be performed"}, 
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Get user from request
            user = request.user.username if request.user.is_authenticated else None
            
            # Get location history
            if user:
                locations = LocationSearch.objects(user=user).order_by('-timestamp')
            else:
                # For demo purposes, return all locations if not authenticated
                locations = LocationSearch.objects.order_by('-timestamp')
            
            # Create CSV response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="location_history.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['ID', 'User', 'Location Name', 'Latitude', 'Longitude', 'Search Query', 'Timestamp'])
            
            for location in locations:
                writer.writerow([
                    str(location.id),
                    location.user,
                    location.location_name,
                    location.latitude,
                    location.longitude,
                    location.search_query,
                    location.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                ])
            
            return response
            
        except Exception as e:
            logger.error(f"Error exporting location history: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

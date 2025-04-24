"""
URL patterns for Smart Irrigation System core app
"""
from django.urls import path
from .views import (
    IrrigationDecisionView, 
    IrrigationHistoryView,
    ExportHistoryCSVView,
    CropSoilDataView
)
from .location_views import (
    LocationSearchView,
    LocationHistoryView,
    ExportLocationCSVView
)

urlpatterns = [
    path('irrigation/decision/', IrrigationDecisionView.as_view(), name='irrigation_decision'),
    path('irrigation/history/', IrrigationHistoryView.as_view(), name='irrigation_history'),
    path('irrigation/export-csv/', ExportHistoryCSVView.as_view(), name='export_history_csv'),
    path('crops/', CropSoilDataView.as_view(), name='crop_soil_data'),
    
    # Location search endpoints
    path('locations/search/', LocationSearchView.as_view(), name='location_search'),
    path('locations/history/', LocationHistoryView.as_view(), name='location_history'),
    path('locations/export-csv/', ExportLocationCSVView.as_view(), name='export_location_csv'),
]

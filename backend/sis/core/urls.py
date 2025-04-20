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

urlpatterns = [
    path('irrigation/decision/', IrrigationDecisionView.as_view(), name='irrigation_decision'),
    path('irrigation/history/', IrrigationHistoryView.as_view(), name='irrigation_history'),
    path('irrigation/export-csv/', ExportHistoryCSVView.as_view(), name='export_history_csv'),
    path('crops/', CropSoilDataView.as_view(), name='crop_soil_data'),
]

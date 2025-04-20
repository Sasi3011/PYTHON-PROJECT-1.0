"""
Admin configuration for Smart Irrigation System
"""
from django.contrib import admin
from django import forms

# Temporary implementation without MongoDB
class CropAdmin(admin.ModelAdmin):
    """Admin interface for Crop model"""
    list_display = ('name',)

class SoilAdmin(admin.ModelAdmin):
    """Admin interface for Soil model"""
    list_display = ('name',)

class IrrigationLogAdmin(admin.ModelAdmin):
    """Admin interface for IrrigationLog model (read-only)"""
    list_display = ('timestamp', 'user', 'crop_type', 'soil_type')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

# Register models with admin site
# Commented out until MongoDB is configured
# admin.site.register(Crop, CropAdmin)
# admin.site.register(Soil, SoilAdmin)
# admin.site.register(IrrigationLog, IrrigationLogAdmin)

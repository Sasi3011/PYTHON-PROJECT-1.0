"""
Crop and Soil Database for Smart Irrigation System
Provides initial data and functions to populate the database with crop and soil information
"""
import logging
from ..models import Crop, Soil

logger = logging.getLogger(__name__)

# Default crop data
DEFAULT_CROPS = {
    "turmeric": {
        "ideal_moisture": [65, 75],
        "ideal_temp": [25, 30],
        "base_water_lph": 1.2
    },
    "tomato": {
        "ideal_moisture": [60, 70],
        "ideal_temp": [20, 28],
        "base_water_lph": 0.9
    },
    "potato": {
        "ideal_moisture": [55, 65],
        "ideal_temp": [18, 24],
        "base_water_lph": 0.8
    },
    "rice": {
        "ideal_moisture": [80, 90],
        "ideal_temp": [24, 32],
        "base_water_lph": 1.5
    },
    "wheat": {
        "ideal_moisture": [50, 60],
        "ideal_temp": [15, 25],
        "base_water_lph": 0.7
    },
    "cotton": {
        "ideal_moisture": [55, 65],
        "ideal_temp": [22, 30],
        "base_water_lph": 1.0
    },
    "sugarcane": {
        "ideal_moisture": [70, 80],
        "ideal_temp": [25, 35],
        "base_water_lph": 1.4
    },
    "maize": {
        "ideal_moisture": [60, 70],
        "ideal_temp": [20, 30],
        "base_water_lph": 1.1
    }
}

# Default soil data
DEFAULT_SOILS = {
    "Red Soil": {
        "absorption_rate": 0.8
    },
    "Black Soil": {
        "absorption_rate": 0.7
    },
    "Alluvial Soil": {
        "absorption_rate": 0.9
    },
    "Laterite Soil": {
        "absorption_rate": 0.6
    },
    "Sandy Soil": {
        "absorption_rate": 0.5
    },
    "Loamy Soil": {
        "absorption_rate": 0.85
    },
    "Clay Soil": {
        "absorption_rate": 0.65
    },
    "Silt Soil": {
        "absorption_rate": 0.75
    }
}

def populate_default_data():
    """
    Populates the database with default crop and soil data if they don't exist
    
    Returns:
        tuple: (crops_added, soils_added) - Number of crops and soils added
    """
    crops_added = 0
    soils_added = 0
    
    try:
        # Add default crops if they don't exist
        for crop_name, crop_data in DEFAULT_CROPS.items():
            if not Crop.objects(name=crop_name).first():
                crop = Crop(
                    name=crop_name,
                    ideal_moisture=crop_data["ideal_moisture"],
                    ideal_temp=crop_data["ideal_temp"],
                    base_water_lph=crop_data["base_water_lph"]
                )
                crop.save()
                crops_added += 1
                logger.info(f"Added crop: {crop_name}")
        
        # Add default soils if they don't exist
        for soil_name, soil_data in DEFAULT_SOILS.items():
            if not Soil.objects(name=soil_name).first():
                soil = Soil(
                    name=soil_name,
                    absorption_rate=soil_data["absorption_rate"]
                )
                soil.save()
                soils_added += 1
                logger.info(f"Added soil: {soil_name}")
        
        logger.info(f"Database populated with {crops_added} crops and {soils_added} soils")
        return crops_added, soils_added
        
    except Exception as e:
        logger.error(f"Error populating database: {str(e)}")
        return 0, 0

def get_crop_data(crop_name):
    """
    Gets crop data from the database
    
    Args:
        crop_name (str): Name of the crop
        
    Returns:
        dict: Crop data or None if not found
    """
    try:
        crop = Crop.objects(name=crop_name).first()
        if crop:
            return {
                "name": crop.name,
                "ideal_moisture": crop.ideal_moisture,
                "ideal_temp": crop.ideal_temp,
                "base_water_lph": crop.base_water_lph
            }
        return None
    except Exception as e:
        logger.error(f"Error getting crop data: {str(e)}")
        return None

def get_soil_data(soil_name):
    """
    Gets soil data from the database
    
    Args:
        soil_name (str): Name of the soil
        
    Returns:
        dict: Soil data or None if not found
    """
    try:
        soil = Soil.objects(name=soil_name).first()
        if soil:
            return {
                "name": soil.name,
                "absorption_rate": soil.absorption_rate
            }
        return None
    except Exception as e:
        logger.error(f"Error getting soil data: {str(e)}")
        return None

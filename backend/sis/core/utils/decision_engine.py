"""
Decision Engine for Smart Irrigation System
Implements rule-based AI logic to calculate optimal water requirements and irrigation duration
"""
import logging

logger = logging.getLogger(__name__)

def calculate_irrigation_decision(crop_data, soil_data, sensor_data, weather_data):
    """
    Calculates irrigation decision based on crop, soil, sensor, and weather data
    
    Args:
        crop_data (dict): Crop information
            - name: Crop name
            - ideal_moisture: [min, max] percentage
            - ideal_temp: [min, max] celsius
            - base_water_lph: Base water need in liters per hour
        soil_data (dict): Soil information
            - name: Soil name
            - absorption_rate: Absorption coefficient (0-1)
        sensor_data (dict): Sensor readings
            - soil_moisture: Current soil moisture percentage
            - temperature: Current temperature in Celsius
            - humidity: Current humidity percentage
        weather_data (dict): Weather information
            - temperature: Current temperature in Celsius
            - humidity: Current humidity percentage
            - rain_probability: Probability of rain percentage
            
    Returns:
        dict: Irrigation decision
            - water_amount: Water amount in liters per hour
            - duration: Irrigation duration in hours
            - status: Status of irrigation (Active, Pending, etc.)
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
        
        # Rule 1: If soil moisture < crop's ideal minimum, increase water by 20%
        if current_moisture < ideal_moisture_min:
            moisture_deficit = (ideal_moisture_min - current_moisture) / ideal_moisture_min
            increase_factor = 1.0 + min(moisture_deficit, 0.5)  # Cap at 50% increase
            water_amount *= increase_factor
            logger.debug(f"Rule 1: Increased water by {(increase_factor-1)*100:.1f}% due to low moisture")
        
        # Rule 2: If soil moisture > crop's ideal maximum, reduce water by 20%
        elif current_moisture > ideal_moisture_max:
            moisture_excess = (current_moisture - ideal_moisture_max) / ideal_moisture_max
            decrease_factor = max(0.5, 1.0 - moisture_excess)  # Cap at 50% decrease
            water_amount *= decrease_factor
            logger.debug(f"Rule 2: Decreased water by {(1-decrease_factor)*100:.1f}% due to high moisture")
        
        # Rule 3: If temperature > crop's ideal maximum, increase water by 10%
        if current_temp > ideal_temp_max:
            temp_excess = min((current_temp - ideal_temp_max) / 10, 0.3)  # Cap at 30% increase
            water_amount *= (1.0 + temp_excess)
            logger.debug(f"Rule 3: Increased water by {temp_excess*100:.1f}% due to high temperature")
        
        # Rule 4: If rain probability > 60%, reduce water by 50%
        if rain_probability > 60.0:
            water_amount *= 0.5
            logger.debug(f"Rule 4: Decreased water by 50% due to high rain probability ({rain_probability}%)")
        
        # Rule 5: Adjust water based on soil absorption rate
        water_amount /= soil_absorption  # Lower absorption rate means more water needed
        logger.debug(f"Rule 5: Adjusted water by soil absorption rate ({soil_absorption})")
        
        # Calculate irrigation duration (hours)
        # Base duration is 2 hours, adjusted by soil moisture deficit
        moisture_deficit_percent = max(0, (ideal_moisture_min - current_moisture) / ideal_moisture_min)
        duration = 2.0 * (1.0 + moisture_deficit_percent)
        
        # Cap duration between 0.5 and 4 hours
        duration = max(0.5, min(duration, 4.0))
        
        # Round values for readability
        water_amount = round(water_amount, 2)
        duration = round(duration, 1)
        
        # Determine irrigation status
        if rain_probability > 80.0:
            status = "Pending"  # Pending due to high rain probability
        elif current_moisture > ideal_moisture_max * 1.2:
            status = "Cancelled"  # Cancel if soil is already very wet
        else:
            status = "Active"
        
        # Create decision dictionary
        decision = {
            'water_amount': water_amount,
            'duration': duration,
            'status': status
        }
        
        logger.debug(f"Irrigation decision: {decision}")
        return decision
        
    except Exception as e:
        logger.error(f"Error calculating irrigation decision: {str(e)}")
        # Return fallback decision if calculation fails
        return {
            'water_amount': 1.0,
            'duration': 2.0,
            'status': 'Pending'
        }

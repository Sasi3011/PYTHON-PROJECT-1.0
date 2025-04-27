"""
Script to view API data from the Smart Irrigation System
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"

def get_api_data(endpoint):
    """Get data from an API endpoint"""
    url = f"{BASE_URL}/{endpoint}/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error accessing {url}: {e}")
        return None

def print_formatted_data(data, title):
    """Print data in a formatted way"""
    print(f"\n=== {title} ===")
    print(json.dumps(data, indent=2))
    print("=" * (len(title) + 8))

def main():
    """Main function"""
    # Get irrigation history
    history_data = get_api_data("irrigation/history")
    if history_data:
        print_formatted_data(history_data, "IRRIGATION HISTORY")
    
    # Get crop data
    crop_data = get_api_data("crops")
    if crop_data:
        print_formatted_data(crop_data, "CROP DATA")
    
    # Get location history
    location_data = get_api_data("locations/history")
    if location_data:
        print_formatted_data(location_data, "LOCATION HISTORY")

if __name__ == "__main__":
    main()

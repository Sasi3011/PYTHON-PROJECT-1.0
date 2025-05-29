# Smart Irrigation System - Technical Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Phase 1: Core System Implementation](#phase-1-core-system-implementation)
4. [Phase 2: Map Search and MongoDB Integration](#phase-2-map-search-and-mongodb-integration)
5. [API Documentation](#api-documentation)
6. [Frontend Components](#frontend-components)
7. [Database Schema](#database-schema)
8. [Installation and Setup](#installation-and-setup)
9. [Usage Guide](#usage-guide)
10. [Future Enhancements](#future-enhancements)

## Project Overview

The Smart Irrigation System is an intelligent application designed to optimize water usage in agricultural settings. It combines real-time weather data, soil conditions, crop requirements, and geographical information to provide precise irrigation recommendations. The system helps farmers make data-driven decisions about when and how much to irrigate their fields, leading to water conservation and improved crop yields.

### Key Features
- Crop-specific irrigation recommendations
- Soil type analysis and consideration
- Weather data integration
- Location-based customization
- Historical data tracking and visualization
- Map-based location selection with search functionality
- MongoDB storage for data persistence

## System Architecture

The Smart Irrigation System follows a client-server architecture with the following components:

### Backend
- **Framework**: Django (Python)
- **REST API**: Django REST Framework
- **Primary Database**: SQLite (for Django models)
- **Secondary Database**: MongoDB (for location data and search history)
- **Weather Data**: Integration with OpenWeatherMap API
- **Geocoding**: Integration with OpenStreetMap Nominatim API

### Frontend
- **Interface**: HTML, CSS (TailwindCSS), JavaScript
- **Map Visualization**: Leaflet.js
- **Data Visualization**: Chart.js
- **HTTP Client**: Axios

### Data Flow
1. User inputs crop type, soil type, and location
2. Backend retrieves weather data for the location
3. Decision engine calculates optimal irrigation parameters
4. Results are displayed to the user and stored in the database
5. Historical data is visualized through charts and tables

## Phase 1: Core System Implementation

### 1.1 Backend Development

#### 1.1.1 Django Project Setup
- Created Django project structure
- Configured settings and environment variables
- Set up URL routing and views

#### 1.1.2 Core Models
- Implemented models for crops, soils, and irrigation data
- Created data structures for sensor and weather information
- Established relationships between models

#### 1.1.3 API Development
- Developed RESTful API endpoints using Django REST Framework
- Implemented serializers for data transformation
- Created views for handling HTTP requests

#### 1.1.4 Decision Engine
- Developed algorithm for irrigation recommendations
- Integrated weather data processing
- Implemented soil moisture and crop water requirement calculations

#### 1.1.5 Data Storage
- Set up SQLite database for Django models
- Implemented data persistence for irrigation history

### 1.2 Frontend Development

#### 1.2.1 User Interface
- Designed responsive UI with TailwindCSS
- Created form components for user input
- Implemented result visualization

#### 1.2.2 Map Integration
- Integrated Leaflet.js for map display
- Implemented location selection via map clicking
- Added coordinate display and input

#### 1.2.3 Data Visualization
- Integrated Chart.js for historical data visualization
- Created dynamic charts for irrigation history
- Implemented data tables for detailed information

#### 1.2.4 API Integration
- Set up Axios for API communication
- Implemented data fetching and submission
- Added error handling and loading states

## Phase 2: Map Search and MongoDB Integration

### 2.1 MongoDB Integration

#### 2.1.1 MongoDB Setup
- Configured MongoDB connection in Django settings
- Installed required packages (mongoengine, pymongo)
- Implemented connection error handling

#### 2.1.2 MongoDB Models
- Created `LocationSearch` model for storing search data
- Defined fields for location name, coordinates, timestamp, and user
- Implemented indexes for efficient querying

#### 2.1.3 Data Migration Strategy
- Designed approach for handling both SQLite and MongoDB
- Implemented fallback mechanisms when MongoDB is unavailable
- Created in-memory storage for testing purposes

### 2.2 Location Search Functionality

#### 2.2.1 Backend API Endpoints
- Created `/api/locations/search/` endpoint for geocoding queries
- Implemented `/api/locations/history/` for retrieving search history
- Added `/api/locations/export-csv/` for data export

#### 2.2.2 Geocoding Integration
- Integrated OpenStreetMap Nominatim API for geocoding
- Implemented search query processing
- Added result formatting and error handling

#### 2.2.3 Search History Storage
- Implemented saving search results to MongoDB
- Added user association with search history
- Created timestamp tracking for historical data

### 2.3 Frontend Enhancements

#### 2.3.1 Search Bar Implementation
- Added search input and button to the map section
- Styled components to match existing UI
- Implemented responsive design for all screen sizes

#### 2.3.2 Search Results Display
- Created dropdown for displaying search results
- Implemented result selection functionality
- Added coordinate display in results

#### 2.3.3 Map Integration
- Enhanced map to center on selected search results
- Added markers for selected locations
- Implemented smooth transitions between locations

#### 2.3.4 Event Handling
- Added click events for search result selection
- Implemented form field population with selected coordinates
- Created keyboard shortcuts for search submission

## API Documentation

### Authentication Endpoints
- `POST /api-auth/login/`: User login
- `POST /api-auth/logout/`: User logout
- `GET /api-auth/user/`: Get current user information

### Core Endpoints
- `GET /api/crops/`: Get available crops and soil types
- `POST /api/irrigation/decision/`: Submit parameters and get irrigation decision
- `GET /api/irrigation/history/`: Get irrigation history
- `GET /api/irrigation/export-csv/`: Export irrigation history as CSV

### Location Endpoints
- `GET /api/locations/search/?q={query}`: Search for locations
- `GET /api/locations/history/`: Get location search history
- `GET /api/locations/export-csv/`: Export location history as CSV
- `GET /api/locations/details/{location_id}/`: Get details for a specific location

### Request/Response Examples

#### Location Search Request
```
GET /api/locations/search/?q=Chennai
```

#### Location Search Response
```json
[
  {
    "name": "Chennai, Chennai District, Tamil Nadu, India",
    "latitude": 13.0836939,
    "longitude": 80.270186,
    "type": "city",
    "address": {
      "city": "Chennai",
      "state": "Tamil Nadu",
      "country": "India"
    }
  },
  {
    "name": "Chennai Central, Park Town, Chennai, Chennai District, Tamil Nadu, India",
    "latitude": 13.0836,
    "longitude": 80.2781,
    "type": "railway_station",
    "address": {
      "city": "Chennai",
      "state": "Tamil Nadu",
      "country": "India"
    }
  }
]
```

## Frontend Components

### Map Component
The map component allows users to select a location either by clicking directly on the map or by searching for a place name. It uses Leaflet.js for rendering the map and OpenStreetMap for the map tiles.

```javascript
// Map initialization
const map = L.map('map').setView([20.5937, 78.9629], 5);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);
```

### Search Component
The search component allows users to find locations by name. It sends requests to the backend API, which uses the OpenStreetMap Nominatim service for geocoding.

```javascript
// Search functionality
async function searchLocations() {
  const query = searchInput.value.trim();
  if (!query) return;
  
  try {
    const response = await axios.get(`${API_BASE_URL}/locations/search/?q=${encodeURIComponent(query)}`);
    // Process and display results
  } catch (error) {
    console.error('Error searching for locations:', error);
  }
}
```

### Form Component
The form component collects user input for crop type, soil type, and location coordinates. It validates the input and submits it to the backend for processing.

### Results Display
The results component shows the irrigation recommendation, including water amount, duration, and status. It also displays additional information such as weather conditions and soil moisture.

### History Visualization
The history visualization component shows past irrigation decisions in both chart and table formats. It allows users to track patterns and trends over time.

## Database Schema

### MongoDB Collections

#### Location Searches Collection
```
{
  "_id": ObjectId,
  "user": String,
  "location_name": String,
  "latitude": Float,
  "longitude": Float,
  "timestamp": DateTime,
  "search_query": String,
  "additional_data": {
    "result_count": Integer
  }
}
```

### Django Models

#### Crop Model
```python
class Crop(Document):
    name = fields.StringField(required=True, unique=True)
    ideal_moisture = fields.ListField(fields.FloatField(), required=True)
    ideal_temp = fields.ListField(fields.FloatField(), required=True)
    base_water_lph = fields.FloatField(required=True)
```

#### Soil Model
```python
class Soil(Document):
    name = fields.StringField(required=True, unique=True)
    absorption_rate = fields.FloatField(required=True)
```

#### Irrigation Log Model
```python
class IrrigationLog(Document):
    timestamp = fields.DateTimeField(default=datetime.datetime.utcnow)
    user = fields.StringField(required=True)
    crop_type = fields.StringField(required=True)
    soil_type = fields.StringField(required=True)
    latitude = fields.FloatField(required=True)
    longitude = fields.FloatField(required=True)
    sensor_data = fields.EmbeddedDocumentField(SensorData, required=True)
    weather_data = fields.EmbeddedDocumentField(WeatherData, required=True)
    decision = fields.EmbeddedDocumentField(IrrigationDecision, required=True)
```

## Installation and Setup

### Prerequisites
- Python 3.8+
- MongoDB 4.4+
- Node.js 14+ (for development)

### Backend Setup
1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/smart-irrigation-system.git
   cd smart-irrigation-system
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables
   ```bash
   cp backend/.env.template backend/.env
   # Edit .env file with your settings
   ```

5. Run migrations
   ```bash
   cd backend
   python manage.py migrate
   ```

6. Start the development server
   ```bash
   python manage.py runserver
   ```

### Frontend Setup
1. Open the frontend in a web browser
   ```bash
   ./start_frontend.bat  # On Windows
   # Or manually open frontend/simple.html in your browser
   ```

## Usage Guide

### Basic Usage
1. Open the application in your web browser
2. Select a crop type from the dropdown menu
3. Select a soil type from the dropdown menu
4. Specify a location using one of these methods:
   - Click directly on the map
   - Enter coordinates manually
   - Search for a location by name
5. Click "Calculate Irrigation" to get recommendations
6. View the results in the decision display panel
7. Check historical data in the charts and tables below

### Using the Location Search
1. Enter a place name in the search box
2. Click the "Search" button or press Enter
3. Select a result from the dropdown list
4. The map will center on the selected location
5. The latitude and longitude fields will be automatically filled

### Viewing History
1. Scroll down to the "Irrigation History" section
2. View the chart for a visual representation of past decisions
3. Check the table for detailed information about each decision
4. Click "Export CSV" to download the history as a CSV file

## Future Enhancements

### Planned Features
1. **Mobile Application**: Develop a native mobile app for Android and iOS
2. **IoT Integration**: Connect with soil moisture sensors and automated irrigation systems
3. **Advanced Analytics**: Implement machine learning for predictive irrigation scheduling
4. **User Profiles**: Add support for multiple farms and fields per user
5. **Offline Mode**: Enable functionality when internet connection is limited
6. **Notification System**: Alert users about optimal irrigation times
7. **Water Conservation Metrics**: Track water savings over time

### Technical Improvements
1. **Real-time Updates**: Implement WebSockets for live data updates
2. **Performance Optimization**: Enhance database queries and frontend rendering
3. **Security Enhancements**: Add OAuth 2.0 authentication and role-based access control
4. **Scalability**: Migrate to a more scalable database solution for production
5. **Internationalization**: Add support for multiple languages
6. **Accessibility**: Improve compliance with WCAG guidelines

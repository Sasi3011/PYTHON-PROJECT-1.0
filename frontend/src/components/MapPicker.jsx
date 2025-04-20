import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';

// LocationMarker component to handle map clicks and marker position
const LocationMarker = ({ onLocationSelect }) => {
  const [position, setPosition] = useState(null);
  
  const map = useMapEvents({
    click(e) {
      const { lat, lng } = e.latlng;
      setPosition([lat, lng]);
      onLocationSelect(lat, lng);
    }
  });

  return position === null ? null : (
    <Marker position={position} />
  );
};

const MapPicker = ({ onLocationSelect }) => {
  const [defaultPosition, setDefaultPosition] = useState([20.5937, 78.9629]); // Default to center of India
  
  // Try to get user's location if available
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          setDefaultPosition([latitude, longitude]);
        },
        (error) => {
          console.error("Error getting location:", error);
        }
      );
    }
  }, []);

  return (
    <div className="border rounded-lg overflow-hidden">
      <MapContainer center={defaultPosition} zoom={5} scrollWheelZoom={true}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <LocationMarker onLocationSelect={onLocationSelect} />
      </MapContainer>
      <div className="bg-gray-100 p-2 text-xs text-gray-600">
        Click on the map to select a location for your field
      </div>
    </div>
  );
};

export default MapPicker;

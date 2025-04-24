import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default marker icon in Leaflet with React
const defaultIcon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

L.Marker.prototype.options.icon = defaultIcon;

const MapSearch = ({ onLocationSelect }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [mapCenter, setMapCenter] = useState([20.5937, 78.9629]); // Default to center of India
  const [mapZoom, setMapZoom] = useState(5);
  const [searchHistory, setSearchHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch search history on component mount
  useEffect(() => {
    fetchSearchHistory();
  }, []);

  const fetchSearchHistory = async () => {
    try {
      const response = await axios.get('/api/locations/history/');
      setSearchHistory(response.data.history || []);
    } catch (error) {
      console.error('Error fetching search history:', error);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(`/api/locations/search/?q=${encodeURIComponent(searchQuery)}`);
      setSearchResults(response.data);
      
      if (response.data.length > 0) {
        const firstResult = response.data[0];
        handleLocationSelect(firstResult);
        
        // Refresh search history after a successful search
        fetchSearchHistory();
      } else {
        setError('No results found for your search query');
      }
    } catch (error) {
      console.error('Error searching for location:', error);
      setError('Error searching for location. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLocationSelect = (location) => {
    setSelectedLocation(location);
    setMapCenter([location.latitude, location.longitude]);
    setMapZoom(13);
    
    // If there's an external handler, call it
    if (onLocationSelect) {
      onLocationSelect(location.latitude, location.longitude);
    }
  };

  const handleHistoryItemClick = (historyItem) => {
    setSelectedLocation({
      name: historyItem.location_name,
      latitude: historyItem.latitude,
      longitude: historyItem.longitude
    });
    setMapCenter([historyItem.latitude, historyItem.longitude]);
    setMapZoom(13);
    
    // If there's an external handler, call it
    if (onLocationSelect) {
      onLocationSelect(historyItem.latitude, historyItem.longitude);
    }
  };

  const exportToCsv = async () => {
    try {
      window.open('/api/locations/export-csv/', '_blank');
    } catch (error) {
      console.error('Error exporting to CSV:', error);
      setError('Error exporting to CSV. Please try again.');
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Location Search</h2>
      
      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search for a location..."
            className="flex-grow px-4 py-2 border border-gray-300 rounded-l focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <button
            type="submit"
            className="bg-primary-600 text-white px-4 py-2 rounded-r hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
            disabled={loading}
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
        {error && (
          <div className="mt-2 text-red-500">{error}</div>
        )}
      </form>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Search Results */}
        <div className="md:col-span-1">
          <h3 className="text-lg font-medium text-gray-800 mb-3">Search Results</h3>
          <div className="max-h-96 overflow-y-auto">
            {searchResults.length > 0 ? (
              <ul className="divide-y divide-gray-200">
                {searchResults.map((result, index) => (
                  <li 
                    key={index} 
                    className="py-2 cursor-pointer hover:bg-gray-50"
                    onClick={() => handleLocationSelect(result)}
                  >
                    <div className="font-medium">{result.name}</div>
                    <div className="text-sm text-gray-500">
                      Lat: {result.latitude.toFixed(6)}, Lng: {result.longitude.toFixed(6)}
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="text-gray-500">No results to display</div>
            )}
          </div>
        </div>

        {/* Map */}
        <div className="md:col-span-2">
          <div className="h-96 rounded-lg overflow-hidden border border-gray-300">
            <MapContainer 
              center={mapCenter} 
              zoom={mapZoom} 
              style={{ height: '100%', width: '100%' }}
              key={`${mapCenter[0]}-${mapCenter[1]}-${mapZoom}`} // Force re-render when center/zoom changes
            >
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              />
              {selectedLocation && (
                <Marker position={[selectedLocation.latitude, selectedLocation.longitude]}>
                  <Popup>
                    <div>
                      <h3 className="font-medium">{selectedLocation.name}</h3>
                      <p className="text-sm">
                        Latitude: {selectedLocation.latitude.toFixed(6)}<br />
                        Longitude: {selectedLocation.longitude.toFixed(6)}
                      </p>
                    </div>
                  </Popup>
                </Marker>
              )}
            </MapContainer>
          </div>
        </div>
      </div>

      {/* Search History */}
      <div className="mt-8">
        <div className="flex justify-between items-center mb-3">
          <h3 className="text-lg font-medium text-gray-800">Search History</h3>
          <button
            onClick={exportToCsv}
            className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            Export to CSV
          </button>
        </div>
        <div className="max-h-64 overflow-y-auto">
          {searchHistory.length > 0 ? (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Location</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Coordinates</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {searchHistory.map((item) => (
                  <tr 
                    key={item.id} 
                    className="cursor-pointer hover:bg-gray-50"
                    onClick={() => handleHistoryItemClick(item)}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{item.location_name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">
                        {item.latitude.toFixed(6)}, {item.longitude.toFixed(6)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">
                        {new Date(item.timestamp).toLocaleString()}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="text-gray-500 p-4 text-center">No search history available</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MapSearch;

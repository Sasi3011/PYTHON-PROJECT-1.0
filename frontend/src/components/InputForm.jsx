import React, { useState } from 'react';
import MapPicker from './MapPicker';

const InputForm = ({ onSubmit, crops, soils }) => {
  const [formData, setFormData] = useState({
    crop_type: '',
    soil_type: '',
    latitude: '',
    longitude: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showMap, setShowMap] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleLocationSelect = (lat, lng) => {
    setFormData(prev => ({
      ...prev,
      latitude: lat.toFixed(6),
      longitude: lng.toFixed(6)
    }));
    setShowMap(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    // Validate form
    if (!formData.crop_type) {
      setError('Please select a crop type');
      return;
    }
    if (!formData.soil_type) {
      setError('Please select a soil type');
      return;
    }
    if (!formData.latitude || !formData.longitude) {
      setError('Please select a location');
      return;
    }

    try {
      setLoading(true);
      const result = await onSubmit(formData);
      if (result?.error) {
        setError(result.error);
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-6">Irrigation Parameters</h2>
      
      {error && (
        <div className="bg-red-50 text-red-700 p-3 rounded-md mb-4 text-sm">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="crop_type" className="form-label">Crop Type</label>
          <select
            id="crop_type"
            name="crop_type"
            value={formData.crop_type}
            onChange={handleChange}
            className="input-field"
            disabled={loading}
          >
            <option value="">Select Crop Type</option>
            {crops.map(crop => (
              <option key={crop.name} value={crop.name}>
                {crop.name.charAt(0).toUpperCase() + crop.name.slice(1)}
              </option>
            ))}
          </select>
        </div>
        
        <div className="form-group">
          <label htmlFor="soil_type" className="form-label">Soil Type</label>
          <select
            id="soil_type"
            name="soil_type"
            value={formData.soil_type}
            onChange={handleChange}
            className="input-field"
            disabled={loading}
          >
            <option value="">Select Soil Type</option>
            {soils.map(soil => (
              <option key={soil.name} value={soil.name}>
                {soil.name}
              </option>
            ))}
          </select>
        </div>
        
        <div className="form-group">
          <label className="form-label">Location</label>
          <div className="flex space-x-2">
            <input
              type="text"
              placeholder="Latitude"
              name="latitude"
              value={formData.latitude}
              onChange={handleChange}
              className="input-field w-1/2"
              disabled={loading}
            />
            <input
              type="text"
              placeholder="Longitude"
              name="longitude"
              value={formData.longitude}
              onChange={handleChange}
              className="input-field w-1/2"
              disabled={loading}
            />
          </div>
          <button
            type="button"
            onClick={() => setShowMap(!showMap)}
            className="mt-2 text-sm text-primary-600 hover:text-primary-800"
          >
            {showMap ? 'Hide Map' : 'Pick Location on Map'}
          </button>
        </div>
        
        {showMap && (
          <div className="mb-4">
            <MapPicker onLocationSelect={handleLocationSelect} />
          </div>
        )}
        
        <button
          type="submit"
          className="btn-primary w-full mt-4"
          disabled={loading}
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </span>
          ) : 'Calculate Irrigation'}
        </button>
      </form>
    </div>
  );
};

export default InputForm;

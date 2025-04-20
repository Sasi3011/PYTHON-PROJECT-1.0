import React from 'react';

const DecisionDisplay = ({ data }) => {
  if (!data) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 h-full flex items-center justify-center">
        <div className="text-center text-gray-500">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <p className="mt-4">Submit irrigation parameters to see results</p>
        </div>
      </div>
    );
  }

  const { sensor_data, weather_data, decision, timestamp } = data;
  
  // Format date
  const formattedDate = new Date(timestamp).toLocaleString();
  
  // Determine status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'Active':
        return 'bg-green-100 text-green-800';
      case 'Pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'Cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-6">Irrigation Decision</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {/* Sensor Data Card */}
        <div className="card bg-blue-50">
          <h3 className="text-lg font-medium text-blue-800 mb-3">Sensor Data</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Soil Moisture:</span>
              <span className="font-medium">{sensor_data.soil_moisture}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Temperature:</span>
              <span className="font-medium">{sensor_data.temperature}°C</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Humidity:</span>
              <span className="font-medium">{sensor_data.humidity}%</span>
            </div>
          </div>
        </div>
        
        {/* Weather Data Card */}
        <div className="card bg-purple-50">
          <h3 className="text-lg font-medium text-purple-800 mb-3">Weather Data</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Temperature:</span>
              <span className="font-medium">{weather_data.temperature}°C</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Humidity:</span>
              <span className="font-medium">{weather_data.humidity}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Rain Probability:</span>
              <span className="font-medium">{weather_data.rain_probability}%</span>
            </div>
          </div>
        </div>
        
        {/* Decision Card */}
        <div className="card bg-green-50">
          <h3 className="text-lg font-medium text-green-800 mb-3">Irrigation Plan</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Water Amount:</span>
              <span className="font-medium">{decision.water_amount} L/h</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Duration:</span>
              <span className="font-medium">{decision.duration} hours</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Status:</span>
              <span className={`font-medium px-2 py-1 rounded-full text-xs ${getStatusColor(decision.status)}`}>
                {decision.status}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Summary */}
      <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
        <div className="flex items-center mb-2">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-primary-600 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="text-md font-medium text-gray-800">Decision Summary</h3>
        </div>
        <p className="text-gray-600">
          {decision.status === 'Active' && (
            <>Irrigate with <span className="font-medium">{decision.water_amount} liters per hour</span> for <span className="font-medium">{decision.duration} hours</span>.</>
          )}
          {decision.status === 'Pending' && (
            <>Irrigation pending due to high rain probability. Recommended amount: <span className="font-medium">{decision.water_amount} liters per hour</span> for <span className="font-medium">{decision.duration} hours</span>.</>
          )}
          {decision.status === 'Cancelled' && (
            <>Irrigation not needed at this time. Soil moisture is sufficient.</>
          )}
        </p>
        <p className="text-xs text-gray-500 mt-2">
          Generated on {formattedDate}
        </p>
      </div>
    </div>
  );
};

export default DecisionDisplay;

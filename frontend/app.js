// Smart Irrigation System - Frontend Application
document.addEventListener('DOMContentLoaded', function() {
  // App state
  const state = {
    isAuthenticated: false,
    user: null,
    crops: [],
    soils: [],
    irrigationData: null,
    irrigationHistory: [],
    loading: {
      auth: false,
      crops: false,
      decision: false,
      history: false
    },
    errors: {
      auth: null,
      crops: null,
      decision: null,
      history: null
    },
    formData: {
      crop_type: '',
      soil_type: '',
      latitude: '',
      longitude: ''
    }
  };

  // API endpoints
  const API = {
    login: '/api-auth/login/',
    logout: '/api-auth/logout/',
    crops: '/api/crops/',
    decision: '/api/irrigation/decision/',
    history: '/api/irrigation/history/',
    exportCsv: '/api/irrigation/export-csv/'
  };

  // Initialize the application
  function init() {
    renderApp();
    fetchCropsAndSoils();
    fetchIrrigationHistory();
  }

  // Fetch crops and soils data
  function fetchCropsAndSoils() {
    state.loading.crops = true;
    renderApp();

    axios.get(API.crops)
      .then(response => {
        state.crops = response.data.crops;
        state.soils = response.data.soils;
        state.loading.crops = false;
        state.errors.crops = null;
      })
      .catch(error => {
        console.error('Error fetching crops and soils:', error);
        state.loading.crops = false;
        state.errors.crops = 'Failed to load crops and soils data';
      })
      .finally(() => {
        renderApp();
      });
  }

  // Fetch irrigation history
  function fetchIrrigationHistory() {
    state.loading.history = true;
    renderApp();

    axios.get(API.history)
      .then(response => {
        state.irrigationHistory = response.data.history;
        state.loading.history = false;
        state.errors.history = null;
      })
      .catch(error => {
        console.error('Error fetching irrigation history:', error);
        state.loading.history = false;
        state.errors.history = 'Failed to load irrigation history';
      })
      .finally(() => {
        renderApp();
        if (state.irrigationHistory.length > 0) {
          renderHistoryChart();
        }
      });
  }

  // Submit irrigation decision request
  function submitIrrigationDecision(event) {
    event.preventDefault();
    
    // Validate form
    if (!state.formData.crop_type) {
      state.errors.decision = 'Please select a crop type';
      renderApp();
      return;
    }
    if (!state.formData.soil_type) {
      state.errors.decision = 'Please select a soil type';
      renderApp();
      return;
    }
    if (!state.formData.latitude || !state.formData.longitude) {
      state.errors.decision = 'Please enter latitude and longitude';
      renderApp();
      return;
    }

    state.loading.decision = true;
    state.errors.decision = null;
    renderApp();

    axios.post(API.decision, state.formData)
      .then(response => {
        state.irrigationData = response.data;
        state.loading.decision = false;
        fetchIrrigationHistory(); // Refresh history after new decision
      })
      .catch(error => {
        console.error('Error submitting irrigation data:', error);
        state.loading.decision = false;
        state.errors.decision = error.response?.data?.error || 'An error occurred';
        renderApp();
      });
  }

  // Handle form input changes
  function handleInputChange(event) {
    const { name, value } = event.target;
    state.formData[name] = value;
    renderApp();
  }

  // Export history as CSV
  function exportCSV() {
    window.open(API.exportCsv, '_blank');
  }

  // Initialize map
  function initMap() {
    setTimeout(() => {
      const mapContainer = document.getElementById('map');
      if (!mapContainer) return;
      
      // Create map centered on India
      const map = L.map('map').setView([20.5937, 78.9629], 5);
      
      // Add tile layer
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      }).addTo(map);
      
      // Add click event to map
      map.on('click', function(e) {
        const { lat, lng } = e.latlng;
        
        // Update form data
        state.formData.latitude = lat.toFixed(6);
        state.formData.longitude = lng.toFixed(6);
        
        // Clear existing markers
        map.eachLayer(function(layer) {
          if (layer instanceof L.Marker) {
            map.removeLayer(layer);
          }
        });
        
        // Add marker at clicked location
        L.marker([lat, lng]).addTo(map);
        
        // Update UI
        renderApp();
      });
    }, 100);
  }

  // Render history chart
  function renderHistoryChart() {
    setTimeout(() => {
      const chartCanvas = document.getElementById('historyChart');
      if (!chartCanvas || state.irrigationHistory.length === 0) return;
      
      // Sort history by timestamp
      const sortedHistory = [...state.irrigationHistory].sort((a, b) => 
        new Date(a.timestamp) - new Date(b.timestamp)
      );
      
      // Prepare data for chart
      const labels = sortedHistory.map(item => {
        const date = new Date(item.timestamp);
        return date.toLocaleDateString();
      });
      
      const waterAmountData = sortedHistory.map(item => item.decision.water_amount);
      const soilMoistureData = sortedHistory.map(item => item.sensor_data.soil_moisture);
      const rainProbabilityData = sortedHistory.map(item => item.weather_data.rain_probability);
      
      // Create chart
      new Chart(chartCanvas, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Water Amount (L/h)',
              data: waterAmountData,
              borderColor: 'rgb(53, 162, 235)',
              backgroundColor: 'rgba(53, 162, 235, 0.5)',
              yAxisID: 'y'
            },
            {
              label: 'Soil Moisture (%)',
              data: soilMoistureData,
              borderColor: 'rgb(75, 192, 192)',
              backgroundColor: 'rgba(75, 192, 192, 0.5)',
              yAxisID: 'y1'
            },
            {
              label: 'Rain Probability (%)',
              data: rainProbabilityData,
              borderColor: 'rgb(255, 99, 132)',
              backgroundColor: 'rgba(255, 99, 132, 0.5)',
              yAxisID: 'y1'
            }
          ]
        },
        options: {
          responsive: true,
          interaction: {
            mode: 'index',
            intersect: false
          },
          scales: {
            y: {
              type: 'linear',
              display: true,
              position: 'left',
              title: {
                display: true,
                text: 'Water Amount (L/h)'
              },
              min: 0
            },
            y1: {
              type: 'linear',
              display: true,
              position: 'right',
              title: {
                display: true,
                text: 'Percentage (%)'
              },
              min: 0,
              max: 100,
              grid: {
                drawOnChartArea: false
              }
            }
          }
        }
      });
    }, 100);
  }

  // Format date
  function formatDate(dateString) {
    return new Date(dateString).toLocaleString();
  }

  // Render the application
  function renderApp() {
    const rootElement = document.getElementById('root');
    
    // Main app container
    rootElement.innerHTML = `
      <div class="min-h-screen bg-gray-50">
        <header class="bg-white shadow-sm">
          <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
            <h1 class="text-2xl font-bold text-primary-700">Smart Irrigation System</h1>
            <div class="flex items-center space-x-4">
              <span class="text-gray-600">Welcome, Guest</span>
            </div>
          </div>
        </header>

        <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div class="space-y-8">
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div class="lg:col-span-1">
                ${renderInputForm()}
              </div>
              <div class="lg:col-span-2">
                ${renderDecisionDisplay()}
              </div>
            </div>
            
            <div class="bg-white rounded-lg shadow-md p-6">
              <div class="flex justify-between items-center mb-6">
                <h2 class="text-xl font-semibold text-gray-800">Irrigation History</h2>
                <button 
                  onclick="window.appExportCSV()"
                  class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm flex items-center"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Export CSV
                </button>
              </div>
              
              <div class="mb-8">
                ${renderHistoryChartContainer()}
              </div>
              
              ${renderHistoryTable()}
            </div>
          </div>
        </main>

        <footer class="bg-white border-t border-gray-200 py-6">
          <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <p class="text-center text-gray-500 text-sm">
              &copy; ${new Date().getFullYear()} Smart Irrigation System. All rights reserved.
            </p>
          </div>
        </footer>
      </div>
    `;
    
    // Initialize map after rendering
    initMap();
  }

  // Render input form
  function renderInputForm() {
    return `
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-semibold text-gray-800 mb-6">Irrigation Parameters</h2>
        
        ${state.errors.decision ? `
          <div class="bg-red-50 text-red-700 p-3 rounded-md mb-4 text-sm">
            ${state.errors.decision}
          </div>
        ` : ''}
        
        <form id="irrigationForm">
          <div class="mb-4">
            <label for="crop_type" class="block text-sm font-medium text-gray-700 mb-1">Crop Type</label>
            <select
              id="crop_type"
              name="crop_type"
              value="${state.formData.crop_type}"
              onchange="window.appHandleInputChange(event)"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              ${state.loading.decision ? 'disabled' : ''}
            >
              <option value="">Select Crop Type</option>
              ${state.crops.map(crop => `
                <option value="${crop.name}" ${state.formData.crop_type === crop.name ? 'selected' : ''}>
                  ${crop.name.charAt(0).toUpperCase() + crop.name.slice(1)}
                </option>
              `).join('')}
            </select>
          </div>
          
          <div class="mb-4">
            <label for="soil_type" class="block text-sm font-medium text-gray-700 mb-1">Soil Type</label>
            <select
              id="soil_type"
              name="soil_type"
              value="${state.formData.soil_type}"
              onchange="window.appHandleInputChange(event)"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              ${state.loading.decision ? 'disabled' : ''}
            >
              <option value="">Select Soil Type</option>
              ${state.soils.map(soil => `
                <option value="${soil.name}" ${state.formData.soil_type === soil.name ? 'selected' : ''}>
                  ${soil.name}
                </option>
              `).join('')}
            </select>
          </div>
          
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Location</label>
            <div class="flex space-x-2">
              <input
                type="text"
                placeholder="Latitude"
                name="latitude"
                value="${state.formData.latitude}"
                onchange="window.appHandleInputChange(event)"
                class="w-1/2 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                ${state.loading.decision ? 'disabled' : ''}
              />
              <input
                type="text"
                placeholder="Longitude"
                name="longitude"
                value="${state.formData.longitude}"
                onchange="window.appHandleInputChange(event)"
                class="w-1/2 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                ${state.loading.decision ? 'disabled' : ''}
              />
            </div>
          </div>
          
          <div class="mb-4">
            <div id="map" style="height: 300px; width: 100%; border-radius: 0.5rem;"></div>
            <p class="text-xs text-gray-500 mt-1">Click on the map to select a location</p>
          </div>
          
          <button
            type="submit"
            onclick="window.appSubmitIrrigationDecision(event)"
            class="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-2 px-4 rounded-md transition-colors duration-300"
            ${state.loading.decision ? 'disabled' : ''}
          >
            ${state.loading.decision ? `
              <span class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </span>
            ` : 'Calculate Irrigation'}
          </button>
        </form>
      </div>
    `;
  }

  // Render decision display
  function renderDecisionDisplay() {
    if (!state.irrigationData) {
      return `
        <div class="bg-white rounded-lg shadow-md p-6 h-full flex items-center justify-center">
          <div class="text-center text-gray-500">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <p class="mt-4">Submit irrigation parameters to see results</p>
          </div>
        </div>
      `;
    }

    const { sensor_data, weather_data, decision, timestamp } = state.irrigationData;
    
    // Format date
    const formattedDate = formatDate(timestamp);
    
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

    return `
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-semibold text-gray-800 mb-6">Irrigation Decision</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <!-- Sensor Data Card -->
          <div class="bg-blue-50 rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-300">
            <h3 class="text-lg font-medium text-blue-800 mb-3">Sensor Data</h3>
            <div class="space-y-2">
              <div class="flex justify-between">
                <span class="text-gray-600">Soil Moisture:</span>
                <span class="font-medium">${sensor_data.soil_moisture}%</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Temperature:</span>
                <span class="font-medium">${sensor_data.temperature}°C</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Humidity:</span>
                <span class="font-medium">${sensor_data.humidity}%</span>
              </div>
            </div>
          </div>
          
          <!-- Weather Data Card -->
          <div class="bg-purple-50 rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-300">
            <h3 class="text-lg font-medium text-purple-800 mb-3">Weather Data</h3>
            <div class="space-y-2">
              <div class="flex justify-between">
                <span class="text-gray-600">Temperature:</span>
                <span class="font-medium">${weather_data.temperature}°C</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Humidity:</span>
                <span class="font-medium">${weather_data.humidity}%</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Rain Probability:</span>
                <span class="font-medium">${weather_data.rain_probability}%</span>
              </div>
            </div>
          </div>
          
          <!-- Decision Card -->
          <div class="bg-green-50 rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-300">
            <h3 class="text-lg font-medium text-green-800 mb-3">Irrigation Plan</h3>
            <div class="space-y-2">
              <div class="flex justify-between">
                <span class="text-gray-600">Water Amount:</span>
                <span class="font-medium">${decision.water_amount} L/h</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Duration:</span>
                <span class="font-medium">${decision.duration} hours</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Status:</span>
                <span class="font-medium px-2 py-1 rounded-full text-xs ${getStatusColor(decision.status)}">
                  ${decision.status}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Summary -->
        <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
          <div class="flex items-center mb-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary-600 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 class="text-md font-medium text-gray-800">Decision Summary</h3>
          </div>
          <p class="text-gray-600">
            ${decision.status === 'Active' ? `
              Irrigate with <span class="font-medium">${decision.water_amount} liters per hour</span> for <span class="font-medium">${decision.duration} hours</span>.
            ` : decision.status === 'Pending' ? `
              Irrigation pending due to high rain probability. Recommended amount: <span class="font-medium">${decision.water_amount} liters per hour</span> for <span class="font-medium">${decision.duration} hours</span>.
            ` : `
              Irrigation not needed at this time. Soil moisture is sufficient.
            `}
          </p>
          <p class="text-xs text-gray-500 mt-2">
            Generated on ${formattedDate}
          </p>
        </div>
      </div>
    `;
  }

  // Render history chart container
  function renderHistoryChartContainer() {
    if (state.loading.history) {
      return `
        <div class="flex items-center justify-center h-64 bg-gray-50 rounded-lg">
          <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
        </div>
      `;
    }
    
    if (state.errors.history) {
      return `
        <div class="bg-red-50 text-red-700 p-4 rounded-lg">
          ${state.errors.history}
        </div>
      `;
    }
    
    if (state.irrigationHistory.length === 0) {
      return `
        <div class="flex items-center justify-center h-64 bg-gray-50 rounded-lg">
          <p class="text-gray-500">No irrigation history available yet</p>
        </div>
      `;
    }
    
    return `
      <div class="chart-container bg-white p-4 rounded-lg border border-gray-200">
        <canvas id="historyChart"></canvas>
      </div>
    `;
  }

  // Render history table
  function renderHistoryTable() {
    if (state.loading.history) {
      return `
        <div class="flex items-center justify-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
        </div>
      `;
    }
    
    if (state.errors.history) {
      return `
        <div class="bg-red-50 text-red-700 p-4 rounded-lg">
          ${state.errors.history}
        </div>
      `;
    }
    
    if (state.irrigationHistory.length === 0) {
      return `
        <div class="text-center py-8 text-gray-500">
          <p>No irrigation history available yet.</p>
        </div>
      `;
    }

    // Get status color
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

    return `
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date & Time
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Crop & Soil
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Soil Moisture
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Weather
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Irrigation
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            ${state.irrigationHistory.map(item => `
              <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  ${formatDate(item.timestamp)}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">
                    ${item.crop_type.charAt(0).toUpperCase() + item.crop_type.slice(1)}
                  </div>
                  <div class="text-sm text-gray-500">${item.soil_type}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  ${item.sensor_data.soil_moisture}%
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">${item.weather_data.temperature}°C</div>
                  <div class="text-sm text-gray-500">
                    Rain: ${item.weather_data.rain_probability}%
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  ${item.decision.water_amount} L/h for ${item.decision.duration}h
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(item.decision.status)}">
                    ${item.decision.status}
                  </span>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  }

  // Expose functions to window for event handlers
  window.appHandleInputChange = handleInputChange;
  window.appSubmitIrrigationDecision = submitIrrigationDecision;
  window.appExportCSV = exportCSV;

  // Initialize the application
  init();
});

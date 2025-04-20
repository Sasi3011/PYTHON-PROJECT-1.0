import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import axios from 'axios';

// Components
import InputForm from './components/InputForm';
import DecisionDisplay from './components/DecisionDisplay';
import HistoryTable from './components/HistoryTable';
import HistoryChart from './components/HistoryChart';
import LoginForm from './components/LoginForm';

// Set up axios defaults
axios.defaults.withCredentials = true;

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [irrigationData, setIrrigationData] = useState(null);
  const [irrigationHistory, setIrrigationHistory] = useState([]);
  const [crops, setCrops] = useState([]);
  const [soils, setSoils] = useState([]);
  const navigate = useNavigate();

  // Check authentication status on load
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await axios.get('/api-auth/user/');
        if (response.data.username) {
          setIsAuthenticated(true);
          setUser(response.data);
        }
      } catch (error) {
        console.error('Authentication check failed:', error);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  // Fetch crops and soils data
  useEffect(() => {
    const fetchCropsAndSoils = async () => {
      try {
        const response = await axios.get('/api/crops/');
        setCrops(response.data.crops);
        setSoils(response.data.soils);
      } catch (error) {
        console.error('Error fetching crops and soils:', error);
      }
    };

    fetchCropsAndSoils();
  }, []);

  // Fetch irrigation history when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      fetchIrrigationHistory();
    }
  }, [isAuthenticated]);

  const fetchIrrigationHistory = async () => {
    try {
      const response = await axios.get('/api/irrigation/history/');
      setIrrigationHistory(response.data.history);
    } catch (error) {
      console.error('Error fetching irrigation history:', error);
    }
  };

  const handleLogin = async (username, password) => {
    try {
      const response = await axios.post('/api-auth/login/', {
        username,
        password,
      });
      
      if (response.status === 200) {
        setIsAuthenticated(true);
        setUser({ username });
        navigate('/');
      }
    } catch (error) {
      console.error('Login failed:', error);
      return { error: 'Login failed. Please check your credentials.' };
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post('/api-auth/logout/');
      setIsAuthenticated(false);
      setUser(null);
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const handleIrrigationSubmit = async (formData) => {
    try {
      const response = await axios.post('/api/irrigation/decision/', formData);
      setIrrigationData(response.data);
      fetchIrrigationHistory(); // Refresh history after new decision
    } catch (error) {
      console.error('Error submitting irrigation data:', error);
      return { error: error.response?.data?.error || 'An error occurred' };
    }
  };

  const exportCSV = async () => {
    try {
      window.open('/api/irrigation/export-csv/', '_blank');
    } catch (error) {
      console.error('Error exporting CSV:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-700">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {isAuthenticated && (
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold text-primary-700">Smart Irrigation System</h1>
            <div className="flex items-center space-x-4">
              <span className="text-gray-600">Welcome, {user?.username}</span>
              <button 
                onClick={handleLogout}
                className="text-sm bg-gray-200 hover:bg-gray-300 px-3 py-1 rounded-md"
              >
                Logout
              </button>
            </div>
          </div>
        </header>
      )}

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          <Route 
            path="/login" 
            element={
              isAuthenticated ? 
                <Navigate to="/" /> : 
                <LoginForm onLogin={handleLogin} />
            } 
          />
          <Route 
            path="/" 
            element={
              isAuthenticated ? (
                <div className="space-y-8">
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <div className="lg:col-span-1">
                      <InputForm 
                        onSubmit={handleIrrigationSubmit} 
                        crops={crops}
                        soils={soils}
                      />
                    </div>
                    <div className="lg:col-span-2">
                      <DecisionDisplay data={irrigationData} />
                    </div>
                  </div>
                  
                  <div className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex justify-between items-center mb-6">
                      <h2 className="text-xl font-semibold text-gray-800">Irrigation History</h2>
                      <button 
                        onClick={exportCSV}
                        className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm flex items-center"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        Export CSV
                      </button>
                    </div>
                    
                    <div className="mb-8">
                      <HistoryChart history={irrigationHistory} />
                    </div>
                    
                    <HistoryTable history={irrigationHistory} />
                  </div>
                </div>
              ) : (
                <Navigate to="/login" />
              )
            } 
          />
        </Routes>
      </main>

      <footer className="bg-white border-t border-gray-200 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-gray-500 text-sm">
            &copy; {new Date().getFullYear()} Smart Irrigation System. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default App;

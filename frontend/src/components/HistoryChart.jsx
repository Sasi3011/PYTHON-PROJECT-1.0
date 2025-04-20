import React, { useEffect, useState } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, TimeScale } from 'chart.js';
import { Line } from 'react-chartjs-2';
import 'chartjs-adapter-date-fns';

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, TimeScale);

const HistoryChart = ({ history }) => {
  const [chartData, setChartData] = useState({
    datasets: [],
  });
  const [chartOptions, setChartOptions] = useState({});

  useEffect(() => {
    if (!history || history.length === 0) return;

    // Sort history by timestamp
    const sortedHistory = [...history].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

    // Prepare data for chart
    const labels = sortedHistory.map(item => new Date(item.timestamp));
    const waterAmountData = sortedHistory.map(item => item.decision.water_amount);
    const soilMoistureData = sortedHistory.map(item => item.sensor_data.soil_moisture);
    const rainProbabilityData = sortedHistory.map(item => item.weather_data.rain_probability);

    setChartData({
      labels,
      datasets: [
        {
          label: 'Water Amount (L/h)',
          data: waterAmountData,
          borderColor: 'rgb(53, 162, 235)',
          backgroundColor: 'rgba(53, 162, 235, 0.5)',
          yAxisID: 'y',
        },
        {
          label: 'Soil Moisture (%)',
          data: soilMoistureData,
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.5)',
          yAxisID: 'y1',
        },
        {
          label: 'Rain Probability (%)',
          data: rainProbabilityData,
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.5)',
          yAxisID: 'y1',
        },
      ],
    });

    setChartOptions({
      responsive: true,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      stacked: false,
      plugins: {
        title: {
          display: true,
          text: 'Irrigation History',
        },
        tooltip: {
          callbacks: {
            title: function(tooltipItems) {
              return new Date(tooltipItems[0].parsed.x).toLocaleString();
            }
          }
        }
      },
      scales: {
        x: {
          type: 'time',
          time: {
            unit: 'day',
            tooltipFormat: 'PPP',
            displayFormats: {
              day: 'MMM d'
            }
          },
          title: {
            display: true,
            text: 'Date',
          },
        },
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          title: {
            display: true,
            text: 'Water Amount (L/h)',
          },
          min: 0,
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          title: {
            display: true,
            text: 'Percentage (%)',
          },
          min: 0,
          max: 100,
          grid: {
            drawOnChartArea: false,
          },
        },
      },
    });
  }, [history]);

  if (!history || history.length === 0) {
    return (
      <div className="chart-container flex items-center justify-center bg-gray-50 rounded-lg p-4">
        <p className="text-gray-500">No data available for chart visualization</p>
      </div>
    );
  }

  return (
    <div className="chart-container bg-white p-4 rounded-lg border border-gray-200">
      <Line options={chartOptions} data={chartData} />
    </div>
  );
};

export default HistoryChart;

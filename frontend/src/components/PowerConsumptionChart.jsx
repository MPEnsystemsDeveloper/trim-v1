import React, { useState, useMemo } from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip as ChartTooltip, Legend } from 'chart.js';
import dayjs from 'dayjs';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, ChartTooltip, Legend);

// CORRECTED: The component now correctly processes the `data` prop from the `/daily-consumption` endpoint.
// It uses `item.date` instead of `item.timestamp` and `item.total_kWh` instead of `item.total_kwh`.
const PowerConsumptionChart = ({ data }) => {
  const [mode, setMode] = useState('day');

  const chartData = useMemo(() => {
    if (!data || data.length === 0) {
      return { labels: [], datasets: [] };
    }

    const aggregated = data.reduce((acc, item) => {
      // Use `item.date` from the API response
      const dateKey = mode === 'day'
        ? dayjs(item.date).format('YYYY-MM-DD')
        : dayjs(item.date).startOf('month').format('YYYY-MM-DD');
      
      // Use `item.total_kWh` (case-sensitive) from the API response
      const value = item.total_kWh || 0;
      
      if (!acc[dateKey]) {
        acc[dateKey] = 0;
      }
      acc[dateKey] += value;
      
      return acc;
    }, {});

    const processedData = Object.entries(aggregated)
      .map(([date, total_kWh]) => ({ date, total_kWh }))
      .sort((a, b) => dayjs(a.date).isAfter(dayjs(b.date)) ? 1 : -1);

    const maxPower = processedData.length > 0 
      ? Math.max(...processedData.map(item => item.total_kWh))
      : 0;

    const labels = processedData.map(item => {
      return mode === 'day'
        ? dayjs(item.date).format('DD MMM')
        : dayjs(item.date).format('MMM YYYY');
    });

    return {
      labels,
      datasets: [{
        label: 'Power (kWh)',
        data: processedData.map(item => item.total_kWh),
        backgroundColor: processedData.map(item => 
          (item.total_kWh === maxPower && maxPower > 0) ? '#189B4B' : '#DEFEEB'
        ),
        hoverBackgroundColor: '#189B4B',
        borderRadius: 6,
        barThickness: 30,
      }],
    };
  }, [data, mode]);

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        enabled: false,
        external: (context) => {
          const tooltipModel = context.tooltip;
          let tooltipEl = document.getElementById('custom-bar-tooltip');
          if (!tooltipEl) {
            tooltipEl = document.createElement('div');
            tooltipEl.id = 'custom-bar-tooltip';
            tooltipEl.className = 'p-3 rounded-md shadow text-sm border';
            tooltipEl.style.backgroundColor = '#189B4B';
            tooltipEl.style.borderColor = '#157A3C';
            tooltipEl.style.color = '#fff';
            tooltipEl.style.position = 'absolute';
            tooltipEl.style.pointerEvents = 'none';
            tooltipEl.style.transition = 'opacity 0.1s ease';
            tooltipEl.style.zIndex = 100;
            document.body.appendChild(tooltipEl);
          }
          if (tooltipModel.opacity === 0) {
            tooltipEl.style.opacity = 0; return;
          }
          if (tooltipModel.body) {
            const label = tooltipModel.title[0];
            const value = tooltipModel.dataPoints[0].raw;
            tooltipEl.innerHTML = `
              <div class="font-semibold mb-1">${label}</div>
              <div style="font-weight:500;">Power: ${parseFloat(value).toFixed(2)} kWh</div>
            `;
          }
          const { offsetLeft: chartX, offsetTop: chartY } = context.chart.canvas;
          tooltipEl.style.opacity = 1;
          tooltipEl.style.left = chartX + tooltipModel.caretX + 'px';
          tooltipEl.style.top = chartY + tooltipModel.caretY + 'px';
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: { display: true, text: 'kWh', font: { size: 12 } },
        grid: { color: '#F3F4F6', drawBorder: false },
      },
      x: {
        title: { display: true, text: mode === 'day' ? 'Date' : 'Month', font: { size: 12 } },
        grid: { display: false },
      },
    },
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <div className="px-4 py-1 bg-[#DEFEEB] text-sm font-semibold rounded-full text-[#189B4B]">
          Power Consumption
        </div>
        <div className="flex bg-[#F1F1F1] rounded-full p-1 text-sm font-medium">
          <button
            onClick={() => setMode('month')}
            className={`px-3 py-1 rounded-full transition-colors duration-200 ${
              mode === 'month' ? 'bg-white shadow-sm text-[#189B4B]' : 'text-gray-500'
            }`}
          >
            Month
          </button>
          <button
            onClick={() => setMode('day')}
            className={`px-3 py-1 rounded-full transition-colors duration-200 ${
              mode === 'day' ? 'bg-white shadow-sm text-[#189B4B]' : 'text-gray-500'
            }`}
          >
            Day
          </button>
        </div>
      </div>
      <div className="h-[300px] flex items-center justify-center">
        {chartData.labels && chartData.labels.length > 0 ? (
          <Bar data={chartData} options={options} />
        ) : (
          <div className="text-center text-gray-500">No consumption data available for the selected filters.</div>
        )}
      </div>
    </div>
  );
};

export default PowerConsumptionChart;
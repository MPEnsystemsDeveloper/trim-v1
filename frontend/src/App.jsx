// App.jsx

import React, { useState, useEffect, useCallback } from "react";
import dayjs from "dayjs"; // Make sure dayjs is installed: npm install dayjs
import Sidebar from "./components/Sidebar";
import FilterBar from "./components/FilterBar";
import PowerConsumptionChart from "./components/PowerConsumptionChart";
import PhaseWiseCurrentChart from "./components/PhaseWiseCurrentChart";
import PhaseWisePowerChart from "./components/PhaseWisePowerChart";
import TotalPowerChart from "./components/TotalPowerChart";

// The API base URL is correct.
const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [showTotalPower, setShowTotalPower] = useState(false);

  // Helper function to set the initial date range
  const getInitialFilter = () => {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    return {
      device: "",
      startDate: yesterday, // JS Date object for the date picker
      endDate: today,       // JS Date object for the date picker
      // UPDATED: The backend expects '1hr', not '1h'
      interval: "1hr",
    };
  };

  const [filter, setFilter] = useState(getInitialFilter);
  const [mainChartData, setMainChartData] = useState([]);
  const [powerConsumptionData, setPowerConsumptionData] = useState([]);
  const [deviceNames, setDeviceNames] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [xAxisTicks, setXAxisTicks] = useState([]);

  // UPDATED: The entire data fetching logic is revised to match the backend API.
  const fetchAllChartData = useCallback(async (currentFilter) => {
    if (!currentFilter.device) {
      console.log("Skipping fetch: No device selected.");
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);
    setMainChartData([]);
    setPowerConsumptionData([]);
    setXAxisTicks([]);

    try {
      // --- Fetch Processed Data ---
      const processedParams = new URLSearchParams({
        device_name: currentFilter.device,
        interval: currentFilter.interval,
      });

      // UPDATED: Format dates and times as separate strings as expected by the backend
      if (currentFilter.startDate) {
        processedParams.append("start_date", dayjs(currentFilter.startDate).format("YYYY-MM-DD"));
        processedParams.append("start_time", dayjs(currentFilter.startDate).format("HH:mm"));
      }
      if (currentFilter.endDate) {
        processedParams.append("end_date", dayjs(currentFilter.endDate).format("YYYY-MM-DD"));
        processedParams.append("end_time", dayjs(currentFilter.endDate).format("HH:mm"));
      }
      
      // UPDATED: Correct endpoint path from '/processed-data' to '/processed'
      const processedPromise = fetch(`${API_BASE_URL}/processed?${processedParams.toString()}`);

      // --- Fetch Daily Consumption Data ---
      const consumptionParams = new URLSearchParams({
        device_name: currentFilter.device,
      });
      if (currentFilter.startDate) {
        consumptionParams.append("start_date", dayjs(currentFilter.startDate).format("YYYY-MM-DD"));
      }
      if (currentFilter.endDate) {
        consumptionParams.append("end_date", dayjs(currentFilter.endDate).format("YYYY-MM-DD"));
      }

      // UPDATED: Correct endpoint path from '/power-consumption' to '/daily-consumption'
      const consumptionPromise = fetch(`${API_BASE_URL}/daily-consumption?${consumptionParams.toString()}`);

      // Await both promises
      const [processedResult, consumptionResult] = await Promise.all([processedPromise, consumptionPromise]);

      // --- Handle Processed Data Response ---
      if (!processedResult.ok) {
        const err = await processedResult.json();
        throw new Error(`Failed to fetch main chart data: ${err.detail || processedResult.statusText}`);
      }
      // UPDATED: The backend returns a direct array, not an object with a 'data' key.
      const processedData = await processedResult.json();
      setMainChartData(processedData);

      // Calculate X-axis ticks from the direct array
      if (processedData && processedData.length > 0) {
        const ticks = new Set();
        processedData.forEach(item => {
          ticks.add(dayjs(item.timestamp).startOf('day').valueOf());
        });
        setXAxisTicks(Array.from(ticks));
      }

      // --- Handle Daily Consumption Response ---
      if (!consumptionResult.ok) {
        const err = await consumptionResult.json();
        throw new Error(`Failed to fetch power consumption data: ${err.detail || consumptionResult.statusText}`);
      }
      // UPDATED: The backend returns a direct array.
      const consumptionData = await consumptionResult.json();
      setPowerConsumptionData(consumptionData);

    } catch (e) {
      console.error("Fetch error:", e);
      setError(e.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // UPDATED: Logic to fetch initial device names is revised.
  useEffect(() => {
    const fetchInitialData = async () => {
      setIsLoading(true);
      try {
        // UPDATED: Correct endpoint path from '/device-names' to '/devices'
        const namesResponse = await fetch(`${API_BASE_URL}/devices`);
        if (!namesResponse.ok) throw new Error('Could not fetch device list.');
        
        // UPDATED: The backend returns a direct array of strings.
        const fetchedDeviceNames = await namesResponse.json();
        setDeviceNames(fetchedDeviceNames);

        if (fetchedDeviceNames && fetchedDeviceNames.length > 0) {
          const firstDevice = fetchedDeviceNames[0];
          // Set the filter state with the first device
          const initialFilter = { ...getInitialFilter(), device: firstDevice };
          setFilter(initialFilter);
          // Fetch data for the first device
          await fetchAllChartData(initialFilter);
        } else {
          // No devices found, stop loading
          setIsLoading(false);
        }
      } catch (e) {
        setError(e.message);
        setIsLoading(false);
      }
    };
    fetchInitialData();
    // The dependency array is correct. We only want this to run once on mount.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleApplyFilter = () => {
    fetchAllChartData(filter);
  };

  // The JSX rendering part remains the same as it was already well-structured.
  return (
    <div className="flex h-screen bg-[#F8FAFC]">
      <Sidebar />
      <div className="flex-1 p-6 overflow-y-auto">
        <h2 className="text-2xl font-semibold text-gray-800 mb-6">Current Meter Data</h2>
        <div className="mb-6">
          <FilterBar filter={filter} setFilter={setFilter} onApply={handleApplyFilter} deviceNames={deviceNames} />
        </div>
        {isLoading ? (
          <div className="text-center p-10">Loading...</div>
        ) : error ? (
          <div className="text-center p-10 text-red-500 bg-red-100 rounded-lg">
            <strong>Error:</strong> {error}
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white rounded-[20px] shadow-md p-5">
                <PowerConsumptionChart data={powerConsumptionData} />
              </div>
              <div className="bg-white rounded-[20px] shadow-md p-5">
                <PhaseWiseCurrentChart data={mainChartData} xAxisTicks={xAxisTicks} />
              </div>
            </div>
            <div className="mt-6 bg-white rounded-[20px] shadow-md p-5">
              <div className="flex mb-4">
                <button onClick={() => setShowTotalPower(false)} className={`px-5 py-2 rounded-l-full text-sm font-semibold ${!showTotalPower ? 'bg-green-600 text-white' : 'bg-green-100 text-green-600'}`}>Phase Wise Power</button>
                <button onClick={() => setShowTotalPower(true)} className={`px-5 py-2 rounded-r-full text-sm font-semibold ${showTotalPower ? 'bg-green-600 text-white' : 'bg-green-100 text-green-600'}`}>Total Power</button>
              </div>
              {showTotalPower ? 
                <TotalPowerChart data={mainChartData} xAxisTicks={xAxisTicks} /> : 
                <PhaseWisePowerChart data={mainChartData} xAxisTicks={xAxisTicks} />
              }
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
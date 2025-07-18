import React, { useState } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Label,
  CartesianGrid,
} from "recharts";
import dayjs from "dayjs";

const PhaseWisePowerChart = ({ data, xAxisTicks }) => {
  const [showR, setShowR] = useState(true);
  const [showY, setShowY] = useState(true);
  const [showB, setShowB] = useState(true);

  if (!data || data.length === 0) {
    // Added a title for consistency
    return (
      <>
        <div className="flex justify-between items-center mb-4">
          <div className="bg-green-100 text-green-700 px-4 py-1 rounded-full text-sm font-semibold shadow-sm">
            Phase Wise Power
          </div>
        </div>
        <div className="flex justify-center items-center h-[300px] text-gray-500">
          No data available for the selected filters.
        </div>
      </>
    );
  }

  const formattedData = data.map((item) => ({
    ...item,
    timestamp: dayjs(item.timestamp).valueOf(),
  }));

  return (
    <>
      {/* Added a title for the chart */}
      <div className="flex justify-between items-center mb-4">
        <div className="bg-green-100 text-green-700 px-4 py-1 rounded-full text-sm font-semibold shadow-sm">
          Phase Wise Power
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowB(!showB)}
            className={`flex items-center px-3 py-1 text-sm font-semibold rounded-full border transition 
              ${showB ? "bg-blue-100 text-blue-600 border-blue-400" : "bg-white text-blue-400 border-blue-300"}`}
          >
            P_B
          </button>
          <button
            onClick={() => setShowY(!showY)}
            className={`flex items-center px-3 py-1 text-sm font-semibold rounded-full border transition 
              ${showY ? "bg-yellow-100 text-yellow-600 border-yellow-400" : "bg-white text-yellow-400 border-yellow-300"}`}
          >
            P_Y
          </button>
          <button
            onClick={() => setShowR(!showR)}
            className={`flex items-center px-3 py-1 text-sm font-semibold rounded-full border transition 
              ${showR ? "bg-red-100 text-red-600 border-red-400" : "bg-white text-red-400 border-red-300"}`}
          >
            P_R
          </button>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={formattedData} margin={{ top: 10, right: 30, left: 10, bottom: 40 }}>
          <defs>
            <linearGradient id="colorR" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#ef4444" stopOpacity={0.4} /><stop offset="95%" stopColor="#ef4444" stopOpacity={0.05} /></linearGradient>
            <linearGradient id="colorY" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#eab308" stopOpacity={0.4} /><stop offset="95%" stopColor="#eab308" stopOpacity={0.05} /></linearGradient>
            <linearGradient id="colorB" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} /><stop offset="95%" stopColor="#3b82f6" stopOpacity={0.05} /></linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />

          <XAxis
            dataKey="timestamp"
            type="number"
            domain={['dataMin', 'dataMax']}
            ticks={xAxisTicks}
            tickFormatter={(unixTime) => dayjs(unixTime).format('DD MMM')}
            tick={{ fontSize: 11 }}
            angle={-30}
            textAnchor="end"
          >
            <Label value="Timestamp" offset={30} position="bottom" fontSize={12} />
          </XAxis>
          <YAxis tick={{ fontSize: 12 }}>
            <Label value="Power (kW)" angle={-90} position="insideLeft" offset={0} fontSize={12} />
          </YAxis>

          <Tooltip
            // The `labelFormatter` prop is removed as it's not used when a custom `content` function is provided.
            content={({ active, payload, label }) => {
              if (active && payload && payload.length) {
                return (
                  <div className="p-3 rounded-md shadow text-sm border" style={{ backgroundColor: "#189B4B", color: "#fff" }}>
                    {/* --- MODIFIED LINE --- */}
                    {/* The label (unix timestamp) is now formatted correctly */}
                    <p className="font-semibold mb-1">
                      {dayjs(label).format('DD MMM YYYY, HH:mm')}
                    </p>
                    {/* --- END OF MODIFICATION --- */}
                    
                    {payload.map((entry, index) => (
                      <p key={index} style={{ color: "#fff", fontWeight: 500, marginTop: '4px' }}>
                        {entry.name} : {parseFloat(entry.value).toFixed(2)} kW
                      </p>
                    ))}
                  </div>
                );
              }
              return null;
            }}
          />

          {showB && <Area type="monotone" dataKey="b_power(kw)" stroke="#3b82f6" fill="url(#colorB)" name="Power-B" />}
          {showY && <Area type="monotone" dataKey="y_power(kw)" stroke="#eab308" fill="url(#colorY)" name="Power-Y" />}
          {showR && <Area type="monotone" dataKey="r_power(kw)" stroke="#ef4444" fill="url(#colorR)" name="Power-R" />}
        </AreaChart>
      </ResponsiveContainer>
    </>
  );
};

export default PhaseWisePowerChart;
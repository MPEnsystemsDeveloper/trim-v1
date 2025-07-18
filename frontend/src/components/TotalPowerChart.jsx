import React from "react";
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

// CORRECTED: Updated to use `xAxisTicks` prop and correct `dataKey` value.
const TotalPowerChart = ({ data, xAxisTicks }) => {
  if (!data || data.length === 0) {
    // Added a title for consistency
    return (
      <>
        <div className="flex justify-between items-center mb-4">
          <div className="bg-green-100 text-green-700 px-4 py-1 rounded-full text-sm font-semibold shadow-sm">
            Total Power
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
          Total Power
        </div>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart
          data={formattedData}
          margin={{ top: 10, right: 30, left: 10, bottom: 40 }}
        >
          <defs>
            <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#22c55e" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#22c55e" stopOpacity={0.05} />
            </linearGradient>
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
            <Label
              value="Timestamp"
              offset={30}
              position="bottom"
              fontSize={12}
            />
          </XAxis>

          <YAxis tick={{ fontSize: 12 }}>
            <Label
              value="Power (kW)"
              angle={-90}
              position="insideLeft"
              offset={0}
              fontSize={12}
            />
          </YAxis>

          <Tooltip
            // The `labelFormatter` prop is removed as it's not used when a custom `content` function is provided.
            content={({ active, payload, label }) => {
              if (active && payload && payload.length) {
                return (
                  <div
                    className="p-3 rounded-md shadow text-sm border"
                    style={{ backgroundColor: "#189B4B", color: "#fff" }}
                  >
                    {/* MODIFICATION: Format the label (which is a unix timestamp) here */}
                    <p className="font-semibold mb-1">{dayjs(label).format('DD MMM YYYY, HH:mm')}</p>
                    {payload.map((entry, index) => (
                      <p key={index} style={{ color: "#fff", fontWeight: 500 }}>
                        {entry.name} : {parseFloat(entry.value).toFixed(2)} kW
                      </p>
                    ))}
                  </div>
                );
              }
              return null;
            }}
          />

          {/* CORRECTED: The dataKey attribute now matches the API response */}
          <Area
            type="monotone"
            dataKey="total_power(kw)"
            stroke="#16a34a"
            fill="url(#colorTotal)"
            name="Total Power"
            strokeWidth={2}
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </>
  );
};

export default TotalPowerChart;
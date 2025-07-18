import React, { forwardRef } from "react";
import DatePicker from "react-datepicker";
import { Calendar, ChevronDown } from "lucide-react";

import "react-datepicker/dist/react-datepicker.css";

// --- Helper Components (No changes needed here) ---
const FilterGroup = ({ label, htmlFor, children }) => (
  <div className="flex flex-col flex-grow min-w-[200px]">
    <label htmlFor={htmlFor} className="block mb-1.5 text-sm font-medium text-slate-600">
      {label}
    </label>
    {children}
  </div>
);

const SelectInput = ({ id, value, onChange, children }) => (
  <div className="relative w-full">
    <select
      id={id}
      value={value}
      onChange={onChange}
      className="h-[42px] appearance-none w-full bg-gray-50 border border-gray-200 text-slate-800 text-sm rounded-lg focus:border-[#189B4B] focus:ring-1 focus:ring-[#189B4B] block p-2.5 pr-8 focus:outline-none"
    >
      {children}
    </select>
    <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2.5 text-slate-500">
      <ChevronDown size={18} />
    </div>
  </div>
);

const CustomDateInput = forwardRef(({ value, onClick, placeholder, ...props }, ref) => (
  <div className="relative">
    <input
      type="text"
      className="h-[42px] w-full bg-gray-50 border border-gray-200 text-slate-800 text-sm rounded-lg focus:border-[#189B4B] focus:ring-1 focus:ring-[#189B4B] block p-2.5"
      onClick={onClick}
      ref={ref}
      value={value}
      placeholder={placeholder}
      readOnly
      {...props}
    />
    <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3 text-slate-500">
      <Calendar size={18} />
    </div>
  </div>
));

// --- The Main FilterBar Component ---
const FilterBar = ({ filter, setFilter, onApply, deviceNames }) => {
  const handleDateChange = (date, fieldName) => {
    setFilter(prevFilter => ({ ...prevFilter, [fieldName]: date }));
  };
  
  const startDate = filter.startDate ? new Date(filter.startDate) : null;
  const endDate = filter.endDate ? new Date(filter.endDate) : null;

  return (
    <div className="bg-white p-5 rounded-xl shadow-md">
      <div className="flex flex-wrap items-end gap-x-4 gap-y-5">
        
        <FilterGroup label="Device" htmlFor="device-filter">
          <SelectInput
            id="device-filter"
            value={filter.device}
            onChange={(e) => setFilter({ ...filter, device: e.target.value })}
          >
            <option value="">Select a Device</option>
            {deviceNames && deviceNames.map((name) => <option key={name} value={name}>{name}</option>)}
          </SelectInput>
        </FilterGroup>

        <FilterGroup label="Start Date & Time" htmlFor="start-date">
          <DatePicker
            id="start-date"
            name="startDate"
            selected={startDate}
            onChange={(date) => handleDateChange(date, 'startDate')}
            selectsStart
            startDate={startDate}
            endDate={endDate}
            maxDate={endDate || new Date()}
            showTimeSelect
            isClearable
            dateFormat="MM/dd/yyyy h:mm aa"
            customInput={<CustomDateInput placeholder=" " />}
          />
        </FilterGroup>

        <FilterGroup label="End Date & Time" htmlFor="end-date">
          <DatePicker
            id="end-date"
            name="endDate"
            selected={endDate}
            onChange={(date) => handleDateChange(date, 'endDate')}
            selectsEnd
            startDate={startDate}
            endDate={endDate}
            minDate={startDate}
            showTimeSelect
            isClearable
            dateFormat="MM/dd/yyyy h:mm aa"
            customInput={<CustomDateInput placeholder=" " />}
          />
        </FilterGroup>
        
        <FilterGroup label="Interval" htmlFor="interval-filter">
            <SelectInput
              id="interval-filter"
              value={filter.interval}
              onChange={(e) => setFilter({ ...filter, interval: e.target.value })}
            >
              {/* CORRECTED: The 'value' attributes now match the backend API enum */}
              <option value="raw">Raw Data</option>
              <option value="1hr">1 Hour</option>
              <option value="4hr">4 Hours</option>
              <option value="8hr">8 Hours</option>
              <option value="12hr">12 Hours</option>
              <option value="24hr">24 Hours (Daily)</option>
            </SelectInput>
        </FilterGroup>

        <div className="flex-shrink-0">
          <button
            onClick={onApply}
            disabled={!filter.device}
            className="h-[42px] w-full sm:w-auto bg-[#189B4B] text-white font-semibold text-sm rounded-lg hover:bg-[#148641] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#189B4B] px-5 disabled:bg-slate-300 disabled:cursor-not-allowed"
          >
            Apply Filters
          </button>
        </div>
      </div>
    </div>
  );
};

export default FilterBar;
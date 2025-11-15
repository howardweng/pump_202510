// components/ToggleSwitch/index.jsx
import React from 'react';

function ToggleSwitch({
  checked,
  onChange,
  label,
  disabled = false
}) {
  return (
    <label className="flex items-center cursor-pointer">
      <input
        type="checkbox"
        checked={checked}
        onChange={onChange}
        disabled={disabled}
        className="hidden"
      />
      <div className={`w-10 h-5 flex items-center rounded-full p-1 duration-300 ${
        checked ? 'bg-green-500' : 'bg-gray-400'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}>
        <div className={`bg-white w-4 h-4 rounded-full shadow-md transform duration-300 ${
          checked ? 'translate-x-5' : 'translate-x-0'
        }`}></div>
      </div>
      {label && <span className="ml-2 text-gray-700 text-sm">{label}</span>}
    </label>
  );
}

export default ToggleSwitch;

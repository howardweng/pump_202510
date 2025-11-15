// components/StatusIndicator/index.jsx
import React from 'react';

function StatusIndicator({
  status,      // 'normal' | 'error'
  label,       // 顯示文字
  size = 'md'  // 'sm' | 'md' | 'lg'
}) {
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-10 h-10'
  };

  return (
    <div className="flex flex-col items-center bg-white p-3 rounded-lg shadow-md border-2 border-slate-300 w-32 text-center">
      <div className={`${sizeClasses[size]} rounded-full shadow-lg transition-colors duration-500 ${
        status === 'normal'
          ? 'bg-green-600 slow-flashing'
          : 'bg-red-600 flashing'
      }`}></div>
      <p className="mt-2 text-sm font-bold text-slate-800 break-words leading-tight whitespace-pre-wrap">
        {label}
      </p>
    </div>
  );
}

export default StatusIndicator;

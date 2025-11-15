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

  const containerClasses = {
    sm: 'p-2 w-full',
    md: 'p-3 w-32',
    lg: 'p-4 w-36'
  };

  const textClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base'
  };

  return (
    <div className={`flex flex-col items-center bg-white rounded-lg shadow-md border-2 border-slate-300 text-center ${containerClasses[size]}`}>
      <div className={`${sizeClasses[size]} rounded-full shadow-lg transition-colors duration-500 ${
        status === 'normal'
          ? 'bg-green-600 slow-flashing'
          : 'bg-red-600 flashing'
      }`}></div>
      <p className={`mt-1 ${textClasses[size]} font-bold text-slate-800 break-words leading-tight whitespace-pre-wrap`}>
        {label}
      </p>
    </div>
  );
}

export default StatusIndicator;

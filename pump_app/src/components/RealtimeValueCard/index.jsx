// components/RealtimeValueCard/index.jsx
import React from 'react';

function RealtimeValueCard({
  title,         // 卡片標題
  value,         // 數值
  unit,          // 單位
  valueColor,    // 數值顏色 (text-blue-600, text-orange-800)
  size = 'lg'    // 'md' | 'lg' | 'xl'
}) {
  const sizeClasses = {
    md: 'text-5xl',
    lg: 'text-6xl',
    xl: 'text-7xl'
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg border-2 border-slate-300 text-center">
      <h3 className="text-lg font-bold text-slate-800">{title}</h3>
      <p className={`${sizeClasses[size]} font-bold ${valueColor} mt-2`}>
        {value}
      </p>
      <p className="text-2xl font-semibold text-slate-700">{unit}</p>
    </div>
  );
}

export default RealtimeValueCard;

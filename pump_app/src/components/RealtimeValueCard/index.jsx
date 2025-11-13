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
    md: 'text-4xl',
    lg: 'text-5xl',
    xl: 'text-6xl'
  };

  return (
    <div className="bg-white p-6 rounded shadow border border-gray-300 text-center">
      <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
      <p className={`${sizeClasses[size]} font-bold ${valueColor} mt-2`}>
        {value}
      </p>
      <p className="text-2xl text-gray-600">{unit}</p>
    </div>
  );
}

export default RealtimeValueCard;

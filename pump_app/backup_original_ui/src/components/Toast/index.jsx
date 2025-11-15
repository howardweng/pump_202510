// components/Toast/index.jsx
import React from 'react';

function Toast({ message, onClose, type = 'success' }) {
  const bgColors = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    info: 'bg-blue-500'
  };

  return (
    <div className={`fixed bottom-28 left-1/2 transform -translate-x-1/2 ${bgColors[type]} text-white p-3 rounded shadow-lg z-50`}>
      {message}
      <button
        className="mt-2 px-4 py-1 bg-gray-800 text-white rounded block mx-auto"
        onClick={onClose}
      >
        關閉
      </button>
    </div>
  );
}

export default Toast;

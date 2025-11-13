// pages/MainDashboard/index.jsx
import React from 'react';
import { useTest } from '../../context/TestContext';

function MainDashboard() {
  const {
    testMode,
    testType,
    testStatus,
    realtimePressure,
    realtimeCurrent,
    realtimeFlow,
    sensorStatus,
    currentSensorStatus,
    relayStatus
  } = useTest();

  return (
    <div className="container mx-auto px-4 py-6">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">主控台</h1>

      {/* 系統狀態 */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">系統狀態</h2>
        <div className="grid grid-cols-3 gap-4">
          <div className="p-4 bg-gray-50 rounded">
            <p className="text-sm text-gray-600">感測器</p>
            <p className="text-lg font-bold text-gray-800">{sensorStatus}</p>
          </div>
          <div className="p-4 bg-gray-50 rounded">
            <p className="text-sm text-gray-600">電流感測器</p>
            <p className="text-lg font-bold text-gray-800">{currentSensorStatus}</p>
          </div>
          <div className="p-4 bg-gray-50 rounded">
            <p className="text-sm text-gray-600">繼電器</p>
            <p className="text-lg font-bold text-gray-800">{relayStatus}</p>
          </div>
        </div>
      </div>

      {/* 測試資訊 */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">測試資訊</h2>
        <div className="grid grid-cols-3 gap-4">
          <div className="p-4 bg-blue-50 rounded">
            <p className="text-sm text-gray-600">測試模式</p>
            <p className="text-lg font-bold text-blue-800">
              {testMode === 'vacuum' ? '真空幫浦' : testMode === 'positive' ? '正壓幫浦' : '手動模式'}
            </p>
          </div>
          <div className="p-4 bg-blue-50 rounded">
            <p className="text-sm text-gray-600">測試類型</p>
            <p className="text-lg font-bold text-blue-800">
              {testType === 'pressure' ? '壓力測試' : '流量測試'}
            </p>
          </div>
          <div className="p-4 bg-blue-50 rounded">
            <p className="text-sm text-gray-600">測試狀態</p>
            <p className="text-lg font-bold text-blue-800">
              {testStatus === 'idle' ? '待機' : testStatus === 'running' ? '執行中' : testStatus === 'paused' ? '暫停' : '停止'}
            </p>
          </div>
        </div>
      </div>

      {/* 即時數據 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">即時數據</h2>
        <div className="grid grid-cols-3 gap-4">
          <div className="p-4 bg-green-50 rounded">
            <p className="text-sm text-gray-600">
              {testType === 'pressure' ? '壓力 (kPa)' : '流量'}
            </p>
            <p className="text-2xl font-bold text-green-800">
              {testType === 'pressure' ? realtimePressure.toFixed(1) : realtimeFlow.toFixed(1)}
            </p>
          </div>
          <div className="p-4 bg-orange-50 rounded">
            <p className="text-sm text-gray-600">電流 (A)</p>
            <p className="text-2xl font-bold text-orange-800">{realtimeCurrent.toFixed(1)}</p>
          </div>
          <div className="p-4 bg-purple-50 rounded">
            <p className="text-sm text-gray-600">功率 (W)</p>
            <p className="text-2xl font-bold text-purple-800">
              {(realtimeCurrent * 24).toFixed(0)}
            </p>
          </div>
        </div>
      </div>

      {/* 提示訊息 */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded">
        <p className="text-sm text-blue-800">
          請前往「測試設定」頁面配置測試參數後開始測試
        </p>
      </div>
    </div>
  );
}

export default MainDashboard;

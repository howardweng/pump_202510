// pages/MainDashboard/index.jsx
import React, { useState, useRef } from 'react';
import { useTest } from '../../context/TestContext';
import { useMQTT } from '../../hooks/useMQTT';
import StatusIndicator from '../../components/StatusIndicator';
import RealtimeValueCard from '../../components/RealtimeValueCard';
import Toast from '../../components/Toast';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { exportTestData, saveTestToLocalStorage, saveReferenceToLocalStorage } from '../../utils/exportData';

function MainDashboard() {
  const {
    testMode, setTestMode,
    testType, setTestType,
    testStatus, setTestStatus,
    realtimePressure,
    realtimeCurrent,
    realtimeFlow,
    chartData,
    setChartData,
    sensorStatus,
    currentSensorStatus,
    relayStatus,
    coverClosed, setCoverClosed,
    valveStatus, setValveStatus,
    startTimeRef,
    testConfig
  } = useTest();

  const { publishCommand } = useMQTT();
  const [toastMessage, setToastMessage] = useState('');
  const chartRef = useRef(null);

  // 啟動測試
  const handleStart = () => {
    if (!testConfig.pumpModel) {
      setToastMessage('⚠️ 請先在「測試設定」頁面配置測試參數');
      return;
    }

    if (!coverClosed) {
      setToastMessage('⚠️ 請關閉測試保護蓋才能啟動測試');
      return;
    }

    setTestStatus('running');
    startTimeRef.current = Date.now();
    setChartData([]);
    publishCommand('pump/control/start', { mode: testMode, type: testType });
    setToastMessage('✅ 測試已啟動');
  };

  // 暫停測試
  const handlePause = () => {
    setTestStatus('paused');
    publishCommand('pump/control/pause', {});
    setToastMessage('⏸️ 測試已暫停');
  };

  // 停止測試
  const handleStop = () => {
    setTestStatus('stopped');
    publishCommand('pump/control/stop', {});
    setToastMessage('⏹️ 測試已停止');
  };

  // 手動控制電磁閥
  const handleValveToggle = (valve) => {
    if (testMode !== 'manual') {
      setToastMessage('⚠️ 請切換到手動模式才能控制電磁閥');
      return;
    }

    const newStatus = { ...valveStatus, [valve]: !valveStatus[valve] };

    // 安全檢查
    const dangerousCombos = [
      { A: true, B: true, C: false, D: false },
      { A: false, B: false, C: true, D: true },
      { A: true, B: true, C: true, D: true }
    ];

    const isDangerous = dangerousCombos.some(combo =>
      combo.A === newStatus.A &&
      combo.B === newStatus.B &&
      combo.C === newStatus.C &&
      combo.D === newStatus.D
    );

    if (isDangerous) {
      setToastMessage('⚠️ 警告: 此閥門組合可能造成設備損壞或安全風險！');
      return;
    }

    setValveStatus(newStatus);
    publishCommand(`pump/valves/${valve.toLowerCase()}`, { state: !valveStatus[valve] });
  };

  // 獲取圖表 Y 軸標籤和單位
  const getYAxisLabel = () => {
    if (testType === 'pressure') {
      return '壓力 (kPa)';
    } else {
      return testMode === 'vacuum' || testMode === 'positive' ? '氣體流量 (L/min)' : '液體流量 (m³/h)';
    }
  };

  // 獲取當前數值和單位
  const getCurrentValue = () => {
    if (testType === 'pressure') {
      return { value: realtimePressure.toFixed(1), unit: 'kPa', color: 'text-blue-600' };
    } else {
      const unit = testMode === 'vacuum' || testMode === 'positive' ? 'L/min' : 'm³/h';
      return { value: realtimeFlow.toFixed(1), unit, color: 'text-green-600' };
    }
  };

  // 匯出測試數據
  const handleExport = async () => {
    if (chartData.length === 0) {
      setToastMessage('⚠️ 沒有可匯出的數據');
      return;
    }

    const result = await exportTestData({
      chartData,
      testConfig,
      testMode,
      testType,
      chartElement: chartRef.current
    });

    if (result.success) {
      setToastMessage(`✅ 數據已匯出: ${result.filename}`);
    } else {
      setToastMessage(`❌ 匯出失敗: ${result.error}`);
    }
  };

  // 儲存為測試數據
  const handleSaveTest = () => {
    if (chartData.length === 0) {
      setToastMessage('⚠️ 沒有可儲存的數據');
      return;
    }

    const testData = {
      id: Date.now(),
      pumpModel: testConfig.pumpModel,
      testMode: testMode === 'vacuum' ? '真空幫浦' : testMode === 'positive' ? '正壓幫浦' : '手動模式',
      testType: testType === 'pressure' ? '壓力測試' : '流量測試',
      date: new Date().toISOString().split('T')[0],
      chartData: chartData,
      avgValue: chartData.length > 0
        ? (chartData.reduce((sum, d) => sum + (testType === 'pressure' ? d.pressure : d.flow), 0) / chartData.length).toFixed(2)
        : 0,
      avgCurrent: chartData.length > 0
        ? (chartData.reduce((sum, d) => sum + d.current, 0) / chartData.length).toFixed(2)
        : 0,
      duration: chartData.length > 0 ? chartData[chartData.length - 1].time : 0
    };

    if (saveTestToLocalStorage(testData)) {
      setToastMessage('✅ 測試數據已儲存');
    } else {
      setToastMessage('❌ 儲存失敗');
    }
  };

  // 儲存為參考數據
  const handleSaveReference = () => {
    if (chartData.length === 0) {
      setToastMessage('⚠️ 沒有可儲存的數據');
      return;
    }

    const referenceData = {
      id: Date.now(),
      pumpModel: testConfig.pumpModel,
      testMode: testMode === 'vacuum' ? '真空幫浦' : testMode === 'positive' ? '正壓幫浦' : '手動模式',
      testType: testType === 'pressure' ? '壓力測試' : '流量測試',
      date: new Date().toISOString().split('T')[0],
      chartData: chartData,
      avgValue: chartData.length > 0
        ? (chartData.reduce((sum, d) => sum + (testType === 'pressure' ? d.pressure : d.flow), 0) / chartData.length).toFixed(2)
        : 0,
      avgCurrent: chartData.length > 0
        ? (chartData.reduce((sum, d) => sum + d.current, 0) / chartData.length).toFixed(2)
        : 0,
      duration: chartData.length > 0 ? chartData[chartData.length - 1].time : 0
    };

    if (saveReferenceToLocalStorage(referenceData)) {
      setToastMessage('✅ 參考數據已儲存');
    } else {
      setToastMessage('❌ 儲存失敗');
    }
  };

  const currentData = getCurrentValue();

  return (
    <div className="container mx-auto px-4 py-2">
      {/* 頂部狀態列 + 控制區 - 混合改進風格 */}
      <div className="bg-white rounded-lg shadow-lg p-4 mb-3 border-2 border-slate-300">
        <div className="flex justify-between mb-3">
          {/* 狀態指示燈 */}
          <div className="flex gap-4">
            <StatusIndicator
              status={sensorStatus === '正常' ? 'normal' : 'error'}
              label={sensorStatus === '正常' ? (testType === 'pressure' ? '壓力偵測正常' : '流量偵測正常') : (testType === 'pressure' ? '壓力傳輸錯誤' : '流量傳輸錯誤')}
              size="md"
            />
            <StatusIndicator
              status={currentSensorStatus === '正常' ? 'normal' : 'error'}
              label={currentSensorStatus === '正常' ? '電流偵測正常' : '電流傳輸錯誤'}
              size="md"
            />
            <StatusIndicator
              status={relayStatus === '正常' ? 'normal' : 'error'}
              label={relayStatus === '正常' ? '繼電器正常' : '繼電器異常'}
              size="md"
            />
          </div>

          {/* 測試蓋狀態 + 控制按鈕 */}
          <div className="flex flex-col items-end gap-3">
          {/* 測試蓋狀態 */}
          <div className="flex items-center gap-4">
            <StatusIndicator
              status={coverClosed ? 'normal' : 'error'}
              label={coverClosed ? '測試蓋已關閉' : '測試蓋未關閉'}
              size="md"
            />
            <button
              onClick={() => setCoverClosed(!coverClosed)}
              className="px-5 py-2 bg-gray-600 text-white text-sm font-bold rounded-lg hover:bg-gray-700 transition shadow-md"
            >
              {coverClosed ? '模擬開蓋' : '模擬關蓋'}
            </button>
          </div>

          {/* 控制按鈕 */}
          <div className="flex gap-3">
            <button
              onClick={handleStart}
              disabled={testStatus === 'running' || !coverClosed}
              className="px-10 py-4 bg-green-600 text-white text-xl rounded-lg font-bold hover:bg-green-700 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
            >
              啟動測試
            </button>
            <button
              onClick={handlePause}
              disabled={testStatus !== 'running'}
              className="px-10 py-4 bg-yellow-600 text-white text-xl rounded-lg font-bold hover:bg-yellow-700 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
            >
              暫停
            </button>
            <button
              onClick={handleStop}
              disabled={testStatus === 'idle'}
              className="px-10 py-4 bg-red-600 text-white text-xl rounded-lg font-bold hover:bg-red-700 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
            >
              停止
            </button>
          </div>
        </div>
      </div>

        {/* 電磁閥狀態 */}
        <div className="border-t-2 border-slate-300 pt-4">
          <h3 className="text-sm font-bold text-slate-800 mb-3">電磁閥狀態 {testMode === 'manual' && <span className="text-xs text-blue-700 font-semibold">(點擊切換)</span>}</h3>
          <div className="flex gap-3">
            {['A', 'B', 'C', 'D'].map((valve) => (
              <button
                key={valve}
                onClick={() => handleValveToggle(valve)}
                disabled={testMode !== 'manual'}
                className={`px-7 py-3 rounded-lg font-bold text-lg transition shadow-md ${
                  valveStatus[valve]
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-300 text-slate-800'
                } ${testMode === 'manual' ? 'hover:opacity-80 cursor-pointer' : 'cursor-not-allowed opacity-60'}`}
              >
                {valve}: {valveStatus[valve] ? '開' : '關'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 左側配置 + 右側即時數值 */}
      <div className="grid grid-cols-12 gap-4 mb-3">
        {/* 左側：當前測試配置 */}
        <div className="col-span-3">
          {!testConfig.pumpModel ? (
            <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded-lg shadow-md border-2 border-yellow-200">
              <div className="flex items-center">
                <svg className="w-5 h-5 text-yellow-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <p className="text-yellow-900 font-bold text-sm">
                  尚未設定測試配置，請前往「測試設定」頁面進行設定
                </p>
              </div>
            </div>
          ) : (
            <div className="bg-blue-50 border-2 border-blue-300 rounded-lg p-4 shadow-md h-full">
              <h3 className="text-base font-bold text-slate-800 mb-4 pb-2 border-b border-blue-300 text-center">當前測試配置</h3>
              <div className="space-y-2.5 text-sm">
                <div className="flex items-start">
                  <span className="text-slate-400 font-medium w-20 flex-shrink-0">型號:</span>
                  <span className="text-lg font-bold text-[#0066CC] flex-1 break-words">{testConfig.pumpModel}</span>
                </div>
                <div className="flex items-start">
                  <span className="text-slate-400 font-medium w-20 flex-shrink-0">測試模式:</span>
                  <span className="text-lg font-bold text-[#0066CC] flex-1">
                    {testConfig.testMode === 'vacuum' ? '真空幫浦' : testConfig.testMode === 'positive' ? '正壓幫浦' : '手動模式'}
                  </span>
                </div>
                <div className="flex items-start">
                  <span className="text-slate-400 font-medium w-20 flex-shrink-0">測試類型:</span>
                  <span className="text-lg font-bold text-[#0066CC] flex-1">
                    {testConfig.testType === 'pressure' ? '壓力測試' : '流量測試'}
                  </span>
                </div>
                <div className="flex items-start">
                  <span className="text-slate-400 font-medium w-20 flex-shrink-0">電源:</span>
                  <span className="text-lg font-bold text-[#0066CC] flex-1">{testConfig.powerSource || '-'}</span>
                </div>
                <div className="flex items-start">
                  <span className="text-slate-400 font-medium w-20 flex-shrink-0">額定功率:</span>
                  <span className="text-lg font-bold text-[#0066CC] flex-1">{testConfig.ratedPower} W</span>
                </div>
                <div className="flex items-start">
                  <span className="text-slate-400 font-medium w-20 flex-shrink-0">最大電流:</span>
                  <span className="text-lg font-bold text-[#0066CC] flex-1">{testConfig.maxCurrent} A</span>
                </div>
                <div className="flex items-start">
                  <span className="text-slate-400 font-medium w-20 flex-shrink-0">儲存目標:</span>
                  <span className="text-lg font-bold text-[#0066CC] flex-1">
                    {testConfig.saveTarget === 'test' ? '測試數據' : '參考數據'}
                  </span>
                </div>
                {testConfig.notes && (
                  <div className="flex items-start">
                    <span className="text-slate-400 font-medium w-20 flex-shrink-0">備註資料:</span>
                    <span className="text-lg font-bold text-[#0066CC] flex-1 break-words">{testConfig.notes}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* 右側：即時數值顯示 */}
        <div className="col-span-9">
          <div className="grid grid-cols-3 gap-4">
        <RealtimeValueCard
          title={testType === 'pressure' ? '即時壓力' : '即時流量'}
          value={currentData.value}
          unit={currentData.unit}
          valueColor={currentData.color}
          size="lg"
        />
        <RealtimeValueCard
          title="即時電流"
          value={realtimeCurrent.toFixed(1)}
          unit="A"
          valueColor="text-orange-800"
          size="lg"
        />
        <RealtimeValueCard
          title="即時功率"
          value={(realtimeCurrent * 24).toFixed(0)}
          unit="W"
          valueColor="text-purple-800"
          size="lg"
        />
          </div>
        </div>
      </div>

      {/* 圖表區域 - 混合改進風格 */}
      <div ref={chartRef} className="bg-white rounded-lg shadow-lg p-4 border-2 border-slate-300">
        <h2 className="text-lg font-bold text-slate-800 mb-3">
          {testType === 'pressure' ? '壓力' : '流量'}曲線圖
        </h2>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#D1D5DB" />
            <XAxis
              dataKey="time"
              label={{ value: '時間 (秒)', position: 'insideBottom', offset: -5, style: { fill: '#374151', fontWeight: 'bold' } }}
              stroke="#374151"
              tick={{ fill: '#374151', fontWeight: 'bold' }}
            />
            <YAxis
              label={{ value: getYAxisLabel(), angle: -90, position: 'insideLeft', style: { fill: '#374151', fontWeight: 'bold' } }}
              stroke="#374151"
              tick={{ fill: '#374151', fontWeight: 'bold' }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#FFFFFF', 
                border: '2px solid #9CA3AF',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
              }}
            />
            <Legend 
              wrapperStyle={{ fontWeight: 'bold' }}
            />
            <Line
              type="monotone"
              dataKey={testType === 'pressure' ? 'pressure' : 'flow'}
              stroke="#2563EB"
              strokeWidth={3}
              name={testType === 'pressure' ? '壓力 (kPa)' : `流量 (${currentData.unit})`}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="current"
              stroke="#EA580C"
              strokeWidth={3}
              name="電流 (A)"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>

        {/* 匯出與儲存按鈕 */}
        <div className="mt-4 flex gap-2">
          <button
            onClick={handleExport}
            disabled={chartData.length === 0}
            className="px-5 py-2 bg-blue-600 text-white text-sm font-bold rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
          >
            匯出 CSV + 圖表
          </button>
          <button
            onClick={handleSaveTest}
            disabled={chartData.length === 0}
            className="px-5 py-2 bg-green-600 text-white text-sm font-bold rounded-lg hover:bg-green-700 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
          >
            儲存為測試數據
          </button>
          <button
            onClick={handleSaveReference}
            disabled={chartData.length === 0}
            className="px-5 py-2 bg-purple-600 text-white text-sm font-bold rounded-lg hover:bg-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
          >
            儲存為參考數據
          </button>
        </div>
      </div>


      {/* Toast 通知 */}
      {toastMessage && (
        <Toast
          message={toastMessage}
          onClose={() => setToastMessage('')}
          type="info"
        />
      )}
    </div>
  );
}

export default MainDashboard;

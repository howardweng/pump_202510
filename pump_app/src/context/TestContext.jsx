// context/TestContext.jsx
import React, { createContext, useContext, useState, useRef } from 'react';

const TestContext = createContext();

export function TestProvider({ children }) {
  // 測試控制狀態
  const [testMode, setTestMode] = useState('vacuum'); // 'vacuum' | 'positive' | 'manual'
  const [testType, setTestType] = useState('pressure'); // 'pressure' | 'flow'
  const [testStatus, setTestStatus] = useState('idle'); // 'idle' | 'running' | 'paused' | 'stopped'
  const [testCompleted, setTestCompleted] = useState(false);

  // 即時數據
  const [realtimePressure, setRealtimePressure] = useState(0);
  const [realtimeCurrent, setRealtimeCurrent] = useState(0);
  const [realtimeFlow, setRealtimeFlow] = useState(0);

  // 圖表數據
  const [chartData, setChartData] = useState([]);
  const startTimeRef = useRef(null);

  // 系統狀態
  const [sensorStatus, setSensorStatus] = useState('正常'); // 統一感測器狀態 (壓力/流量)
  const [currentSensorStatus, setCurrentSensorStatus] = useState('正常');
  const [relayStatus, setRelayStatus] = useState('正常');

  // 電磁閥狀態
  const [valveStatus, setValveStatus] = useState({ A: false, B: false, C: false, D: false });

  // 參考數據
  const [selectedReference, setSelectedReference] = useState(null);
  const [referenceDataList, setReferenceDataList] = useState([]);

  // 測試配置
  const [testConfig, setTestConfig] = useState({
    pumpModel: '',
    testMode: 'vacuum',
    testType: 'pressure',
    powerSource: '',
    ratedPower: 0,
    maxCurrent: 0,
    saveTarget: 'test'
  });

  const value = {
    // 狀態
    testMode, setTestMode,
    testType, setTestType,
    testStatus, setTestStatus,
    testCompleted, setTestCompleted,
    realtimePressure, setRealtimePressure,
    realtimeCurrent, setRealtimeCurrent,
    realtimeFlow, setRealtimeFlow,
    chartData, setChartData,
    startTimeRef,
    sensorStatus, setSensorStatus,
    currentSensorStatus, setCurrentSensorStatus,
    relayStatus, setRelayStatus,
    valveStatus, setValveStatus,
    selectedReference, setSelectedReference,
    referenceDataList, setReferenceDataList,
    testConfig, setTestConfig
  };

  return (
    <TestContext.Provider value={value}>
      {children}
    </TestContext.Provider>
  );
}

export function useTest() {
  const context = useContext(TestContext);
  if (!context) {
    throw new Error('useTest must be used within TestProvider');
  }
  return context;
}

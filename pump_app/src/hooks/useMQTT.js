// hooks/useMQTT.js
import { useEffect, useRef } from 'react';
import mqtt from 'mqtt';
import config from '../config';
import { useTest } from '../context/TestContext';

export function useMQTT() {
  const mqttClient = useRef(null);
  const {
    testType,
    setRealtimePressure,
    setRealtimeCurrent,
    setRealtimeFlow,
    setChartData,
    setValveStatus,
    setSensorStatus,
    setCurrentSensorStatus,
    setRelayStatus,
    startTimeRef,
    testStatus
  } = useTest();

  const lastSensorUpdateRef = useRef(Date.now());
  const lastCurrentUpdateRef = useRef(Date.now());
  const lastRelayUpdateRef = useRef(Date.now());

  useEffect(() => {
    // 連接 MQTT
    mqttClient.current = mqtt.connect(config.mqttHost, {
      username: config.mqttUsername,
      password: config.mqttPassword,
      reconnectPeriod: 1000
    });

    mqttClient.current.on('connect', () => {
      console.log('✅ MQTT 連線成功');

      // 訂閱主題
      mqttClient.current.subscribe([
        'pump/sensors/pressure',
        'pump/sensors/current',
        'pump/sensors/flow',
        'pump/valves/status',
        'pump/system/status'
      ]);
    });

    mqttClient.current.on('message', (topic, message) => {
      try {
        const payload = JSON.parse(message.toString());

        if (topic === 'pump/sensors/pressure') {
          lastSensorUpdateRef.current = Date.now();
          setRealtimePressure(payload.value);

          // 如果是壓力測試且測試中,加入圖表數據
          if (testType === 'pressure' && testStatus === 'running' && startTimeRef.current) {
            const elapsedSec = (Date.now() - startTimeRef.current) / 1000;
            setChartData(prev => [...prev, {
              time: parseFloat(elapsedSec.toFixed(2)),
              pressure: payload.value,
              current: prev[prev.length - 1]?.current || 0,
              timestamp: Date.now()
            }]);
          }
        }

        if (topic === 'pump/sensors/current') {
          lastCurrentUpdateRef.current = Date.now();
          setRealtimeCurrent(payload.value);

          // 更新圖表中的電流數據
          if (testStatus === 'running' && startTimeRef.current) {
            setChartData(prev => {
              if (prev.length === 0) return prev;
              const lastIndex = prev.length - 1;
              const updated = [...prev];
              updated[lastIndex] = { ...updated[lastIndex], current: payload.value };
              return updated;
            });
          }
        }

        if (topic === 'pump/sensors/flow') {
          lastSensorUpdateRef.current = Date.now();
          setRealtimeFlow(payload.value);

          // 如果是流量測試且測試中,加入圖表數據
          if (testType === 'flow' && testStatus === 'running' && startTimeRef.current) {
            const elapsedSec = (Date.now() - startTimeRef.current) / 1000;
            setChartData(prev => [...prev, {
              time: parseFloat(elapsedSec.toFixed(2)),
              flow: payload.value,
              current: prev[prev.length - 1]?.current || 0,
              timestamp: Date.now()
            }]);
          }
        }

        if (topic === 'pump/valves/status') {
          setValveStatus(payload);
        }

        if (topic.startsWith('pump/relay/')) {
          lastRelayUpdateRef.current = Date.now();
        }

      } catch (error) {
        console.error('❌ MQTT 訊息解析錯誤:', error);
      }
    });

    mqttClient.current.on('error', (err) => {
      console.error('❌ MQTT 連線錯誤:', err);
    });

    // 狀態監測定時器
    const statusCheckInterval = setInterval(() => {
      const now = Date.now();

      // 檢查壓力/流量感測器 (統一)
      if (now - lastSensorUpdateRef.current > 1500) {
        setSensorStatus('錯誤');
      } else {
        setSensorStatus('正常');
      }

      // 檢查電流感測器
      if (now - lastCurrentUpdateRef.current > 1500) {
        setCurrentSensorStatus('錯誤');
      } else {
        setCurrentSensorStatus('正常');
      }

      // 檢查繼電器
      if (now - lastRelayUpdateRef.current > 1500) {
        setRelayStatus('錯誤');
      } else {
        setRelayStatus('正常');
      }
    }, 1000);

    // 清理
    return () => {
      clearInterval(statusCheckInterval);
      if (mqttClient.current) {
        mqttClient.current.end();
      }
    };
  }, [testStatus, testType, setRealtimePressure, setRealtimeCurrent, setRealtimeFlow, setChartData, setValveStatus, setSensorStatus, setCurrentSensorStatus, setRelayStatus, startTimeRef]);

  // 發送 MQTT 指令
  const publishCommand = (topic, message) => {
    if (mqttClient.current && mqttClient.current.connected) {
      mqttClient.current.publish(topic, JSON.stringify(message));
      console.log(`📤 發送 MQTT: ${topic}`, message);
    }
  };

  return { publishCommand };
}

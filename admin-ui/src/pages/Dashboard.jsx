import React, { useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getDevices, updateDevice } from '../api/devices'
import { useMQTT } from '../hooks/useMQTT'

function Dashboard() {
  const queryClient = useQueryClient()
  const { data: devices, isLoading, error } = useQuery({
    queryKey: ['devices'],
    queryFn: getDevices,
    refetchInterval: 5000, // 每 5 秒刷新一次（減少頻率以避免閃爍）
    staleTime: 3000, // 數據在 3 秒內被視為新鮮，不會自動重新獲取
  })

  // 更新設備狀態的 mutation
  const updateDeviceMutation = useMutation({
    mutationFn: ({ deviceId, enabled }) => updateDevice(deviceId, { enabled }),
    onSuccess: () => {
      // 更新成功後，重新獲取設備列表
      queryClient.invalidateQueries({ queryKey: ['devices'] })
    },
  })

  // 更新設備配置的 mutation
  const updateConfigMutation = useMutation({
    mutationFn: ({ deviceId, config }) => updateDevice(deviceId, { config }),
    onSuccess: () => {
      // 更新成功後，重新獲取設備列表
      queryClient.invalidateQueries({ queryKey: ['devices'] })
    },
  })

  // 調試信息
  console.log('Dashboard render:', {
    isLoading,
    hasError: !!error,
    errorMessage: error?.message,
    devicesCount: devices?.length,
    devices: devices
  })

  if (isLoading) {
    return <div className="text-center py-8 text-slate-700">載入中...</div>
  }

  if (error) {
    console.error('Dashboard error:', error)
    return <div className="text-center py-8 text-red-500">錯誤: {error.message}</div>
  }

  if (!devices || devices.length === 0) {
    return (
      <div>
        <h2 className="text-3xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">設備狀態總覽</h2>
        <div className="text-center py-8 text-slate-500">沒有設備數據</div>
      </div>
    )
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'enabled':
        return 'bg-emerald-400 shadow-lg shadow-emerald-400/50'
      case 'disabled':
        return 'bg-slate-400'
      case 'error':
        return 'bg-rose-500 shadow-lg shadow-rose-500/50'
      default:
        return 'bg-slate-400'
    }
  }

  const getDeviceTypeName = (type) => {
    const typeMap = {
      flow_meter: '流量計',
      pressure_sensor: '壓力計',
      single_phase_power_meter: '單相電表',
      three_phase_power_meter: '三相電表',
      relay_io: '繼電器 IO',
    }
    return typeMap[type] || type
  }

  // 處理開關切換
  const handleToggle = async (deviceId, currentEnabled) => {
    const newEnabled = !currentEnabled
    try {
      await updateDeviceMutation.mutateAsync({ deviceId, enabled: newEnabled })
    } catch (error) {
      console.error('更新設備狀態失敗:', error)
      alert(`更新設備狀態失敗: ${error.message}`)
    }
  }

  // 處理配置更新
  const handleConfigUpdate = async (deviceId, configKey, value) => {
    try {
      // 獲取當前設備配置
      const device = devices.find(d => d.id === deviceId)
      if (!device) return

      // 更新配置
      const newConfig = {
        ...device.config,
        [configKey]: Array.isArray(value) ? value : (parseFloat(value) || 0)
      }

      await updateConfigMutation.mutateAsync({ deviceId, config: newConfig })
    } catch (error) {
      console.error('更新設備配置失敗:', error)
      alert(`更新設備配置失敗: ${error.message}`)
    }
  }

  // 實時數據顯示組件
  const RealtimeDataDisplay = React.memo(({ device }) => {
    const { realtimeData, lastUpdate } = useMQTT(device.id, device.type, device.enabled)

    // 使用 useMemo 穩定 raw_registers 數據，避免閃爍
    // 使用 JSON.stringify 進行深度比較，而不是對象引用比較
    const stableRawRegisters = useMemo(() => {
      return realtimeData?.raw_registers || null
    }, [JSON.stringify(realtimeData?.raw_registers)])

    if (!device.enabled) {
      return (
        <div className="mt-4 pt-4 border-t border-slate-200">
          <div className="bg-slate-100 p-3 rounded-lg">
            <div className="text-sm font-semibold text-slate-500 mb-1">實時數據</div>
            <div className="text-xs text-slate-400">設備已停止 - 無數據</div>
          </div>
        </div>
      )
    }

    if (!realtimeData) {
      return (
        <div className="mt-4 pt-4 border-t border-slate-200">
          <div className="bg-amber-50 p-3 rounded-lg border border-amber-200">
            <div className="text-sm font-semibold text-amber-700 mb-1">實時數據</div>
            <div className="text-xs text-amber-600">等待數據中...</div>
          </div>
        </div>
      )
    }

    const formatTime = (date) => {
      if (!date) return '未知'
      return date.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    }

    const renderData = () => {
      switch (device.type) {
        case 'flow_meter':
          return (
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-xs text-slate-600">瞬时流量:</span>
                <span className="text-sm font-bold text-blue-600">
                  {realtimeData.instantaneous_flow?.toFixed(2) || 'N/A'} L/min
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-slate-600">累積流量:</span>
                <span className="text-sm font-bold text-indigo-600">
                  {realtimeData.cumulative_flow?.toFixed(2) || 'N/A'} L
                </span>
              </div>
              <div className="text-xs text-slate-500 mt-2 pt-2 border-t border-slate-200">
                💡 解釋: 流量計正在讀取水流數據，瞬时流量表示當前流速，累積流量表示總流量
              </div>
            </div>
          )
        
        case 'pressure_sensor':
          const unit = device.id.includes('vacuum') ? 'kPa' : 'kg/cm²'
          return (
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-xs text-slate-600">壓力值:</span>
                <span className="text-sm font-bold text-rose-600">
                  {realtimeData.pressure?.toFixed(2) || 'N/A'} {unit}
                </span>
              </div>
              <div className="text-xs text-slate-500 mt-2 pt-2 border-t border-slate-200">
                💡 解釋: 壓力感測器正在讀取壓力數據，{device.id.includes('vacuum') ? '真空壓力' : '正壓'}值應與配置值一致
              </div>
            </div>
          )
        
        case 'single_phase_power_meter':
          return (
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-xs text-slate-600">電壓:</span>
                <span className="text-sm font-bold text-amber-600">
                  {realtimeData.voltage?.toFixed(1) || 'N/A'} V
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-slate-600">電流:</span>
                <span className="text-sm font-bold text-emerald-600">
                  {realtimeData.current?.toFixed(2) || 'N/A'} A
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-slate-600">功率:</span>
                <span className="text-sm font-bold text-purple-600">
                  {realtimeData.active_power?.toFixed(1) || 'N/A'} W
                </span>
              </div>
              <div className="text-xs text-slate-500 mt-2 pt-2 border-t border-slate-200">
                💡 解釋: 電表正在讀取電力數據，電壓×電流≈功率，數據應與配置值一致
              </div>
            </div>
          )
        
        case 'three_phase_power_meter':
          return (
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-xs text-slate-600">合相功率:</span>
                <span className="text-sm font-bold text-violet-600">
                  {realtimeData.power_total?.toFixed(2) || 'N/A'} kW
                </span>
              </div>
              <div className="grid grid-cols-3 gap-1 text-xs">
                <div>
                  <span className="text-slate-500">A相:</span>
                  <span className="ml-1 font-semibold text-slate-700">
                    {realtimeData.voltage_a?.toFixed(0) || 'N/A'}V
                  </span>
                </div>
                <div>
                  <span className="text-slate-500">B相:</span>
                  <span className="ml-1 font-semibold text-slate-700">
                    {realtimeData.voltage_b?.toFixed(0) || 'N/A'}V
                  </span>
                </div>
                <div>
                  <span className="text-slate-500">C相:</span>
                  <span className="ml-1 font-semibold text-slate-700">
                    {realtimeData.voltage_c?.toFixed(0) || 'N/A'}V
                  </span>
                </div>
              </div>
              <div className="text-xs text-slate-500 mt-2 pt-2 border-t border-slate-200">
                💡 解釋: 三相電表正在讀取三相電力數據，合相功率為三相功率總和
              </div>
            </div>
          )
        
        default:
          return (
            <div className="text-xs text-slate-500">
              <pre className="bg-slate-50 p-2 rounded text-xs overflow-x-auto">
                {JSON.stringify(realtimeData, null, 2)}
              </pre>
            </div>
          )
      }
    }

    return (
      <div className="mt-4 pt-4 border-t border-slate-200">
        <div className="bg-gradient-to-br from-emerald-50 to-teal-50 p-3 rounded-lg border border-emerald-200">
          <div className="flex justify-between items-center mb-2">
            <div className="text-sm font-semibold text-emerald-700">實時數據</div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
              <span className="text-xs text-emerald-600">{formatTime(lastUpdate)}</span>
            </div>
          </div>
          {renderData()}
          
          {/* 寄存器原始數據顯示 - 使用穩定的數據避免閃爍 */}
          {stableRawRegisters && (
            <div className="mt-3 pt-3 border-t border-emerald-200">
              <div className="text-xs font-semibold text-emerald-700 mb-2">📡 Modbus 寄存器原始數據</div>
              <div className="space-y-2">
                {/* 完整響應格式 */}
                <div className="text-xs">
                  <span className="text-slate-600 font-medium">完整響應 (Slave+FC+Len+Data):</span>
                  <code className="ml-2 px-2 py-1 bg-slate-900 text-emerald-400 font-mono rounded text-xs break-all">
                    {stableRawRegisters.hex_raw || 'N/A'}
                  </code>
                </div>
                
                {/* 寄存器詳細列表 */}
                {stableRawRegisters.register_map && stableRawRegisters.register_map.length > 0 && (
                  <div className="text-xs">
                    <span className="text-slate-600 font-medium mb-1 block">寄存器詳細值:</span>
                    <div className="bg-slate-50 rounded p-2 max-h-32 overflow-y-auto">
                      <div className="grid grid-cols-1 gap-1">
                        {stableRawRegisters.register_map.map((reg, idx) => (
                          <div key={`${reg.address_hex}-${reg.value}-${idx}`} className="flex items-center justify-between text-xs font-mono">
                            <span className="text-slate-600">
                              {reg.address_hex}:
                            </span>
                            <span className="text-slate-800 font-semibold">
                              {reg.value} (0x{reg.value.toString(16).toUpperCase().padStart(4, '0')})
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
                
                {/* 元數據 */}
                <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500 pt-1 border-t border-slate-200">
                  <span>起始: 0x{stableRawRegisters.start_address?.toString(16).toUpperCase().padStart(4, '0') || '0000'}</span>
                  <span>•</span>
                  <span>數量: {stableRawRegisters.count || 0}</span>
                  <span>•</span>
                  <span>Slave: {stableRawRegisters.slave_id || 'N/A'}</span>
                  <span>•</span>
                  <span>FC: 0x{(stableRawRegisters.function_code || 3).toString(16).toUpperCase().padStart(2, '0')}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }, (prevProps, nextProps) => {
    // 自定義比較函數，只在設備 ID 或 enabled 狀態改變時重新渲染
    return prevProps.device.id === nextProps.device.id && 
           prevProps.device.enabled === nextProps.device.enabled
  })

  return (
    <div>
      <h2 className="text-3xl font-bold mb-6 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">設備狀態總覽</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {devices?.map((device) => (
          <div
            key={device.id}
            className="bg-gradient-to-br from-white to-slate-50 rounded-xl shadow-lg border border-slate-200 p-6 hover:shadow-xl hover:scale-[1.02] transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-4 pb-4 border-b border-slate-200">
              <h3 className="text-xl font-bold text-slate-800">{device.name}</h3>
              <div className="flex items-center gap-3">
                <div className={`w-4 h-4 rounded-full ${getStatusColor(device.status)} animate-pulse`}></div>
                {/* 現代化開關切換 */}
                <label className="relative inline-flex items-center cursor-pointer group">
                  <input
                    type="checkbox"
                    checked={device.enabled}
                    onChange={() => handleToggle(device.id, device.enabled)}
                    disabled={updateDeviceMutation.isPending}
                    className="sr-only peer"
                  />
                  {/* 開關背景 */}
                  <div className="relative w-14 h-7 bg-gradient-to-r from-slate-300 via-slate-400 to-slate-500 rounded-full shadow-inner transition-all duration-300 ease-in-out peer-checked:bg-gradient-to-r peer-checked:from-emerald-400 peer-checked:via-emerald-500 peer-checked:to-teal-500 peer-checked:shadow-lg peer-checked:shadow-emerald-500/50 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300/50 peer-focus:ring-offset-2">
                    {/* 開關按鈕 */}
                    <div className="absolute top-0.5 left-0.5 w-6 h-6 bg-white rounded-full shadow-lg transform transition-transform duration-300 ease-in-out peer-checked:translate-x-7 peer-checked:shadow-xl flex items-center justify-center">
                      {/* 開啟狀態圖標 (✓) */}
                      <svg className="w-3.5 h-3.5 text-emerald-500 opacity-0 peer-checked:opacity-100 transition-opacity duration-200 absolute" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                  </div>
                  {/* 狀態文字 */}
                  <span className={`ml-3 text-sm font-bold transition-colors duration-200 ${device.enabled ? 'text-emerald-600' : 'text-slate-500'}`}>
                    {device.enabled ? 'ON' : 'OFF'}
                  </span>
                </label>
              </div>
            </div>
            
            <div className="space-y-2 text-sm text-slate-600 mb-4">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-indigo-600">類型:</span> 
                <span className="text-slate-700">{getDeviceTypeName(device.type)}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-indigo-600">Slave ID:</span> 
                <span className="px-2 py-0.5 bg-indigo-100 text-indigo-700 rounded font-mono text-xs">{device.slave_id}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-indigo-600">端口:</span> 
                <span className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded font-mono text-xs">{device.port}</span>
              </div>
            </div>

            {/* 可編輯的配置值 */}
            <div className="mt-4 pt-4 border-t border-slate-200">
              <div className="space-y-3">
                {device.type === 'flow_meter' && (
                  <>
                    <div className="flex items-center justify-between bg-blue-50 p-2 rounded-lg">
                      <label className="text-sm font-semibold text-blue-700">瞬时流量 (L/min):</label>
                      <input
                        type="number"
                        step="0.1"
                        defaultValue={device.config.instantaneous_flow}
                        onBlur={(e) => handleConfigUpdate(device.id, 'instantaneous_flow', e.target.value)}
                        className="w-24 px-3 py-1.5 text-sm border-2 border-blue-200 rounded-lg bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-400 transition-all"
                      />
                    </div>
                    <div className="flex items-center justify-between bg-indigo-50 p-2 rounded-lg">
                      <label className="text-sm font-semibold text-indigo-700">累積流量:</label>
                      <input
                        type="number"
                        step="0.1"
                        defaultValue={device.config.cumulative_flow}
                        onBlur={(e) => handleConfigUpdate(device.id, 'cumulative_flow', e.target.value)}
                        className="w-24 px-3 py-1.5 text-sm border-2 border-indigo-200 rounded-lg bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-400 transition-all"
                      />
                    </div>
                  </>
                )}
                {device.type === 'pressure_sensor' && (
                  <div className="flex items-center justify-between bg-rose-50 p-2 rounded-lg">
                    <label className="text-sm font-semibold text-rose-700">
                      壓力 ({device.id.includes('vacuum') ? 'kPa' : 'kg/cm²'}):
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      defaultValue={device.config.pressure}
                      onBlur={(e) => handleConfigUpdate(device.id, 'pressure', e.target.value)}
                      className="w-24 px-3 py-1.5 text-sm border-2 border-rose-200 rounded-lg bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-rose-500 focus:border-rose-400 transition-all"
                    />
                  </div>
                )}
                {device.type === 'single_phase_power_meter' && (
                  <>
                    <div className="flex items-center justify-between bg-amber-50 p-2 rounded-lg">
                      <label className="text-sm font-semibold text-amber-700">電壓 (V):</label>
                      <input
                        type="number"
                        step="0.1"
                        defaultValue={device.config.voltage}
                        onBlur={(e) => handleConfigUpdate(device.id, 'voltage', e.target.value)}
                        className="w-24 px-3 py-1.5 text-sm border-2 border-amber-200 rounded-lg bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-amber-400 transition-all"
                      />
                    </div>
                    <div className="flex items-center justify-between bg-emerald-50 p-2 rounded-lg">
                      <label className="text-sm font-semibold text-emerald-700">電流 (A):</label>
                      <input
                        type="number"
                        step="0.1"
                        defaultValue={device.config.current}
                        onBlur={(e) => handleConfigUpdate(device.id, 'current', e.target.value)}
                        className="w-24 px-3 py-1.5 text-sm border-2 border-emerald-200 rounded-lg bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-400 transition-all"
                      />
                    </div>
                    <div className="flex items-center justify-between bg-purple-50 p-2 rounded-lg">
                      <label className="text-sm font-semibold text-purple-700">有功功率 (W):</label>
                      <input
                        type="number"
                        step="0.1"
                        defaultValue={device.config.active_power}
                        onBlur={(e) => handleConfigUpdate(device.id, 'active_power', e.target.value)}
                        className="w-24 px-3 py-1.5 text-sm border-2 border-purple-200 rounded-lg bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-400 transition-all"
                      />
                    </div>
                  </>
                )}
                {device.type === 'three_phase_power_meter' && (
                  <>
                    <div className="flex items-center justify-between bg-violet-50 p-2 rounded-lg">
                      <label className="text-sm font-semibold text-violet-700">合相功率 (kW):</label>
                      <input
                        type="number"
                        step="0.1"
                        defaultValue={device.config.power_total}
                        onBlur={(e) => handleConfigUpdate(device.id, 'power_total', e.target.value)}
                        className="w-24 px-3 py-1.5 text-sm border-2 border-violet-200 rounded-lg bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-violet-400 transition-all"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs bg-slate-50 p-2 rounded-lg">
                      <div className="flex items-center justify-between">
                        <span className="text-slate-600 font-medium">電壓 A:</span>
                        <input
                          type="number"
                          step="0.1"
                          defaultValue={device.config.voltage_a}
                          onBlur={(e) => handleConfigUpdate(device.id, 'voltage_a', e.target.value)}
                          className="w-16 px-1.5 py-1 text-xs border-2 border-slate-200 rounded bg-white text-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-400 transition-all"
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-600 font-medium">電壓 B:</span>
                        <input
                          type="number"
                          step="0.1"
                          defaultValue={device.config.voltage_b}
                          onBlur={(e) => handleConfigUpdate(device.id, 'voltage_b', e.target.value)}
                          className="w-16 px-1.5 py-1 text-xs border-2 border-slate-200 rounded bg-white text-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-400 transition-all"
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-600 font-medium">電壓 C:</span>
                        <input
                          type="number"
                          step="0.1"
                          defaultValue={device.config.voltage_c}
                          onBlur={(e) => handleConfigUpdate(device.id, 'voltage_c', e.target.value)}
                          className="w-16 px-1.5 py-1 text-xs border-2 border-slate-200 rounded bg-white text-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-400 transition-all"
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-600 font-medium">電流 A:</span>
                        <input
                          type="number"
                          step="0.1"
                          defaultValue={device.config.current_a}
                          onBlur={(e) => handleConfigUpdate(device.id, 'current_a', e.target.value)}
                          className="w-16 px-1.5 py-1 text-xs border-2 border-slate-200 rounded bg-white text-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-400 transition-all"
                        />
                      </div>
                    </div>
                  </>
                )}
                {device.type === 'relay_io' && (
                  <div className="bg-slate-50 p-3 rounded-lg">
                    <div className="mb-3 text-sm font-semibold text-slate-700">
                      繼電器狀態: <span className="text-emerald-600">{device.config.relay_states.filter(Boolean).length}/8</span> 開啟
                    </div>
                    <div className="grid grid-cols-4 gap-2">
                      {device.config.relay_states.map((state, index) => (
                        <label key={index} className="flex items-center gap-1.5 cursor-pointer p-1.5 rounded hover:bg-white transition-colors">
                          <input
                            type="checkbox"
                            checked={state}
                            onChange={(e) => {
                              const newStates = [...device.config.relay_states]
                              newStates[index] = e.target.checked
                              handleConfigUpdate(device.id, 'relay_states', newStates)
                            }}
                            className="w-4 h-4 text-indigo-600 border-2 border-slate-300 rounded focus:ring-2 focus:ring-indigo-500 focus:ring-offset-1 cursor-pointer"
                          />
                          <span className="text-xs font-medium text-slate-700">R{index + 1}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* 實時數據顯示 */}
            <RealtimeDataDisplay device={device} />
          </div>
        ))}
      </div>
    </div>
  )
}

export default Dashboard




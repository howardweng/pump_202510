import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getDevices, updateDevice } from '../api/devices'

function Dashboard() {
  const queryClient = useQueryClient()
  const { data: devices, isLoading, error } = useQuery({
    queryKey: ['devices'],
    queryFn: getDevices,
    refetchInterval: 2000, // 每 2 秒刷新一次
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
                {/* 開關切換 */}
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={device.enabled}
                    onChange={() => handleToggle(device.id, device.enabled)}
                    disabled={updateDeviceMutation.isPending}
                    className="sr-only peer"
                  />
                  <div className="w-12 h-6 bg-gradient-to-r from-slate-300 to-slate-400 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-gradient-to-r peer-checked:from-emerald-500 peer-checked:to-teal-500 shadow-lg"></div>
                  <span className={`ml-3 text-sm font-semibold ${device.enabled ? 'text-emerald-600' : 'text-slate-500'}`}>
                    {device.enabled ? '開啟' : '關閉'}
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
          </div>
        ))}
      </div>
    </div>
  )
}

export default Dashboard




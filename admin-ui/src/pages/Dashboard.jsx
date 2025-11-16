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

  // 調試信息
  console.log('Dashboard render:', {
    isLoading,
    hasError: !!error,
    errorMessage: error?.message,
    devicesCount: devices?.length,
    devices: devices
  })

  if (isLoading) {
    return <div className="text-center py-8 text-gray-900">載入中...</div>
  }

  if (error) {
    console.error('Dashboard error:', error)
    return <div className="text-center py-8 text-red-600">錯誤: {error.message}</div>
  }

  if (!devices || devices.length === 0) {
    return (
      <div>
        <h2 className="text-3xl font-bold mb-6 text-gray-900">設備狀態總覽</h2>
        <div className="text-center py-8 text-gray-600">沒有設備數據</div>
      </div>
    )
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'enabled':
        return 'bg-green-500'
      case 'disabled':
        return 'bg-gray-500'
      case 'error':
        return 'bg-red-500'
      default:
        return 'bg-gray-500'
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

  return (
    <div>
      <h2 className="text-3xl font-bold mb-6 text-gray-900">設備狀態總覽</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {devices?.map((device) => (
          <div
            key={device.id}
            className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold">{device.name}</h3>
              <div className="flex items-center gap-3">
                <div className={`w-3 h-3 rounded-full ${getStatusColor(device.status)}`}></div>
                {/* 開關切換 */}
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={device.enabled}
                    onChange={() => handleToggle(device.id, device.enabled)}
                    disabled={updateDeviceMutation.isPending}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  <span className="ml-3 text-sm font-medium text-gray-700">
                    {device.enabled ? '開啟' : '關閉'}
                  </span>
                </label>
              </div>
            </div>
            
            <div className="space-y-2 text-sm text-gray-600">
              <div>
                <span className="font-medium">類型:</span> {getDeviceTypeName(device.type)}
              </div>
              <div>
                <span className="font-medium">Slave ID:</span> {device.slave_id}
              </div>
              <div>
                <span className="font-medium">端口:</span> {device.port}
              </div>
            </div>

            {/* 顯示關鍵配置值 */}
            <div className="mt-4 pt-4 border-t">
              <div className="text-xs text-gray-500">
                {device.type === 'flow_meter' && (
                  <div>
                    瞬时流量: {device.config.instantaneous_flow} L/min
                  </div>
                )}
                {device.type === 'pressure_sensor' && (
                  <div>
                    壓力: {device.config.pressure} {device.id.includes('vacuum') ? 'kPa' : 'kg/cm²'}
                  </div>
                )}
                {device.type === 'single_phase_power_meter' && (
                  <div>
                    電壓: {device.config.voltage} V<br />
                    電流: {device.config.current} A
                  </div>
                )}
                {device.type === 'three_phase_power_meter' && (
                  <div>
                    合相功率: {device.config.power_total} kW
                  </div>
                )}
                {device.type === 'relay_io' && (
                  <div>
                    繼電器狀態: {device.config.relay_states.filter(Boolean).length}/8 開啟
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




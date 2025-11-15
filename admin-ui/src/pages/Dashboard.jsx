import { useQuery } from '@tanstack/react-query'
import { getDevices } from '../api/devices'

function Dashboard() {
  const { data: devices, isLoading, error } = useQuery({
    queryKey: ['devices'],
    queryFn: getDevices,
    refetchInterval: 2000, // 每 2 秒刷新一次
  })

  if (isLoading) {
    return <div className="text-center py-8">載入中...</div>
  }

  if (error) {
    return <div className="text-center py-8 text-red-600">錯誤: {error.message}</div>
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

  return (
    <div>
      <h2 className="text-3xl font-bold mb-6">設備狀態總覽</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {devices?.map((device) => (
          <div
            key={device.id}
            className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold">{device.name}</h3>
              <div className={`w-3 h-3 rounded-full ${getStatusColor(device.status)}`}></div>
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
              <div>
                <span className="font-medium">狀態:</span>{' '}
                <span className={device.enabled ? 'text-green-600' : 'text-gray-600'}>
                  {device.enabled ? '啟用' : '停用'}
                </span>
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


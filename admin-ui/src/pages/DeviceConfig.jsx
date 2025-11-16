import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getDevices, updateDevice } from '../api/devices'

function DeviceConfig() {
  const queryClient = useQueryClient()
  const [selectedDevice, setSelectedDevice] = useState(null)
  const [formData, setFormData] = useState({})

  const { data: devices, isLoading } = useQuery({
    queryKey: ['devices'],
    queryFn: getDevices,
  })

  const updateMutation = useMutation({
    mutationFn: ({ deviceId, update }) => updateDevice(deviceId, update),
    onSuccess: () => {
      queryClient.invalidateQueries(['devices'])
      alert('設備已更新')
    },
    onError: (error) => {
      alert(`更新失敗: ${error.message}`)
    },
  })

  const handleDeviceSelect = (device) => {
    setSelectedDevice(device)
    setFormData({
      enabled: device.enabled,
      ...device.config,
    })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!selectedDevice) return

    const update = {
      enabled: formData.enabled,
      config: { ...formData },
    }
    delete update.config.enabled

    updateMutation.mutate({
      deviceId: selectedDevice.id,
      update,
    })
  }

  const handleInputChange = (key, value) => {
    setFormData((prev) => ({
      ...prev,
      [key]: value,
    }))
  }

  if (isLoading) {
    return <div className="text-center py-8">載入中...</div>
  }

  return (
    <div>
      <h2 className="text-3xl font-bold mb-6">設備配置</h2>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 設備列表 */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md p-4">
            <h3 className="text-lg font-semibold mb-4">選擇設備</h3>
            <div className="space-y-2">
              {devices?.map((device) => (
                <button
                  key={device.id}
                  onClick={() => handleDeviceSelect(device)}
                  className={`w-full text-left px-4 py-2 rounded ${
                    selectedDevice?.id === device.id
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100 hover:bg-gray-200'
                  }`}
                >
                  {device.name}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 配置表單 */}
        <div className="lg:col-span-2">
          {selectedDevice ? (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-semibold mb-4">{selectedDevice.name} 配置</h3>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* 啟用/停用 */}
                <div>
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={formData.enabled || false}
                      onChange={(e) => handleInputChange('enabled', e.target.checked)}
                      className="w-4 h-4"
                    />
                    <span>啟用設備</span>
                  </label>
                </div>

                {/* 根據設備類型顯示不同的配置項 */}
                {selectedDevice.type === 'flow_meter' && (
                  <>
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        瞬时流量 (L/min)
                      </label>
                      <input
                        type="number"
                        step="0.1"
                        value={formData.instantaneous_flow || 0}
                        onChange={(e) => handleInputChange('instantaneous_flow', parseFloat(e.target.value))}
                        className="w-full px-3 py-2 border rounded"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        累計流量 (L)
                      </label>
                      <input
                        type="number"
                        step="0.1"
                        value={formData.cumulative_flow || 0}
                        onChange={(e) => handleInputChange('cumulative_flow', parseFloat(e.target.value))}
                        className="w-full px-3 py-2 border rounded"
                      />
                    </div>
                  </>
                )}

                {selectedDevice.type === 'pressure_sensor' && (
                  <div>
                    <label className="block text-sm font-medium mb-1">
                      壓力 ({selectedDevice.id.includes('vacuum') ? 'kPa' : 'kg/cm²'})
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      value={formData.pressure || 0}
                      onChange={(e) => handleInputChange('pressure', parseFloat(e.target.value))}
                      className="w-full px-3 py-2 border rounded"
                    />
                  </div>
                )}

                {selectedDevice.type === 'single_phase_power_meter' && (
                  <>
                    <div>
                      <label className="block text-sm font-medium mb-1">電壓 (V)</label>
                      <input
                        type="number"
                        step="0.1"
                        value={formData.voltage || 0}
                        onChange={(e) => handleInputChange('voltage', parseFloat(e.target.value))}
                        className="w-full px-3 py-2 border rounded"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">電流 (A)</label>
                      <input
                        type="number"
                        step="0.1"
                        value={formData.current || 0}
                        onChange={(e) => handleInputChange('current', parseFloat(e.target.value))}
                        className="w-full px-3 py-2 border rounded"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">有功功率 (kW)</label>
                      <input
                        type="number"
                        step="0.1"
                        value={formData.active_power || 0}
                        onChange={(e) => handleInputChange('active_power', parseFloat(e.target.value))}
                        className="w-full px-3 py-2 border rounded"
                      />
                    </div>
                  </>
                )}

                {selectedDevice.type === 'three_phase_power_meter' && (
                  <>
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-1">A 相電壓 (V)</label>
                        <input
                          type="number"
                          step="0.1"
                          value={formData.voltage_a || 0}
                          onChange={(e) => handleInputChange('voltage_a', parseFloat(e.target.value))}
                          className="w-full px-3 py-2 border rounded"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1">B 相電壓 (V)</label>
                        <input
                          type="number"
                          step="0.1"
                          value={formData.voltage_b || 0}
                          onChange={(e) => handleInputChange('voltage_b', parseFloat(e.target.value))}
                          className="w-full px-3 py-2 border rounded"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1">C 相電壓 (V)</label>
                        <input
                          type="number"
                          step="0.1"
                          value={formData.voltage_c || 0}
                          onChange={(e) => handleInputChange('voltage_c', parseFloat(e.target.value))}
                          className="w-full px-3 py-2 border rounded"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">合相功率 (kW)</label>
                      <input
                        type="number"
                        step="0.1"
                        value={formData.power_total || 0}
                        onChange={(e) => handleInputChange('power_total', parseFloat(e.target.value))}
                        className="w-full px-3 py-2 border rounded"
                      />
                    </div>
                  </>
                )}

                <button
                  type="submit"
                  disabled={updateMutation.isPending}
                  className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 disabled:bg-gray-400"
                >
                  {updateMutation.isPending ? '更新中...' : '更新設備'}
                </button>
              </form>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-md p-6 text-center text-gray-500">
              請選擇一個設備進行配置
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default DeviceConfig




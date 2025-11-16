import apiClient from './client'

export const getDevices = async () => {
  const response = await apiClient.get('/api/devices/')  // 添加尾隨斜線以匹配 FastAPI 路由
  return response.data
}

export const getDevice = async (deviceId) => {
  const response = await apiClient.get(`/api/devices/${deviceId}`)
  return response.data
}

export const updateDevice = async (deviceId, update) => {
  const response = await apiClient.put(`/api/devices/${deviceId}`, update)
  return response.data
}




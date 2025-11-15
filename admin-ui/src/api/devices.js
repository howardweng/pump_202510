import apiClient from './client'

export const getDevices = async () => {
  const response = await apiClient.get('/api/devices')
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


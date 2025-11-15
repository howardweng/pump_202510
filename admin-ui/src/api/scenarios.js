import apiClient from './client'

export const getScenarios = async () => {
  const response = await apiClient.get('/api/scenarios')
  return response.data
}

export const getScenario = async (scenarioId) => {
  const response = await apiClient.get(`/api/scenarios/${scenarioId}`)
  return response.data
}

export const createScenario = async (scenario) => {
  const response = await apiClient.post('/api/scenarios', scenario)
  return response.data
}

export const updateScenario = async (scenarioId, update) => {
  const response = await apiClient.put(`/api/scenarios/${scenarioId}`, update)
  return response.data
}

export const deleteScenario = async (scenarioId) => {
  const response = await apiClient.delete(`/api/scenarios/${scenarioId}`)
  return response.data
}


import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getScenarios, createScenario, updateScenario, deleteScenario } from '../api/scenarios'

function Scenarios() {
  const queryClient = useQueryClient()
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    device_configs: {},
  })

  const { data: scenariosData, isLoading } = useQuery({
    queryKey: ['scenarios'],
    queryFn: getScenarios,
  })

  const createMutation = useMutation({
    mutationFn: createScenario,
    onSuccess: () => {
      queryClient.invalidateQueries(['scenarios'])
      setShowCreateForm(false)
      setFormData({ name: '', description: '', device_configs: {} })
      alert('場景已創建')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: deleteScenario,
    onSuccess: () => {
      queryClient.invalidateQueries(['scenarios'])
      alert('場景已刪除')
    },
  })

  const handleCreate = (e) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  const handleDelete = (scenarioId) => {
    if (window.confirm('確定要刪除此場景嗎？')) {
      deleteMutation.mutate(scenarioId)
    }
  }

  if (isLoading) {
    return <div className="text-center py-8">載入中...</div>
  }

  const scenarios = scenariosData?.scenarios || []

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold">場景管理</h2>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          {showCreateForm ? '取消' : '創建場景'}
        </button>
      </div>

      {/* 創建表單 */}
      {showCreateForm && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-xl font-semibold mb-4">創建新場景</h3>
          <form onSubmit={handleCreate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">場景名稱</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border rounded"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">描述</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-3 py-2 border rounded"
                rows="3"
              />
            </div>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 disabled:bg-gray-400"
            >
              {createMutation.isPending ? '創建中...' : '創建場景'}
            </button>
          </form>
        </div>
      )}

      {/* 場景列表 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {scenarios.length === 0 ? (
          <div className="col-span-full text-center py-8 text-gray-500">
            尚無場景，請創建一個新場景
          </div>
        ) : (
          scenarios.map((scenario) => (
            <div
              key={scenario.id}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-semibold">{scenario.name}</h3>
                  {scenario.description && (
                    <p className="text-sm text-gray-600 mt-1">{scenario.description}</p>
                  )}
                </div>
                <button
                  onClick={() => handleDelete(scenario.id)}
                  className="text-red-500 hover:text-red-700"
                >
                  刪除
                </button>
              </div>
              
              <div className="text-sm text-gray-500">
                <div>設備數量: {Object.keys(scenario.device_configs || {}).length}</div>
                <div>創建時間: {new Date(scenario.created_at).toLocaleString('zh-TW')}</div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default Scenarios




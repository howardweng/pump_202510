import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Dashboard from './pages/Dashboard'
import DeviceConfig from './pages/DeviceConfig'
import Scenarios from './pages/Scenarios'
import './App.css'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
          {/* 導航欄 */}
          <nav className="bg-gradient-to-r from-indigo-600 via-blue-600 to-cyan-600 text-white shadow-xl">
            <div className="container mx-auto px-4 py-4">
              <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold">MODBUS 模擬器管理介面</h1>
                <div className="space-x-2">
                  <Link to="/" className="hover:bg-white/20 px-4 py-2 rounded-lg transition-all font-medium">
                    設備總覽
                  </Link>
                  <Link to="/devices" className="hover:bg-white/20 px-4 py-2 rounded-lg transition-all font-medium">
                    設備配置
                  </Link>
                  <Link to="/scenarios" className="hover:bg-white/20 px-4 py-2 rounded-lg transition-all font-medium">
                    場景管理
                  </Link>
                </div>
              </div>
            </div>
          </nav>

          {/* 主要內容 */}
          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/devices" element={<DeviceConfig />} />
              <Route path="/scenarios" element={<Scenarios />} />
            </Routes>
          </main>
        </div>
      </Router>
    </QueryClientProvider>
  )
}

export default App




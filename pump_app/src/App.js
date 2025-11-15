import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation, useNavigate } from 'react-router-dom';
import { FiRefreshCw } from 'react-icons/fi';
import { TestProvider } from './context/TestContext';
import MainDashboard from './pages/MainDashboard';
import TestSetup from './pages/TestSetup';
import DataManagement from './pages/DataManagement';
import './index.css';

function Header() {
  const navigate = useNavigate();
  const location = useLocation();
  const currentPath = location.pathname;

  return (
    <header className="bg-gray-100 text-gray-900 py-3 shadow-md relative border-b-2 border-gray-300">
      <nav className="container mx-auto flex justify-center gap-4">
        {/* 導航按鈕 - 混合改進風格 */}
        <button
          onClick={() => navigate("/")}
          className={`px-6 py-2 rounded-lg text-lg font-bold shadow-md transition ${
            currentPath === "/"
              ? "bg-blue-600 text-white opacity-50"
              : "bg-blue-600 text-white hover:bg-blue-500"
          }`}
        >
          主控台
        </button>

        <button
          onClick={() => navigate("/setup")}
          className={`px-6 py-2 rounded-lg text-lg font-bold shadow-md transition ${
            currentPath === "/setup"
              ? "bg-blue-600 text-white opacity-50"
              : "bg-blue-600 text-white hover:bg-blue-500"
          }`}
        >
          測試設定
        </button>

        <button
          onClick={() => navigate("/data")}
          className={`px-6 py-2 rounded-lg text-lg font-bold shadow-md transition ${
            currentPath === "/data"
              ? "bg-blue-600 text-white opacity-50"
              : "bg-blue-600 text-white hover:bg-blue-500"
          }`}
        >
          數據管理
        </button>
      </nav>

      {/* 重新整理按鈕 (右側) - 混合改進風格 */}
      <button
        onClick={() => window.location.reload()}
        className="absolute top-1/2 right-4 transform -translate-y-1/2 px-6 py-2 flex items-center gap-2 rounded-lg bg-green-700 text-white text-lg font-bold shadow-md transition hover:bg-green-600"
      >
        <FiRefreshCw className="w-6 h-6" />
        <span>重新整理</span>
      </button>
    </header>
  );
}

function App() {
  return (
    <TestProvider>
      <Router>
        <div className="min-h-screen bg-slate-100">
          <Header />
          <Routes>
            <Route path="/" element={<MainDashboard />} />
            <Route path="/setup" element={<TestSetup />} />
            <Route path="/data" element={<DataManagement />} />
          </Routes>
        </div>
      </Router>
    </TestProvider>
  );
}

export default App;

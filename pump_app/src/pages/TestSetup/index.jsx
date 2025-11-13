// pages/TestSetup/index.jsx
import React, { useState } from 'react';
import { useTest } from '../../context/TestContext';

function TestSetup() {
  const { testConfig, setTestConfig } = useTest();

  const [formData, setFormData] = useState({
    pumpModel: testConfig.pumpModel || '',
    testMode: testConfig.testMode || 'vacuum',
    testType: testConfig.testType || 'pressure',
    powerSource: testConfig.powerSource || '',
    ratedPower: testConfig.ratedPower || 0,
    maxCurrent: testConfig.maxCurrent || 0,
    saveTarget: testConfig.saveTarget || 'test'
  });

  const handleSave = () => {
    setTestConfig(formData);
    alert('測試配置已儲存！');
  };

  return (
    <div className="container mx-auto px-4 py-6">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">測試設定</h1>

      <div className="bg-white rounded-lg shadow p-6 max-w-3xl mx-auto">
        {/* 幫浦型號 */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            幫浦型號 *
          </label>
          <input
            type="text"
            value={formData.pumpModel}
            onChange={(e) => setFormData({ ...formData, pumpModel: e.target.value })}
            placeholder="輸入幫浦型號 (例: DMM9200)"
            className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* 測試模式 */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            測試模式 *
          </label>
          <select
            value={formData.testMode}
            onChange={(e) => setFormData({ ...formData, testMode: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="vacuum">真空幫浦</option>
            <option value="positive">正壓幫浦</option>
            <option value="manual">手動模式</option>
          </select>
        </div>

        {/* 測試類型 */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            測試類型 *
          </label>
          <select
            value={formData.testType}
            onChange={(e) => setFormData({ ...formData, testType: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="pressure">壓力測試</option>
            <option value="flow">流量測試</option>
          </select>
        </div>

        {/* 電源類型 */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            電源類型 *
          </label>
          <select
            value={formData.powerSource}
            onChange={(e) => setFormData({ ...formData, powerSource: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">請選擇...</option>
            <option value="AC110V">AC 110V</option>
            <option value="AC220V">AC 220V</option>
            <option value="DC24V">DC 24V</option>
            <option value="DC12V">DC 12V</option>
          </select>
        </div>

        {/* 額定功率 */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            額定功率 (W)
          </label>
          <input
            type="number"
            value={formData.ratedPower}
            onChange={(e) => setFormData({ ...formData, ratedPower: parseFloat(e.target.value) || 0 })}
            placeholder="輸入額定功率"
            className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* 最大電流 */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            最大電流 (A)
          </label>
          <input
            type="number"
            value={formData.maxCurrent}
            onChange={(e) => setFormData({ ...formData, maxCurrent: parseFloat(e.target.value) || 0 })}
            placeholder="輸入最大電流"
            className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* 儲存目標 */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            儲存目標 *
          </label>
          <select
            value={formData.saveTarget}
            onChange={(e) => setFormData({ ...formData, saveTarget: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="test">測試數據</option>
            <option value="reference">參考數據</option>
          </select>
        </div>

        {/* 按鈕 */}
        <div className="flex gap-4">
          <button
            onClick={handleSave}
            className="flex-1 px-6 py-3 bg-blue-600 text-white rounded font-medium hover:bg-blue-700 transition"
          >
            儲存配置
          </button>
          <button
            onClick={() => setFormData({
              pumpModel: '',
              testMode: 'vacuum',
              testType: 'pressure',
              powerSource: '',
              ratedPower: 0,
              maxCurrent: 0,
              saveTarget: 'test'
            })}
            className="px-6 py-3 bg-gray-300 text-gray-800 rounded font-medium hover:bg-gray-400 transition"
          >
            重置
          </button>
        </div>
      </div>

      {/* 當前配置 */}
      {testConfig.pumpModel && (
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-6 max-w-3xl mx-auto">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">當前測試配置</h2>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span className="text-gray-600">型號:</span>
              <span className="ml-2 font-medium text-gray-800">{testConfig.pumpModel}</span>
            </div>
            <div>
              <span className="text-gray-600">測試模式:</span>
              <span className="ml-2 font-medium text-gray-800">
                {testConfig.testMode === 'vacuum' ? '真空幫浦' : testConfig.testMode === 'positive' ? '正壓幫浦' : '手動模式'}
              </span>
            </div>
            <div>
              <span className="text-gray-600">測試類型:</span>
              <span className="ml-2 font-medium text-gray-800">
                {testConfig.testType === 'pressure' ? '壓力測試' : '流量測試'}
              </span>
            </div>
            <div>
              <span className="text-gray-600">電源:</span>
              <span className="ml-2 font-medium text-gray-800">{testConfig.powerSource || '-'}</span>
            </div>
            <div>
              <span className="text-gray-600">額定功率:</span>
              <span className="ml-2 font-medium text-gray-800">{testConfig.ratedPower} W</span>
            </div>
            <div>
              <span className="text-gray-600">最大電流:</span>
              <span className="ml-2 font-medium text-gray-800">{testConfig.maxCurrent} A</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default TestSetup;

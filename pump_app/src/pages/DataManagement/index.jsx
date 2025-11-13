// pages/DataManagement/index.jsx
import React, { useState, useEffect } from 'react';
import { getTestHistory, getReferenceData, deleteTestData, deleteReferenceData } from '../../utils/exportData';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function DataManagement() {
  const [activeTab, setActiveTab] = useState('test'); // 'test' | 'reference' | 'compare'
  const [testData, setTestData] = useState([]);
  const [referenceData, setReferenceData] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  // 比對選擇
  const [compareReference, setCompareReference] = useState(null);
  const [compareTest, setCompareTest] = useState(null);

  // 載入數據
  useEffect(() => {
    loadData();
  }, []);

  const loadData = () => {
    setTestData(getTestHistory());
    setReferenceData(getReferenceData());
  };

  // 刪除數據
  const handleDelete = (id, type) => {
    if (!window.confirm('確定要刪除此數據嗎？')) return;

    if (type === 'test') {
      if (deleteTestData(id)) {
        loadData();
      }
    } else {
      if (deleteReferenceData(id)) {
        loadData();
      }
    }
  };

  // 搜尋篩選
  const filteredTestData = testData.filter(item =>
    item.pumpModel.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.testMode.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredReferenceData = referenceData.filter(item =>
    item.pumpModel.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.testMode.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // 計算差異
  const calculateDifference = () => {
    if (!compareReference || !compareTest) return null;

    const refValue = parseFloat(compareReference.avgValue);
    const testValue = parseFloat(compareTest.avgValue);
    const diff = testValue - refValue;
    const diffPercent = refValue !== 0 ? ((diff / refValue) * 100).toFixed(2) : 0;

    const refCurrent = parseFloat(compareReference.avgCurrent);
    const testCurrent = parseFloat(compareTest.avgCurrent);
    const currentDiff = testCurrent - refCurrent;
    const currentDiffPercent = refCurrent !== 0 ? ((currentDiff / refCurrent) * 100).toFixed(2) : 0;

    return {
      valueDiff: diff.toFixed(2),
      valueDiffPercent: diffPercent,
      currentDiff: currentDiff.toFixed(2),
      currentDiffPercent: currentDiffPercent,
      isWithinThreshold: Math.abs(parseFloat(diffPercent)) <= 5
    };
  };

  const difference = calculateDifference();

  return (
    <div className="container mx-auto px-4 py-6">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">數據管理</h1>

      {/* Tab 切換 */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setActiveTab('test')}
          className={`px-6 py-2 rounded font-medium transition ${
            activeTab === 'test'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          測試數據 ({testData.length})
        </button>
        <button
          onClick={() => setActiveTab('reference')}
          className={`px-6 py-2 rounded font-medium transition ${
            activeTab === 'reference'
              ? 'bg-green-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          參考數據 ({referenceData.length})
        </button>
        <button
          onClick={() => setActiveTab('compare')}
          className={`px-6 py-2 rounded font-medium transition ${
            activeTab === 'compare'
              ? 'bg-purple-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          數據比對
        </button>
      </div>

      {/* 搜尋框 */}
      {activeTab !== 'compare' && (
        <div className="mb-6">
          <input
            type="text"
            placeholder="搜尋型號或測試模式..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full max-w-md px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      )}

      {/* 測試數據表格 */}
      {activeTab === 'test' && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">型號</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">測試模式</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">測試類型</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">日期</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">平均值</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">平均電流</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">時長</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredTestData.length === 0 ? (
                <tr>
                  <td colSpan="8" className="px-6 py-8 text-center text-gray-500">
                    暫無測試數據
                  </td>
                </tr>
              ) : (
                filteredTestData.map((data) => (
                  <tr key={data.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm text-gray-800">{data.pumpModel}</td>
                    <td className="px-6 py-4 text-sm text-gray-800">{data.testMode}</td>
                    <td className="px-6 py-4 text-sm text-gray-800">{data.testType}</td>
                    <td className="px-6 py-4 text-sm text-gray-800">{data.date}</td>
                    <td className="px-6 py-4 text-sm text-blue-600 font-medium">{data.avgValue}</td>
                    <td className="px-6 py-4 text-sm text-orange-800 font-medium">{data.avgCurrent} A</td>
                    <td className="px-6 py-4 text-sm text-gray-800">{data.duration}s</td>
                    <td className="px-6 py-4 text-sm">
                      <button
                        onClick={() => handleDelete(data.id, 'test')}
                        className="text-red-600 hover:text-red-800"
                      >
                        刪除
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* 參考數據表格 */}
      {activeTab === 'reference' && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-green-50 border-b border-green-200">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">型號</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">測試模式</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">測試類型</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">日期</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">平均值</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">平均電流</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">時長</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredReferenceData.length === 0 ? (
                <tr>
                  <td colSpan="8" className="px-6 py-8 text-center text-gray-500">
                    暫無參考數據
                  </td>
                </tr>
              ) : (
                filteredReferenceData.map((data) => (
                  <tr key={data.id} className="hover:bg-green-50">
                    <td className="px-6 py-4 text-sm text-gray-800">{data.pumpModel}</td>
                    <td className="px-6 py-4 text-sm text-gray-800">{data.testMode}</td>
                    <td className="px-6 py-4 text-sm text-gray-800">{data.testType}</td>
                    <td className="px-6 py-4 text-sm text-gray-800">{data.date}</td>
                    <td className="px-6 py-4 text-sm text-blue-600 font-medium">{data.avgValue}</td>
                    <td className="px-6 py-4 text-sm text-orange-800 font-medium">{data.avgCurrent} A</td>
                    <td className="px-6 py-4 text-sm text-gray-800">{data.duration}s</td>
                    <td className="px-6 py-4 text-sm">
                      <button
                        onClick={() => handleDelete(data.id, 'reference')}
                        className="text-red-600 hover:text-red-800"
                      >
                        刪除
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* 數據比對 */}
      {activeTab === 'compare' && (
        <div>
          {/* 選擇比對數據 */}
          <div className="grid grid-cols-2 gap-6 mb-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">參考數據</h3>
              <select
                value={compareReference?.id || ''}
                onChange={(e) => {
                  const selected = referenceData.find(d => d.id === parseInt(e.target.value));
                  setCompareReference(selected);
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">選擇參考數據...</option>
                {referenceData.map((data) => (
                  <option key={data.id} value={data.id}>
                    {data.pumpModel} - {data.date} ({data.testType})
                  </option>
                ))}
              </select>
              {compareReference && (
                <div className="mt-4 p-3 bg-gray-50 rounded text-sm">
                  <p><span className="font-medium">型號:</span> {compareReference.pumpModel}</p>
                  <p><span className="font-medium">日期:</span> {compareReference.date}</p>
                  <p><span className="font-medium">平均值:</span> <span className="text-blue-600 font-bold">{compareReference.avgValue}</span></p>
                  <p><span className="font-medium">平均電流:</span> <span className="text-orange-800 font-bold">{compareReference.avgCurrent} A</span></p>
                </div>
              )}
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">測試數據</h3>
              <select
                value={compareTest?.id || ''}
                onChange={(e) => {
                  const selected = testData.find(d => d.id === parseInt(e.target.value));
                  setCompareTest(selected);
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">選擇測試數據...</option>
                {testData.map((data) => (
                  <option key={data.id} value={data.id}>
                    {data.pumpModel} - {data.date} ({data.testType})
                  </option>
                ))}
              </select>
              {compareTest && (
                <div className="mt-4 p-3 bg-gray-50 rounded text-sm">
                  <p><span className="font-medium">型號:</span> {compareTest.pumpModel}</p>
                  <p><span className="font-medium">日期:</span> {compareTest.date}</p>
                  <p><span className="font-medium">平均值:</span> <span className="text-blue-600 font-bold">{compareTest.avgValue}</span></p>
                  <p><span className="font-medium">平均電流:</span> <span className="text-orange-800 font-bold">{compareTest.avgCurrent} A</span></p>
                </div>
              )}
            </div>
          </div>

          {/* 差異分析 */}
          {difference && (
            <>
              <div className="bg-white rounded-lg shadow p-6 mb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">差異分析</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className={`p-3 border rounded ${
                    difference.isWithinThreshold ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'
                  }`}>
                    <p className="font-medium text-gray-700">數值差異</p>
                    <p className={`text-xl font-bold mt-1 ${
                      difference.isWithinThreshold ? 'text-green-700' : 'text-yellow-700'
                    }`}>
                      {difference.valueDiff > 0 ? '+' : ''}{difference.valueDiff} ({difference.valueDiffPercent}%)
                    </p>
                    <p className={`text-xs mt-1 ${
                      difference.isWithinThreshold ? 'text-green-600' : 'text-yellow-600'
                    }`}>
                      {difference.isWithinThreshold ? '✓ 正常範圍' : '⚠ 注意'}
                    </p>
                  </div>
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded">
                    <p className="font-medium text-gray-700">電流差異</p>
                    <p className="text-xl font-bold text-blue-700 mt-1">
                      {difference.currentDiff > 0 ? '+' : ''}{difference.currentDiff} A ({difference.currentDiffPercent}%)
                    </p>
                    <p className="text-xs text-blue-600 mt-1">電流變化</p>
                  </div>
                </div>
              </div>

              {/* 曲線對比圖 */}
              {compareReference.chartData && compareTest.chartData && (
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">曲線對比</h3>
                  <ResponsiveContainer width="100%" height={400}>
                    <LineChart>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="time"
                        type="number"
                        domain={[0, 'auto']}
                        label={{ value: '時間 (秒)', position: 'insideBottom', offset: -5 }}
                      />
                      <YAxis
                        label={{ value: compareTest.testType === '壓力測試' ? '壓力 (kPa)' : '流量', angle: -90, position: 'insideLeft' }}
                      />
                      <Tooltip />
                      <Legend />
                      <Line
                        data={compareReference.chartData}
                        type="monotone"
                        dataKey={compareTest.testType === '壓力測試' ? 'pressure' : 'flow'}
                        stroke="#2563eb"
                        strokeWidth={2}
                        name="參考數據"
                        dot={false}
                      />
                      <Line
                        data={compareTest.chartData}
                        type="monotone"
                        dataKey={compareTest.testType === '壓力測試' ? 'pressure' : 'flow'}
                        stroke="#dc2626"
                        strokeWidth={2}
                        strokeDasharray="5 5"
                        name="測試數據"
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default DataManagement;

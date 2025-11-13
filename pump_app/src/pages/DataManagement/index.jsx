// pages/DataManagement/index.jsx
import React from 'react';

function DataManagement() {

  // 模擬測試數據
  const mockTestData = [
    {
      id: 1,
      pumpModel: 'DMM9200',
      testMode: '真空幫浦',
      testType: '壓力測試',
      date: '2025-11-12',
      avgPressure: -93.2,
      avgCurrent: 7.1,
      duration: 120
    },
    {
      id: 2,
      pumpModel: 'SSU2050',
      testMode: '真空幫浦',
      testType: '壓力測試',
      date: '2025-11-11',
      avgPressure: -88.5,
      avgCurrent: 6.8,
      duration: 115
    }
  ];

  // 模擬參考數據
  const mockReferenceData = [
    {
      id: 1,
      pumpModel: 'DMM9200',
      testMode: '真空幫浦',
      testType: '壓力測試',
      date: '2025-11-01',
      avgPressure: -95.5,
      avgCurrent: 6.8,
      duration: 120
    }
  ];

  return (
    <div className="container mx-auto px-4 py-6">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">數據管理</h1>

      {/* 測試數據 */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">測試數據</h2>
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">型號</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">測試模式</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">測試類型</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">日期</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">平均壓力</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">平均電流</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">時長</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {mockTestData.length === 0 ? (
                <tr>
                  <td colSpan="8" className="px-6 py-8 text-center text-gray-500">
                    暫無測試數據
                  </td>
                </tr>
              ) : (
                mockTestData.map((data) => (
                  <tr key={data.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm text-gray-800">{data.pumpModel}</td>
                    <td className="px-6 py-4 text-sm text-gray-800">{data.testMode}</td>
                    <td className="px-6 py-4 text-sm text-gray-800">{data.testType}</td>
                    <td className="px-6 py-4 text-sm text-gray-800">{data.date}</td>
                    <td className="px-6 py-4 text-sm text-blue-600 font-medium">
                      {data.avgPressure} kPa
                    </td>
                    <td className="px-6 py-4 text-sm text-orange-800 font-medium">
                      {data.avgCurrent} A
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-800">{data.duration}s</td>
                    <td className="px-6 py-4 text-sm">
                      <button className="text-blue-600 hover:text-blue-800 mr-3">檢視</button>
                      <button className="text-red-600 hover:text-red-800">刪除</button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 參考數據 */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">參考數據</h2>
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-green-50 border-b border-green-200">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">型號</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">測試模式</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">測試類型</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">日期</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">平均壓力</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">平均電流</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">時長</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {mockReferenceData.length === 0 ? (
                <tr>
                  <td colSpan="8" className="px-6 py-8 text-center text-gray-500">
                    暫無參考數據
                  </td>
                </tr>
              ) : (
                mockReferenceData.map((data) => (
                  <tr key={data.id} className="hover:bg-green-50">
                    <td className="px-6 py-4 text-sm text-gray-800">{data.pumpModel}</td>
                    <td className="px-6 py-4 text-sm text-gray-800">{data.testMode}</td>
                    <td className="px-6 py-4 text-sm text-gray-800">{data.testType}</td>
                    <td className="px-6 py-4 text-sm text-gray-800">{data.date}</td>
                    <td className="px-6 py-4 text-sm text-blue-600 font-medium">
                      {data.avgPressure} kPa
                    </td>
                    <td className="px-6 py-4 text-sm text-orange-800 font-medium">
                      {data.avgCurrent} A
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-800">{data.duration}s</td>
                    <td className="px-6 py-4 text-sm">
                      <button className="text-blue-600 hover:text-blue-800 mr-3">檢視</button>
                      <button className="text-red-600 hover:text-red-800">刪除</button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 數據比對 */}
      <div>
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">數據比對</h2>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="grid grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                參考數據
              </label>
              <select className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="">選擇參考數據...</option>
                {mockReferenceData.map((data) => (
                  <option key={data.id} value={data.id}>
                    {data.pumpModel} - {data.date}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                測試數據
              </label>
              <select className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="">選擇測試數據...</option>
                {mockTestData.map((data) => (
                  <option key={data.id} value={data.id}>
                    {data.pumpModel} - {data.date}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <button className="w-full px-6 py-3 bg-blue-600 text-white rounded font-medium hover:bg-blue-700 transition">
            開始比對
          </button>
        </div>
      </div>

      {/* 提示訊息 */}
      <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded">
        <p className="text-sm text-yellow-800">
          數據管理功能將在後續階段實現完整的 CRUD 操作與數據庫整合
        </p>
      </div>
    </div>
  );
}

export default DataManagement;

// pages/TestSetup/index.jsx
import React, { useState } from 'react';
import { useTest } from '../../context/TestContext';
import { PUMP_MODELS, filterPumpModels, getModelSpec } from '../../constants/pumpModels';

function TestSetup() {
  const { testConfig, setTestConfig } = useTest();

  const [formData, setFormData] = useState({
    pumpModel: testConfig.pumpModel || '',
    testMode: testConfig.testMode || 'vacuum',
    testType: testConfig.testType || 'pressure',
    powerSource: testConfig.powerSource || '',
    ratedPower: testConfig.ratedPower || '',
    maxCurrent: testConfig.maxCurrent || '',
    saveTarget: testConfig.saveTarget || 'test',
    notes: testConfig.notes || ''
  });

  // 搜尋相關狀態
  const [showModelSuggestions, setShowModelSuggestions] = useState(false);
  const [filteredModels, setFilteredModels] = useState(PUMP_MODELS);

  const handleSave = () => {
    // 驗證必填欄位
    if (!formData.pumpModel || formData.pumpModel.trim() === '') {
      alert('請輸入幫浦型號');
      return;
    }
    if (!formData.powerSource) {
      alert('請選擇電源類型');
      return;
    }
    if (!formData.ratedPower || formData.ratedPower === '' || parseInt(formData.ratedPower, 10) <= 0) {
      alert('請輸入有效的額定功率 (必須大於 0)');
      return;
    }
    if (!formData.maxCurrent || formData.maxCurrent === '' || parseInt(formData.maxCurrent, 10) <= 0) {
      alert('請輸入有效的最大電流 (必須大於 0)');
      return;
    }

    // 轉換為數字格式保存
    setTestConfig({
      ...formData,
      ratedPower: parseInt(formData.ratedPower, 10),
      maxCurrent: parseInt(formData.maxCurrent, 10)
    });
    alert('測試配置已儲存！');
  };

  // 處理型號輸入
  const handleModelInput = (e) => {
    const value = e.target.value;
    setFormData({ ...formData, pumpModel: value });
    setShowModelSuggestions(true);
    setFilteredModels(filterPumpModels(value));
  };

  // 選擇型號
  const selectModel = (model) => {
    setFormData({ ...formData, pumpModel: model });
    setShowModelSuggestions(false);
  };

  return (
    <div className="container mx-auto px-4 py-3">
      <h1 className="text-2xl font-bold text-slate-800 mb-3">測試設定</h1>

      {/* 左側配置 + 右側表單 */}
      <div className="grid grid-cols-12 gap-4">
        {/* 左側：當前配置 */}
        <div className="col-span-3">
          {testConfig.pumpModel ? (
            <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border-2 border-indigo-200 rounded-xl p-4 shadow-lg h-full">
              <h2 className="text-base font-bold text-slate-800 mb-4 pb-2 border-b border-indigo-300 text-center">當前測試配置</h2>
              <div className="space-y-2.5 text-sm">
                <div className="flex items-start">
                  <span className="text-slate-400 font-medium w-20 flex-shrink-0">型號:</span>
                  <span className="text-lg font-bold text-[#0066CC] flex-1 break-words">{testConfig.pumpModel}</span>
                </div>
                <div className="flex items-start">
                  <span className="text-slate-400 font-medium w-20 flex-shrink-0">測試模式:</span>
                  <span className="text-lg font-bold text-[#0066CC] flex-1">
                    {testConfig.testMode === 'vacuum' ? '真空幫浦' : testConfig.testMode === 'positive' ? '正壓幫浦' : '手動模式'}
                  </span>
                </div>
                <div className="flex items-start">
                  <span className="text-slate-400 font-medium w-20 flex-shrink-0">測試類型:</span>
                  <span className="text-lg font-bold text-[#0066CC] flex-1">
                    {testConfig.testType === 'pressure' ? '壓力測試' : '流量測試'}
                  </span>
                </div>
                <div className="flex items-start">
                  <span className="text-slate-400 font-medium w-20 flex-shrink-0">電源:</span>
                  <span className="text-lg font-bold text-[#0066CC] flex-1">{testConfig.powerSource || '-'}</span>
                </div>
                <div className="flex items-start">
                  <span className="text-slate-400 font-medium w-20 flex-shrink-0">額定功率:</span>
                  <span className="text-lg font-bold text-[#0066CC] flex-1">{testConfig.ratedPower} W</span>
                </div>
                <div className="flex items-start">
                  <span className="text-slate-400 font-medium w-20 flex-shrink-0">最大電流:</span>
                  <span className="text-lg font-bold text-[#0066CC] flex-1">{testConfig.maxCurrent} A</span>
                </div>
                <div className="flex items-start">
                  <span className="text-slate-400 font-medium w-20 flex-shrink-0">儲存目標:</span>
                  <span className="text-lg font-bold text-[#0066CC] flex-1">
                    {testConfig.saveTarget === 'test' ? '測試數據' : '參考數據'}
                  </span>
                </div>
                {testConfig.notes && (
                  <div className="flex items-start">
                    <span className="text-slate-400 font-medium w-20 flex-shrink-0">備註資料:</span>
                    <span className="text-lg font-bold text-[#0066CC] flex-1 break-words">{testConfig.notes}</span>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded-lg shadow-md border-2 border-yellow-200">
              <div className="flex items-center">
                <svg className="w-5 h-5 text-yellow-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <p className="text-yellow-900 font-bold text-xs">
                  尚未設定測試配置
                </p>
              </div>
            </div>
          )}
        </div>

        {/* 右側：表單 */}
        <div className="col-span-9">
      <div className="bg-white rounded-lg shadow-lg p-6 border-2 border-slate-300">
        {/* 幫浦型號 - 可搜尋下拉選單 */}
        <div className="mb-6 relative">
          <label className="block text-sm font-medium text-slate-400 mb-2">
            幫浦型號 * <span className="text-xs text-slate-400 font-normal">(可搜尋或手動輸入)</span>
          </label>
          <input
            type="text"
            value={formData.pumpModel}
            onChange={handleModelInput}
            onFocus={() => {
              setShowModelSuggestions(true);
              setFilteredModels(filterPumpModels(formData.pumpModel));
            }}
            onBlur={() => setTimeout(() => setShowModelSuggestions(false), 200)}
            placeholder="搜尋或輸入幫浦型號 (例: DMM9200)"
            className="w-full px-4 py-2 bg-white border-2 border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-slate-800 font-bold"
          />

          {/* 下拉建議列表 */}
          {showModelSuggestions && filteredModels.length > 0 && (
            <div className="absolute z-10 w-full mt-1 bg-white border-2 border-slate-300 rounded-lg shadow-xl max-h-80 overflow-y-auto">
              <div className="p-2 bg-slate-100 border-b-2 border-slate-300 text-xs text-slate-700 font-bold sticky top-0">
                找到 {filteredModels.length} 個型號
              </div>
              {filteredModels.map((model, index) => {
                const spec = getModelSpec(model);
                return (
                  <div
                    key={index}
                    onClick={() => selectModel(model)}
                    className="px-4 py-3 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                  >
                    <div className="font-medium text-gray-800">{model}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      <span className="inline-block px-2 py-0.5 bg-blue-100 text-blue-800 rounded mr-2">
                        {spec.type}
                      </span>
                      {spec.description}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* 當前選擇的型號資訊 */}
          {formData.pumpModel && !showModelSuggestions && (
            <div className="mt-2 p-3 bg-blue-50 border-2 border-blue-300 rounded-lg text-sm shadow-md">
              <span className="font-medium text-slate-400">已選擇:</span>
              <span className="ml-2 font-bold text-[#0066CC]">{formData.pumpModel}</span>
              {getModelSpec(formData.pumpModel).description !== '無規格說明' && (
                <div className="mt-1 text-gray-600">
                  {getModelSpec(formData.pumpModel).description}
                </div>
              )}
            </div>
          )}
        </div>

        {/* 測試模式 */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-400 mb-2">
            測試模式 *
          </label>
          <select
            value={formData.testMode}
            onChange={(e) => setFormData({ ...formData, testMode: e.target.value })}
            className="w-full px-4 py-2 bg-white border-2 border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-slate-800"
          >
            <option value="vacuum">真空幫浦</option>
            <option value="positive">正壓幫浦</option>
            <option value="manual">手動模式</option>
          </select>
        </div>

        {/* 測試類型 */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-400 mb-2">
            測試類型 *
          </label>
          <select
            value={formData.testType}
            onChange={(e) => setFormData({ ...formData, testType: e.target.value })}
            className="w-full px-4 py-2 bg-white border-2 border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-slate-800"
          >
            <option value="pressure">壓力測試</option>
            <option value="flow">流量測試</option>
          </select>
        </div>

        {/* 電源類型 */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-400 mb-2">
            電源類型 *
          </label>
          <select
            value={formData.powerSource}
            onChange={(e) => setFormData({ ...formData, powerSource: e.target.value })}
            className="w-full px-4 py-2 bg-white border-2 border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-slate-800"
          >
            <option value="">請選擇...</option>
            <option value="AC110V">AC 110V</option>
            <option value="AC220V">AC 220V</option>
            <option value="AC200V-3P">AC 200V-3P</option>
            <option value="DC24V">DC 24V</option>
            <option value="DC12V">DC 12V</option>
          </select>
        </div>

        {/* 額定功率 */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-400 mb-2">
            額定功率 (W) *
          </label>
          <input
            type="text"
            inputMode="numeric"
            value={formData.ratedPower}
            onChange={(e) => {
              const value = e.target.value;
              // 只允許數字輸入
              if (value === '' || /^\d+$/.test(value)) {
                setFormData({ ...formData, ratedPower: value });
              }
            }}
            placeholder="請輸入整數（例如：100）"
            className="w-full px-4 py-2 bg-white border-2 border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-slate-800 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
          />
        </div>

        {/* 最大電流 */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-400 mb-2">
            最大電流 (A) *
          </label>
          <input
            type="text"
            inputMode="numeric"
            value={formData.maxCurrent}
            onChange={(e) => {
              const value = e.target.value;
              // 只允許數字輸入
              if (value === '' || /^\d+$/.test(value)) {
                setFormData({ ...formData, maxCurrent: value });
              }
            }}
            placeholder="請輸入整數（例如：5）"
            className="w-full px-4 py-2 bg-white border-2 border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-slate-800 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
          />
        </div>

        {/* 儲存目標 */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-400 mb-2">
            儲存目標 *
          </label>
          <select
            value={formData.saveTarget}
            onChange={(e) => setFormData({ ...formData, saveTarget: e.target.value })}
            className="w-full px-4 py-2 bg-white border-2 border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-slate-800"
          >
            <option value="test">測試數據</option>
            <option value="reference">參考數據</option>
          </select>
        </div>

        {/* 備註資料 */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-400 mb-2">
            備註資料
          </label>
          <textarea
            value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            placeholder="可選填備註資訊（例如：測試環境說明、特殊注意事項等）"
            rows={3}
            className="w-full px-4 py-2 bg-white border-2 border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-slate-800 font-bold resize-y"
          />
        </div>

        {/* 按鈕 */}
        <div className="flex gap-3 mt-6 pt-4 border-t-2 border-slate-200">
          <button
            onClick={handleSave}
            className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg font-bold text-lg hover:bg-blue-700 transition shadow-md"
          >
            儲存配置
          </button>
          <button
            onClick={() => setFormData({
              pumpModel: '',
              testMode: 'vacuum',
              testType: 'pressure',
              powerSource: '',
              ratedPower: '',
              maxCurrent: '',
              saveTarget: 'test',
              notes: ''
            })}
            className="px-6 py-3 bg-gray-400 text-white rounded-lg font-bold text-lg hover:bg-gray-500 transition shadow-md"
          >
            重置
          </button>
        </div>
      </div>
        </div>
      </div>
    </div>
  );
}

export default TestSetup;

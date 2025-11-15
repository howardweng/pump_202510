// constants/pumpModels.js

// 幫浦型號資料庫 (50+ models)
export const PUMP_MODELS = [
  // 真空幫浦 (20+ models)
  'DMM9200', 'DMM9250', 'DMM9300', 'SSU2050', 'SSU2070', 'SSU2100',
  'VPX-100', 'VPX-150', 'VPX-200', 'VCM-5000', 'VCM-7500',
  'TVP-300', 'TVP-500', 'TVP-700', 'UVP-1000', 'UVP-1500',
  'MVP-200', 'MVP-350', 'HVP-800', 'HVP-1200',

  // 正壓幫浦 (15+ models)
  'PPM-5000', 'PPM-7500', 'PPM-10000', 'HPU-300', 'HPU-500',
  'ACP-200', 'ACP-350', 'ACP-500', 'PCP-1000', 'PCP-1500',
  'GPX-300', 'GPX-600', 'THP-400', 'THP-800',

  // 水幫浦 (15+ models)
  'WPM-1000', 'WPM-1500', 'WPM-2000', 'LPX-250', 'LPX-400',
  'HWP-300', 'HWP-600', 'HWP-900', 'CWP-500', 'CWP-750',
  'SWP-1200', 'SWP-1800', 'MWP-600', 'MWP-1000'
];

// 幫浦型號規格說明
export const PUMP_MODEL_SPECS = {
  // 真空幫浦
  'DMM9200': { type: '真空幫浦', description: 'Diaphragm 隔膜式真空幫浦 - 標準型' },
  'DMM9250': { type: '真空幫浦', description: 'Diaphragm 隔膜式真空幫浦 - 增強型' },
  'DMM9300': { type: '真空幫浦', description: 'Diaphragm 隔膜式真空幫浦 - 高性能型' },
  'SSU2050': { type: '真空幫浦', description: 'Scroll 渦旋式真空幫浦 - 靜音型' },
  'SSU2070': { type: '真空幫浦', description: 'Scroll 渦旋式真空幫浦 - 中型' },
  'SSU2100': { type: '真空幫浦', description: 'Scroll 渦旋式真空幫浦 - 大型' },
  'VPX-100': { type: '真空幫浦', description: 'Vacuum Pump X系列 - 小型' },
  'VPX-150': { type: '真空幫浦', description: 'Vacuum Pump X系列 - 中型' },
  'VPX-200': { type: '真空幫浦', description: 'Vacuum Pump X系列 - 大型' },
  'VCM-5000': { type: '真空幫浦', description: 'Vacuum Compressor Module - 5000型' },
  'VCM-7500': { type: '真空幫浦', description: 'Vacuum Compressor Module - 7500型' },

  // 正壓幫浦
  'PPM-5000': { type: '正壓幫浦', description: 'Positive Pressure Module - 5000型' },
  'PPM-7500': { type: '正壓幫浦', description: 'Positive Pressure Module - 7500型' },
  'PPM-10000': { type: '正壓幫浦', description: 'Positive Pressure Module - 10000型' },
  'HPU-300': { type: '正壓幫浦', description: 'High Pressure Unit - 300型' },
  'HPU-500': { type: '正壓幫浦', description: 'High Pressure Unit - 500型' },
  'ACP-200': { type: '正壓幫浦', description: 'Air Compressor Pump - 200型' },
  'ACP-350': { type: '正壓幫浦', description: 'Air Compressor Pump - 350型' },
  'ACP-500': { type: '正壓幫浦', description: 'Air Compressor Pump - 500型' },

  // 水幫浦
  'WPM-1000': { type: '水幫浦', description: 'Water Pump Module - 1000型' },
  'WPM-1500': { type: '水幫浦', description: 'Water Pump Module - 1500型' },
  'WPM-2000': { type: '水幫浦', description: 'Water Pump Module - 2000型' },
  'LPX-250': { type: '水幫浦', description: 'Liquid Pump X系列 - 250型' },
  'LPX-400': { type: '水幫浦', description: 'Liquid Pump X系列 - 400型' },
  'HWP-300': { type: '水幫浦', description: 'High Flow Water Pump - 300型' },
  'HWP-600': { type: '水幫浦', description: 'High Flow Water Pump - 600型' },
  'HWP-900': { type: '水幫浦', description: 'High Flow Water Pump - 900型' }
};

// 根據搜尋字串篩選型號
export const filterPumpModels = (searchTerm) => {
  if (!searchTerm) return PUMP_MODELS;

  const term = searchTerm.toLowerCase();
  return PUMP_MODELS.filter(model =>
    model.toLowerCase().includes(term)
  );
};

// 取得型號規格說明
export const getModelSpec = (model) => {
  return PUMP_MODEL_SPECS[model] || { type: '未知', description: '無規格說明' };
};

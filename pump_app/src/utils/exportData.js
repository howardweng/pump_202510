// utils/exportData.js
import html2canvas from 'html2canvas';
import JSZip from 'jszip';

/**
 * Export test data to CSV and chart image, packaged in ZIP
 * @param {Object} params
 * @param {Array} params.chartData - Test data array
 * @param {Object} params.testConfig - Test configuration
 * @param {string} params.testMode - Test mode (vacuum/positive/manual)
 * @param {string} params.testType - Test type (pressure/flow)
 * @param {HTMLElement} params.chartElement - Chart DOM element to capture
 */
export const exportTestData = async ({
  chartData,
  testConfig,
  testMode,
  testType,
  chartElement
}) => {
  try {
    // 1. 生成檔名
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '').replace('T', '_');
    const testTypeLabel = testType === 'pressure' ? '壓力測試' : '流量測試';
    const filename = `${testConfig.pumpModel}_${testTypeLabel}_${timestamp}`;

    // 2. 生成 CSV 內容
    const csvContent = generateCSV(chartData, testConfig, testMode, testType);

    // 3. 截取圖表圖片
    let chartBlob = null;
    if (chartElement) {
      const canvas = await html2canvas(chartElement, {
        backgroundColor: '#ffffff',
        scale: 2
      });
      chartBlob = await new Promise(resolve => {
        canvas.toBlob(resolve, 'image/png');
      });
    }

    // 4. 打包成 ZIP
    const zip = new JSZip();
    zip.file(`${filename}.csv`, csvContent);
    if (chartBlob) {
      zip.file(`${filename}_chart.png`, chartBlob);
    }

    // 5. 下載 ZIP
    const zipBlob = await zip.generateAsync({ type: 'blob' });
    const url = URL.createObjectURL(zipBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}.zip`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    return { success: true, filename: `${filename}.zip` };
  } catch (error) {
    console.error('❌ 匯出數據失敗:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Generate CSV content from chart data
 */
const generateCSV = (chartData, testConfig, testMode, testType) => {
  // CSV 標題行
  const headers = [
    '時間 (秒)',
    testType === 'pressure'
      ? '壓力 (kPa)'
      : (testMode === 'vacuum' || testMode === 'positive' ? '氣體流量 (L/min)' : '液體流量 (m³/h)'),
    '電流 (A)',
    '時間戳記'
  ];

  // 計算統計數據
  const values = chartData.map(d => testType === 'pressure' ? d.pressure : d.flow);
  const currents = chartData.map(d => d.current);
  const avgValue = values.length > 0 ? (values.reduce((a, b) => a + b, 0) / values.length).toFixed(2) : 0;
  const maxValue = values.length > 0 ? Math.max(...values).toFixed(2) : 0;
  const avgCurrent = currents.length > 0 ? (currents.reduce((a, b) => a + b, 0) / currents.length).toFixed(2) : 0;
  const maxCurrent = currents.length > 0 ? Math.max(...currents).toFixed(2) : 0;
  const duration = chartData.length > 0 ? chartData[chartData.length - 1].time.toFixed(2) : 0;

  // 生成 CSV 內容
  let csv = '# 測試摘要\n';
  csv += `# 幫浦型號: ${testConfig.pumpModel}\n`;
  csv += `# 測試模式: ${testMode === 'vacuum' ? '真空幫浦' : testMode === 'positive' ? '正壓幫浦' : '手動模式'}\n`;
  csv += `# 測試類型: ${testType === 'pressure' ? '壓力測試' : '流量測試'}\n`;
  csv += `# 電源: ${testConfig.powerSource || '-'}\n`;
  csv += `# 額定功率: ${testConfig.ratedPower} W\n`;
  csv += `# 測試日期: ${new Date().toLocaleString('zh-TW')}\n`;
  csv += `# 測試時長: ${duration} 秒\n`;
  csv += `# 平均${testType === 'pressure' ? '壓力' : '流量'}: ${avgValue} ${headers[1].match(/\((.+)\)/)[1]}\n`;
  csv += `# 最大${testType === 'pressure' ? '壓力' : '流量'}: ${maxValue} ${headers[1].match(/\((.+)\)/)[1]}\n`;
  csv += `# 平均電流: ${avgCurrent} A\n`;
  csv += `# 最大電流: ${maxCurrent} A\n`;
  csv += '#\n';

  // 數據表頭
  csv += headers.join(',') + '\n';

  // 數據行
  chartData.forEach(row => {
    const value = testType === 'pressure' ? row.pressure : row.flow;
    const timestamp = new Date(row.timestamp).toISOString();
    csv += `${row.time},${value || 0},${row.current || 0},${timestamp}\n`;
  });

  return csv;
};

/**
 * Save test data to localStorage
 */
export const saveTestToLocalStorage = (testData) => {
  try {
    const existingData = JSON.parse(localStorage.getItem('testHistory') || '[]');
    existingData.unshift(testData); // 新數據放最前面

    // 限制最多保存 100 筆記錄
    if (existingData.length > 100) {
      existingData.splice(100);
    }

    localStorage.setItem('testHistory', JSON.stringify(existingData));
    return true;
  } catch (error) {
    console.error('❌ 儲存測試數據失敗:', error);
    return false;
  }
};

/**
 * Save reference data to localStorage
 */
export const saveReferenceToLocalStorage = (referenceData) => {
  try {
    const existingData = JSON.parse(localStorage.getItem('referenceData') || '[]');
    existingData.unshift(referenceData);

    // 限制最多保存 50 筆參考數據
    if (existingData.length > 50) {
      existingData.splice(50);
    }

    localStorage.setItem('referenceData', JSON.stringify(existingData));
    return true;
  } catch (error) {
    console.error('❌ 儲存參考數據失敗:', error);
    return false;
  }
};

/**
 * Get test history from localStorage
 */
export const getTestHistory = () => {
  try {
    return JSON.parse(localStorage.getItem('testHistory') || '[]');
  } catch (error) {
    console.error('❌ 讀取測試記錄失敗:', error);
    return [];
  }
};

/**
 * Get reference data from localStorage
 */
export const getReferenceData = () => {
  try {
    return JSON.parse(localStorage.getItem('referenceData') || '[]');
  } catch (error) {
    console.error('❌ 讀取參考數據失敗:', error);
    return [];
  }
};

/**
 * Delete test data by ID
 */
export const deleteTestData = (id) => {
  try {
    const existingData = JSON.parse(localStorage.getItem('testHistory') || '[]');
    const filtered = existingData.filter(item => item.id !== id);
    localStorage.setItem('testHistory', JSON.stringify(filtered));
    return true;
  } catch (error) {
    console.error('❌ 刪除測試數據失敗:', error);
    return false;
  }
};

/**
 * Delete reference data by ID
 */
export const deleteReferenceData = (id) => {
  try {
    const existingData = JSON.parse(localStorage.getItem('referenceData') || '[]');
    const filtered = existingData.filter(item => item.id !== id);
    localStorage.setItem('referenceData', JSON.stringify(filtered));
    return true;
  } catch (error) {
    console.error('❌ 刪除參考數據失敗:', error);
    return false;
  }
};

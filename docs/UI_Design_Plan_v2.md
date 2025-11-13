# 幫浦測試平台 - React 前端 UI 設計規劃 v2.0
## 基於現有 Air 專案的設計方案

**專案**: 氣體/液體幫浦測試平台
**客戶**: Micron Technology
**開發商**: 岡泰技研有限公司
**文件版本**: 2.0 (基於 Air 專案)
**更新日期**: 2025.11.13
**機密等級**: Confidential

---

## 📋 更新說明

本版本基於現有 **AIR_Aries** 專案進行設計，完全沿用其技術棧、設計風格和配色方案。

**主要調整**:
- ✅ 使用 **Tailwind CSS** (取代 Material-UI)
- ✅ 使用 **Recharts** 作為主要圖表庫
- ✅ 沿用 Air 專案的**淺色背景 + 藍灰色系**配色
- ✅ 採用 **Noto Sans TC** 字體
- ✅ **無需登入功能**
- ✅ 簡化頁面結構,專注於核心測試功能

---

## 目錄

1. [技術棧分析](#1-技術棧分析)
2. [設計風格提取](#2-設計風格提取)
3. [頁面結構規劃](#3-頁面結構規劃)
4. [主控台詳細設計](#4-主控台詳細設計)
5. [測試設定頁面](#5-測試設定頁面)
6. [數據管理頁面](#6-數據管理頁面)
7. [元件設計規範](#7-元件設計規範)
8. [狀態管理](#8-狀態管理)
9. [實作計劃](#9-實作計劃)

---

## 1. 技術棧分析

### 1.1 現有 Air 專案技術棧

```json
{
  "核心框架": {
    "react": "19.0.0",
    "react-router-dom": "6.2.1",
    "react-dom": "19.0.0"
  },
  "樣式框架": {
    "tailwindcss": "3.4.17",
    "postcss": "8.4.49",
    "autoprefixer": "10.4.20"
  },
  "圖表庫": {
    "recharts": "2.15.1",          // ⭐ Control.js 使用
    "echarts": "5.6.0",            // Flow.js 使用
    "echarts-for-react": "3.0.2"
  },
  "通訊": {
    "mqtt": "5.10.3"                // ⭐ 已整合
  },
  "工具庫": {
    "js-cookie": "3.0.5",          // Cookie 管理
    "html2canvas": "1.4.1",        // 圖表截圖
    "jszip": "3.10.1",             // ⭐ CSV + 圖表打包
    "react-icons": "5.4.0",        // Icon
    "axios": "1.7.9"
  }
}
```

### 1.2 幫浦測試平台採用技術棧

```
✅ 完全沿用 Air 專案技術棧
├── React 19.0.0 + React Router v6
├── Tailwind CSS 3.4.17
├── Recharts 2.15.1 (壓力/流量曲線)
├── MQTT.js 5.10.3 (即時通訊)
├── js-cookie (設定持久化)
├── html2canvas (報表截圖)
├── JSZip 3.10.1 (CSV + 圖表打包) ⭐ 新增
└── react-icons (UI 圖示)
```

**決策理由**:
1. 開發團隊已熟悉此技術棧
2. 無需學習新框架,降低學習曲線
3. 可直接複用現有元件和樣式
4. 保持專案一致性

---

## 2. 設計風格提取

### 2.1 配色方案 (來自 Air 專案)

#### 主要色彩
```css
/* 背景色 */
bg-white           /* #ffffff - 主要內容背景 */
bg-gray-100        /* #f3f4f6 - 淺灰背景 (body, 次要區域) */
bg-gray-200        /* #e5e7eb - 卡片/區塊背景 */

/* 主題色 - 藍色系 */
bg-blue-600        /* #2563eb - 主要按鈕 */
bg-blue-900        /* #1e3a8a - 標題文字 */
bg-blue-500        /* #3b82f6 - Hover 狀態 */
text-blue-600      /* 數值顯示 */

/* 功能色 - 紫色 (特殊操作) */
bg-purple-600      /* #9333ea - 啟動測試按鈕 */
bg-purple-500      /* #a855f7 - 進度條 */
bg-purple-700      /* #7e22ce - Hover */

/* 狀態色 */
bg-green-500       /* #22c55e - 正常狀態 */
bg-green-600       /* #16a34a - 開啟狀態 */
bg-green-800       /* #166534 - 重新整理按鈕 */
bg-red-500         /* #ef4444 - 錯誤/警告 */
bg-red-600         /* #dc2626 - 錯誤文字 */
bg-orange-800      /* #9a3412 - 數值強調 */

/* 灰階 (禁用/邊框) */
bg-gray-400        /* #9ca3af - 禁用按鈕 */
bg-gray-600        /* #4b5563 - 關閉狀態 */
bg-gray-700        /* #374151 - 深色文字 */
border-gray-300    /* #d1d5db - 淺邊框 */
border-gray-400    /* #9ca3af - 標準邊框 */
border-gray-600    /* #4b5563 - 強調邊框 */
```

#### 配色應用規則
```
測試狀態:
  就緒   → bg-green-500 (綠)
  運行中 → bg-blue-600 (藍)
  暫停   → bg-orange-500 (橙)
  錯誤   → bg-red-500 (紅)

按鈕配色:
  主要操作 (啟動測試) → bg-purple-600
  次要操作 (設定)     → bg-blue-600
  危險操作 (停止)     → bg-red-600
  禁用狀態           → bg-gray-400
```

### 2.2 字體系統

```css
/* 字體家族 */
font-family: 'Noto Sans TC', sans-serif;  /* 繁體中文優化 */

/* 字體大小 */
text-xs      /* 12px - 次要資訊 */
text-sm      /* 14px - 標籤文字 */
text-base    /* 16px - 一般文字 */
text-lg      /* 18px - 小標題 */
text-xl      /* 20px - 標題 */
text-2xl     /* 24px - 大標題 */
text-4xl     /* 36px - 即時數值 */
text-6xl     /* 48px - 超大數值 (壓力/電流) */

/* 字重 */
font-normal  /* 400 */
font-medium  /* 500 */
font-semibold /* 600 */
font-bold    /* 700 */
```

### 2.3 間距系統

```css
/* Tailwind 間距 (4px 為基準) */
p-1  /* padding: 4px */
p-2  /* padding: 8px */
p-3  /* padding: 12px */
p-4  /* padding: 16px */
p-6  /* padding: 24px */
p-8  /* padding: 32px */

/* 常用間距 */
gap-2  /* 8px  - 小間距 */
gap-4  /* 16px - 標準間距 */
gap-6  /* 24px - 大間距 */

mt-2   /* margin-top: 8px */
mb-4   /* margin-bottom: 16px */
```

### 2.4 圓角與陰影

```css
/* 圓角 */
rounded       /* border-radius: 4px - 標準 */
rounded-sm    /* border-radius: 2px - 小圓角 */
rounded-lg    /* border-radius: 8px - 大圓角 */
rounded-full  /* border-radius: 9999px - 圓形 */

/* 陰影 */
shadow        /* box-shadow: 0 1px 3px rgba(0,0,0,0.1) - 標準 */
shadow-md     /* box-shadow: 0 4px 6px rgba(0,0,0,0.1) - 中等 */
shadow-lg     /* box-shadow: 0 10px 15px rgba(0,0,0,0.1) - 大 */
```

### 2.5 動畫效果

```css
/* 閃爍動畫 (狀態指示燈) */
@keyframes flashing {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.flashing {
  animation: flashing 1s infinite;  /* 快速閃爍 (錯誤) */
}

.slow-flashing {
  animation: flashing 3s infinite;  /* 慢速閃爍 (正常) */
}

/* 過渡效果 */
transition          /* transition: all 0.15s */
transition-colors   /* transition: color, background-color 0.15s */
duration-300        /* transition-duration: 300ms */
```

---

## 3. 頁面結構規劃

### 3.1 整體架構

```
Pump Testing Platform
│
├── Header (導航列)
│   ├── Logo / 標題
│   ├── 導航按鈕 (主控台 / 測試設定 / 數據管理)
│   └── 重新整理按鈕
│
├── Pages (頁面路由)
│   ├── "/" - 主控台 (Main Dashboard)
│   ├── "/setup" - 測試設定 (Test Configuration)
│   └── "/data" - 數據管理 (Data Management)
│
└── Toast 通知 (全局)
```

### 3.2 路由結構

```javascript
// src/App.js
<Routes>
  <Route path="/" element={<MainDashboard />} />
  <Route path="/setup" element={<TestSetup />} />
  <Route path="/data" element={<DataManagement />} />
</Routes>
```

**簡化理由**:
- 無需登入/權限管理頁面
- 無需系統設定頁面 (參數直接在測試設定中調整)
- 專注於核心測試流程

### 3.3 Header 設計

```jsx
// 基於 Air 專案 App.js 的 Header
<header className="bg-gray-100 text-gray-800 py-2 shadow-sm relative">
  <nav className="container mx-auto flex justify-center gap-4">
    {/* 導航按鈕 */}
    <button
      onClick={() => navigate("/")}
      className={`px-6 py-2 rounded text-lg font-medium shadow-md transition ${
        currentPath === "/"
          ? "bg-blue-600 text-white opacity-50"
          : "bg-blue-600 text-white hover:bg-blue-500"
      }`}
    >
      主控台
    </button>

    <button
      onClick={() => navigate("/setup")}
      className={`px-6 py-2 rounded text-lg font-medium shadow-md transition ${
        currentPath === "/setup"
          ? "bg-blue-600 text-white opacity-50"
          : "bg-blue-600 text-white hover:bg-blue-500"
      }`}
    >
      測試設定
    </button>

    <button
      onClick={() => navigate("/data")}
      className={`px-6 py-2 rounded text-lg font-medium shadow-md transition ${
        currentPath === "/data"
          ? "bg-blue-600 text-white opacity-50"
          : "bg-blue-600 text-white hover:bg-blue-500"
      }`}
    >
      數據管理
    </button>
  </nav>

  {/* 重新整理按鈕 (右側) */}
  <button
    onClick={() => window.location.reload()}
    className="absolute top-1/2 right-4 transform -translate-y-1/2 px-6 py-2 flex items-center gap-2 rounded bg-green-800 text-white text-lg font-medium shadow-md transition hover:bg-green-600"
  >
    <FiRefreshCw className="w-6 h-6" />
    <span>重新整理</span>
  </button>
</header>
```

---

## 4. 主控台詳細設計

### 4.1 Layout 配置 ⚠️ **已修正符合原始 PPT 需求**

**重要**: 此 Layout 完全依照原始 PPT 第 298-344 行的設計

```
┌────────────────────────────────────────────────────────────────────┐
│ Header (導航列)                                                    │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ 頂部狀態列 + 控制區 (Top Control Bar)                        │ │
│ │                                                              │ │
│ │ 左側: 狀態指示燈                                             │ │
│ │ 🟢氣體/壓力偵測正常  🟢電流偵測正常  🟢繼電器正常            │ │
│ │                                                              │ │
│ │ 中間: 測試模式 + 測試類型選擇                                │ │
│ │ [真空幫浦] [正壓幫浦] [手動測試]                             │ │
│ │ [壓力測試] [流量測試] ← **新增流量測試選項**                │ │
│ │                                                              │ │
│ │ 右側: 控制按鈕                                               │ │
│ │ [啟動測試] [暫停] [停止]                                     │ │
│ │                                                              │ │
│ │ 電磁閥狀態: A:關 B:開 C:關 D:開                              │ │
│ │ (手動模式下可點擊切換) ← **新增手動控制**                   │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ 📊 參考數據 / 比對資料庫 (上方)                  [載入數據] │ │
│ │ ┌────────────────────────────────────────────────────────┐   │ │
│ │ │型號│功能│運轉│電源│電力│壓力/流量│恆壓電流│日期│[刪除]│   │ │
│ │ │DMM │真空│自動│AC..│1500│-95.5kPa │6.8A   │11/12│      │   │ │
│ │ └────────────────────────────────────────────────────────┘   │ │
│ │ 用途: 從參考資料庫載入歷史數據,供即時比對                   │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │                                                              │ │
│ │          壓力/流量變化曲線圖 (中間大區域)                    │ │
│ │          [Recharts LineChart]                                │ │
│ │                                                              │ │
│ │   • 即時繪製壓力或流量變化                                   │ │
│ │   • X軸: 時間 (秒)                                           │ │
│ │   • Y軸左: 壓力 (kPa / kg/cm²) 或 流量 (L/min)              │ │
│ │   • Y軸右 (可選): 電流 (A)                                   │ │
│ │   • 支援放大/縮小/拖曳                                       │ │
│ │   • Height: 450px                                            │ │
│ │                                                              │ │
│ │   右下角疊加: 即時數值大字體顯示                             │ │
│ │   ┌──────────────┐ ┌──────────────┐                        │ │
│ │   │ 即時壓力/流量│ │ 即時電流     │                        │ │
│ │   │ -85.5 kPa    │ │ 6.8 A        │                        │ │
│ │   │(text-5xl)    │ │(text-5xl)    │                        │ │
│ │   │測試時間:     │ │幫浦狀態:     │                        │ │
│ │   │00:15:32      │ │🟢 運轉中     │                        │ │
│ │   └──────────────┘ └──────────────┘                        │ │
│ │                                                              │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ 📋 當前測試數據 (下方)                                       │ │
│ │ ┌────────────────────────────────────────────────────────┐   │ │
│ │ │型號│功能│運轉│電源│電力│即時壓力/流量│即時電流│測試時間│   │ │
│ │ │DMM │真空│自動│AC..│1500│  -85.5kPa   │ 6.8A  │00:15:32│   │ │
│ │ └────────────────────────────────────────────────────────┘   │ │
│ │ [儲存至參考資料庫] [儲存至測試庫] [匯出CSV]                 │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

測試完成後: [儲存圖表] 按鈕顯示於右下角
```

### 4.2 頂部狀態列 (Top Status Bar) ⚠️ **已修正 - 新增流量測試選項**

**重要**: 依照原始 PPT 第 363-365 行需求,新增測試類型選擇

```jsx
<div className="flex items-center justify-between px-8 py-4 bg-white border-b border-gray-300">

  {/* 左側: 狀態指示燈組 */}
  <div className="flex items-center gap-6">

    {/* 壓力/流量感測器狀態 */}
    <div className="flex flex-col items-center bg-white p-3 rounded-lg shadow-md border border-gray-300 w-32 text-center">
      <div className={`w-8 h-8 rounded-full shadow-md transition-colors duration-500 ${
        sensorStatus === "正常"
          ? "bg-green-500 slow-flashing"
          : "bg-red-500 flashing"
      }`}></div>
      <p className="mt-2 text-sm font-bold text-gray-800">
        {testType === 'pressure'
          ? (sensorStatus === "正常" ? "壓力偵測正常" : "壓力傳輸錯誤")
          : (sensorStatus === "正常" ? "流量偵測正常" : "流量傳輸錯誤")
        }
      </p>
    </div>

    {/* 電流感測器狀態 */}
    <div className="flex flex-col items-center bg-white p-3 rounded-lg shadow-md border border-gray-300 w-32 text-center">
      <div className={`w-8 h-8 rounded-full shadow-md transition-colors duration-500 ${
        currentSensorStatus === "正常"
          ? "bg-green-500 slow-flashing"
          : "bg-red-500 flashing"
      }`}></div>
      <p className="mt-2 text-sm font-bold text-gray-800">
        {currentSensorStatus === "正常" ? "電流偵測正常" : "電流傳輸錯誤"}
      </p>
    </div>

    {/* 繼電器狀態 */}
    <div className="flex flex-col items-center bg-white p-3 rounded-lg shadow-md border border-gray-300 w-32 text-center">
      <div className={`w-8 h-8 rounded-full shadow-md transition-colors duration-500 ${
        relayStatus === "正常"
          ? "bg-green-500 slow-flashing"
          : "bg-red-500 flashing"
      }`}></div>
      <p className="mt-2 text-sm font-bold text-gray-800">
        {relayStatus === "正常" ? "繼電器偵測正常" : "繼電器傳輸錯誤"}
      </p>
    </div>

    {/* 電磁閥狀態 (手動模式可點擊切換) */}
    <div className="bg-white p-3 rounded-lg shadow-md border border-gray-300">
      <h3 className="text-sm font-semibold text-gray-700 mb-2">
        電磁閥狀態 {testMode === 'manual' && <span className="text-xs text-blue-600">(點擊切換)</span>}
      </h3>
      <div className="flex gap-2 text-xs">
        {['A', 'B', 'C', 'D'].map(valve => (
          <button
            key={valve}
            onClick={() => testMode === 'manual' && toggleValve(valve)}
            disabled={testMode !== 'manual'}
            className={`px-2 py-1 rounded transition ${
              valves[valve]
                ? 'bg-green-600 text-white'
                : 'bg-gray-400 text-white'
            } ${testMode === 'manual' ? 'cursor-pointer hover:opacity-80' : 'cursor-default'}`}
          >
            {valve}: {valves[valve] ? '開' : '關'}
          </button>
        ))}
      </div>
    </div>
  </div>

  {/* 中間: 測試模式 + 測試類型選擇 */}
  <div className="bg-gray-200 p-4 rounded shadow-md border border-gray-400">
    <h3 className="text-lg font-semibold text-blue-900 mb-2 text-center">測試配置</h3>

    {/* 測試模式 */}
    <div className="mb-3">
      <p className="text-sm text-gray-700 mb-1 font-medium">測試模式</p>
      <div className="flex gap-2">
        <button
          onClick={() => setTestMode('vacuum')}
          className={`px-3 py-2 rounded text-white text-sm font-medium shadow transition ${
            testMode === 'vacuum'
              ? 'bg-blue-600'
              : 'bg-gray-500 hover:bg-gray-600'
          }`}
        >
          真空幫浦
        </button>
        <button
          onClick={() => setTestMode('positive')}
          className={`px-3 py-2 rounded text-white text-sm font-medium shadow transition ${
            testMode === 'positive'
              ? 'bg-blue-600'
              : 'bg-gray-500 hover:bg-gray-600'
          }`}
        >
          正壓幫浦
        </button>
        <button
          onClick={() => setTestMode('manual')}
          className={`px-3 py-2 rounded text-white text-sm font-medium shadow transition ${
            testMode === 'manual'
              ? 'bg-blue-600'
              : 'bg-gray-500 hover:bg-gray-600'
          }`}
        >
          手動測試
        </button>
      </div>
    </div>

    {/* 測試類型 ⭐ 新增 */}
    <div>
      <p className="text-sm text-gray-700 mb-1 font-medium">測試類型</p>
      <div className="flex gap-2">
        <button
          onClick={() => setTestType('pressure')}
          className={`px-3 py-2 rounded text-white text-sm font-medium shadow transition ${
            testType === 'pressure'
              ? 'bg-purple-600'
              : 'bg-gray-500 hover:bg-gray-600'
          }`}
        >
          {testMode === 'vacuum' || testMode === 'positive' ? '壓力測試' : '液壓測試'}
        </button>
        <button
          onClick={() => setTestType('flow')}
          className={`px-3 py-2 rounded text-white text-sm font-medium shadow transition ${
            testType === 'flow'
              ? 'bg-purple-600'
              : 'bg-gray-500 hover:bg-gray-600'
          }`}
        >
          {testMode === 'vacuum' || testMode === 'positive' ? '氣體流量' : '液體流量'}
        </button>
      </div>
    </div>
  </div>

  {/* 右側: 控制按鈕 */}
  <div className="flex gap-4">
    <button
      onClick={handleStartTest}
      disabled={!canStartTest}
      className={`px-6 py-3 rounded text-white text-lg font-medium shadow-md transition ${
        canStartTest
          ? 'bg-purple-600 hover:bg-purple-700'
          : 'bg-gray-400 cursor-not-allowed'
      }`}
    >
      啟動測試
    </button>

    <button
      onClick={handleStopTest}
      disabled={testStatus !== 'running'}
      className={`px-6 py-3 rounded text-white text-lg font-medium shadow-md transition ${
        testStatus === 'running'
          ? 'bg-red-600 hover:bg-red-700'
          : 'bg-gray-400 cursor-not-allowed'
      }`}
    >
      停止測試
    </button>
  </div>

</div>
```

**手動模式安全檢查邏輯** ⭐ **新增**:

```javascript
// 電磁閥安全組合驗證
const SAFE_VALVE_COMBINATIONS = {
  vacuum: {
    // 真空測試安全組合（來自原始 PPT）
    test: { A: false, B: true, C: false, D: false },
    vent: { A: false, B: false, C: false, D: false }
  },
  positive: {
    // 正壓測試安全組合
    test: { A: true, B: false, C: true, D: false },
    vent: { A: false, B: false, C: false, D: false }
  }
};

const validateValveCombo = (valveStatus, testMode) => {
  // 禁止的危險組合
  const dangerousCombos = [
    { A: true, B: true, C: false, D: false }, // 同時打開 A+B
    { A: false, B: false, C: true, D: true }, // 同時打開 C+D
    { A: true, B: true, C: true, D: true }    // 全部打開
  ];

  const isDangerous = dangerousCombos.some(combo =>
    combo.A === valveStatus.A &&
    combo.B === valveStatus.B &&
    combo.C === valveStatus.C &&
    combo.D === valveStatus.D
  );

  if (isDangerous) {
    return {
      valid: false,
      message: '⚠️ 警告: 此閥門組合可能造成設備損壞或安全風險！'
    };
  }

  return { valid: true };
};

// 使用方式
const toggleValve = (valve) => {
  if (testMode !== 'manual') return;

  const newStatus = { ...valveStatus, [valve]: !valveStatus[valve] };
  const validation = validateValveCombo(newStatus, testMode);

  if (!validation.valid) {
    setToastMessage(validation.message);
    return; // 不允許切換
  }

  setValveStatus(newStatus);
  publishCommand('pump/valves/control', newStatus);
};
```

---

### 4.3 壓力/流量變化曲線圖表區 (Recharts) ⚠️ **已修正 - 支援測試類型切換**

**重要**: 圖表根據測試類型 (testType) 動態切換 Y 軸標籤和數據源

```jsx
<div className="bg-white p-6 rounded shadow border border-gray-400 mb-6">
  {/* 動態標題 */}
  <h2 className="text-2xl font-bold mb-4 text-center text-blue-900">
    {testType === 'pressure'
      ? (testMode === 'vacuum' || testMode === 'positive' ? '壓力變化曲線' : '液壓變化曲線')
      : (testMode === 'vacuum' || testMode === 'positive' ? '氣體流量變化曲線' : '液體流量變化曲線')
    }
  </h2>

  {/* 圖表控制選項 */}
  <div className="flex justify-between items-center mb-2">
    <div className="text-sm text-gray-600">
      目前測試: <span className="font-bold text-purple-600">
        {testType === 'pressure' ? '壓力測試' : '流量測試'}
      </span>
    </div>

    {/* 可選: 顯示電流曲線疊加 */}
    <label className="flex items-center cursor-pointer">
      <input
        type="checkbox"
        checked={showCurrentLine}
        onChange={() => setShowCurrentLine(!showCurrentLine)}
        className="hidden"
      />
      <div className={`w-10 h-5 flex items-center rounded-full p-1 duration-300 ${
        showCurrentLine ? 'bg-green-500' : 'bg-gray-400'
      }`}>
        <div className={`bg-white w-4 h-4 rounded-full shadow-md transform duration-300 ${
          showCurrentLine ? 'translate-x-5' : 'translate-x-0'
        }`}></div>
      </div>
      <span className="ml-2 text-gray-700 text-sm">疊加電流曲線</span>
    </label>
  </div>

  {/* Recharts 圖表 */}
  <ResponsiveContainer width="100%" height={450}>
    <LineChart data={chartData}>
      <CartesianGrid stroke="#ccc" />

      <XAxis
        dataKey="time"
        type="number"
        domain={[0, 'auto']}
        tickFormatter={(tick) => `${tick}s`}
        label={{ value: '時間 (秒)', position: 'insideBottom', offset: -5 }}
      />

      {/* 主 Y 軸 (壓力或流量) ⭐ 流量單位區分 */}
      <YAxis
        yAxisId="primary"
        domain={testType === 'pressure'
          ? (testMode === 'vacuum' ? [-100, 0] : [0, 10])
          : [0, 100]
        }
        tickCount={12}
        label={{
          value: testType === 'pressure'
            ? '壓力 (kPa / kg/cm²)'
            : (testMode === 'vacuum' || testMode === 'positive'
                ? '氣體流量 (L/min)'  // ⭐ 氣體流量
                : '液體流量 (m³/h)'   // ⭐ 液體流量
              ),
          angle: -90,
          position: 'insideLeft'
        }}
      />

      {/* 次 Y 軸 (電流,可選) */}
      {showCurrentLine && (
        <YAxis
          yAxisId="current"
          orientation="right"
          domain={[0, 15]}
          label={{ value: '電流 (A)', angle: 90, position: 'insideRight' }}
        />
      )}

      <Tooltip
        labelFormatter={(label) => `時間: ${label.toFixed(2)} 秒`}
        formatter={(value, name) => [`${value.toFixed(2)}`, name]}
      />

      <Legend />

      {/* 主曲線 (壓力或流量) */}
      <Line
        yAxisId="primary"
        type="monotone"
        dataKey={testType === 'pressure' ? 'pressure' : 'flow'}
        stroke={testType === 'pressure' ? 'red' : 'blue'}
        strokeWidth={3}
        dot={false}
        name={testType === 'pressure'
          ? (testMode === 'vacuum' || testMode === 'positive' ? '壓力' : '液壓')
          : (testMode === 'vacuum' || testMode === 'positive' ? '氣體流量' : '液體流量')
        }
      />

      {/* 電流曲線 (可選疊加) */}
      {showCurrentLine && (
        <Line
          yAxisId="current"
          type="monotone"
          dataKey="current"
          stroke="orange"
          strokeWidth={2}
          dot={false}
          name="電流"
          strokeDasharray="5 5"
        />
      )}
    </LineChart>
  </ResponsiveContainer>

  {/* 右下角即時數值疊加顯示 ⭐ 單位區分 */}
  <div className="flex gap-4 mt-4 justify-end">
    <div className="bg-blue-50 border-2 border-blue-300 rounded p-3 text-center min-w-[150px]">
      <p className="text-sm text-gray-700 mb-1">
        {testType === 'pressure' ? '即時壓力' : '即時流量'}
      </p>
      <p className="text-4xl font-bold text-blue-600">
        {testType === 'pressure'
          ? realtimePressure.toFixed(1)
          : realtimeFlow.toFixed(1)
        }
      </p>
      <p className="text-sm text-gray-600">
        {testType === 'pressure'
          ? 'kPa'
          : (testMode === 'vacuum' || testMode === 'positive' ? 'L/min' : 'm³/h')
        }
      </p>
    </div>

    <div className="bg-orange-50 border-2 border-orange-300 rounded p-3 text-center min-w-[150px]">
      <p className="text-sm text-gray-700 mb-1">即時電流</p>
      <p className="text-4xl font-bold text-orange-800">
        {realtimeCurrent.toFixed(1)}
      </p>
      <p className="text-sm text-gray-600">A</p>
    </div>

    <div className="bg-gray-50 border-2 border-gray-300 rounded p-3 text-center min-w-[150px]">
      <p className="text-sm text-gray-700 mb-1">測試時間</p>
      <p className="text-2xl font-bold text-gray-700">
        {formatTime(elapsedTime)}
      </p>
      <p className="text-sm text-gray-600">
        {pumpStatus === 'running' ? '🟢 運轉中' : '⚪ 停止'}
      </p>
    </div>
  </div>

  {/* 測試完成後顯示儲存按鈕 */}
  {testCompleted && (
    <div className="mt-4 p-4 bg-green-50 border border-green-300 rounded flex items-center justify-between">
      <span className="text-green-800 font-medium">✓ 測試完成</span>
      <div className="flex gap-2 items-center">
        <input
          type="text"
          value={filename}
          onChange={(e) => setFilename(e.target.value)}
          placeholder="檔名備註(可不填)"
          className="border border-blue-500 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={() => saveChartWithTimestamp(chartData, filename)}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 shadow"
        >
          儲存圖表
        </button>
      </div>
    </div>
  )}
</div>
```

### 4.4 參考數據 / 比對資料庫表格 ⭐ **新增**

**重要**: 依照原始 PPT 第 298-344 行需求,參考數據表格應在主控台頂部顯示,供測試時即時比對

```jsx
<div className="bg-white p-6 rounded shadow border border-gray-400 mb-6">
  <div className="flex justify-between items-center mb-4">
    <h2 className="text-xl font-bold text-blue-900">📊 參考數據 / 比對資料庫</h2>
    <div className="flex gap-2">
      <select
        className="px-3 py-2 border border-gray-400 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        value={selectedReferenceId}
        onChange={(e) => loadReferenceData(e.target.value)}
      >
        <option value="">選擇參考數據...</option>
        {referenceDataList.map(ref => (
          <option key={ref.id} value={ref.id}>
            {ref.pumpModel} - {ref.testType} - {ref.date}
          </option>
        ))}
      </select>
      <button
        onClick={() => clearReferenceData()}
        className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
      >
        清除
      </button>
    </div>
  </div>

  {selectedReference ? (
    <div className="border border-gray-300 rounded overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="bg-blue-100">
          <tr>
            <th className="px-4 py-3 text-left">型號</th>
            <th className="px-4 py-3 text-left">功能</th>
            <th className="px-4 py-3 text-left">運轉</th>
            <th className="px-4 py-3 text-left">電源</th>
            <th className="px-4 py-3 text-left">額定電力</th>
            <th className="px-4 py-3 text-left">
              {selectedReference.testType === 'pressure' ? '壓力值' : '流量值'}
            </th>
            <th className="px-4 py-3 text-left">恆壓電流</th>
            <th className="px-4 py-3 text-left">儲存日期</th>
            <th className="px-4 py-3 text-left">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr className="border-b border-gray-200 bg-white">
            <td className="px-4 py-3 font-medium">{selectedReference.pumpModel}</td>
            <td className="px-4 py-3">{selectedReference.pumpFunction}</td>
            <td className="px-4 py-3">{selectedReference.operationMode}</td>
            <td className="px-4 py-3">{selectedReference.powerSource}</td>
            <td className="px-4 py-3">{selectedReference.ratedPower}W</td>
            <td className="px-4 py-3 font-bold text-blue-600">
              {selectedReference.testType === 'pressure'
                ? `${selectedReference.pressureValue} kPa`
                : `${selectedReference.flowValue} L/min`
              }
            </td>
            <td className="px-4 py-3 font-bold text-orange-800">
              {selectedReference.steadyCurrent} A
            </td>
            <td className="px-4 py-3 text-xs text-gray-600">
              {selectedReference.date}
            </td>
            <td className="px-4 py-3">
              <button
                onClick={() => deleteReferenceData(selectedReference.id)}
                className="text-red-600 hover:text-red-700 text-sm"
              >
                刪除
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      {/* 比對提示 */}
      {testStatus === 'running' && (
        <div className="p-3 bg-yellow-50 border-t border-yellow-200">
          <p className="text-sm text-yellow-800">
            💡 測試中: 參考值
            <span className="font-bold mx-1">
              {selectedReference.testType === 'pressure'
                ? `${selectedReference.pressureValue} kPa`
                : `${selectedReference.flowValue} L/min`
              }
            </span>
            / 即時值
            <span className="font-bold mx-1">
              {testType === 'pressure'
                ? `${realtimePressure.toFixed(1)} kPa`
                : `${realtimeFlow.toFixed(1)} L/min`
              }
            </span>
            / 差異
            <span className={`font-bold mx-1 ${
              Math.abs((testType === 'pressure' ? realtimePressure : realtimeFlow) -
                (selectedReference.testType === 'pressure' ? selectedReference.pressureValue : selectedReference.flowValue)) > 5
                ? 'text-red-600'
                : 'text-green-600'
            }`}>
              {testType === 'pressure'
                ? `${(realtimePressure - selectedReference.pressureValue).toFixed(1)} kPa`
                : `${(realtimeFlow - selectedReference.flowValue).toFixed(1)} L/min`
              }
            </span>
          </p>
        </div>
      )}
    </div>
  ) : (
    <div className="p-8 text-center text-gray-500 bg-gray-50 rounded border border-gray-300">
      <p className="text-lg">尚未載入參考數據</p>
      <p className="text-sm mt-1">請從上方下拉選單選擇參考數據進行比對</p>
    </div>
  )}
</div>
```

### 4.5 當前測試數據表格 ⚠️ **已修正 - 支援壓力/流量切換**

**重要**: 表格欄位根據測試類型動態調整

```jsx
<div className="bg-white p-6 rounded shadow border border-gray-400">
  <h2 className="text-xl font-bold mb-4 text-blue-900">📋 當前測試數據</h2>

  <div className="border border-gray-300 rounded overflow-x-auto">
    <table className="w-full text-sm">
      <thead className="bg-gray-200">
        <tr>
          <th className="px-4 py-3 text-left">型號</th>
          <th className="px-4 py-3 text-left">功能</th>
          <th className="px-4 py-3 text-left">測試模式</th>
          <th className="px-4 py-3 text-left">測試類型</th>
          <th className="px-4 py-3 text-left">電源</th>
          <th className="px-4 py-3 text-left">額定電力</th>
          <th className="px-4 py-3 text-left">
            {testType === 'pressure' ? '即時壓力' : '即時流量'}
          </th>
          <th className="px-4 py-3 text-left">即時電流</th>
          <th className="px-4 py-3 text-left">測試時間</th>
        </tr>
      </thead>
      <tbody>
        <tr className="border-b border-gray-200">
          <td className="px-4 py-3 font-medium">{testConfig.pumpModel || '-'}</td>
          <td className="px-4 py-3">
            {testMode === 'vacuum' ? '真空' : testMode === 'positive' ? '正壓' : '手動'}
          </td>
          <td className="px-4 py-3">
            {testMode === 'vacuum' ? '真空幫浦' : testMode === 'positive' ? '正壓幫浦' : '手動測試'}
          </td>
          <td className="px-4 py-3">
            <span className={`px-2 py-1 rounded text-xs font-medium ${
              testType === 'pressure' ? 'bg-red-100 text-red-800' : 'bg-blue-100 text-blue-800'
            }`}>
              {testType === 'pressure'
                ? (testMode === 'vacuum' || testMode === 'positive' ? '壓力測試' : '液壓測試')
                : (testMode === 'vacuum' || testMode === 'positive' ? '氣體流量' : '液體流量')
              }
            </span>
          </td>
          <td className="px-4 py-3">{testConfig.powerSource || '-'}</td>
          <td className="px-4 py-3">{testConfig.ratedPower || '-'}W</td>
          <td className="px-4 py-3 font-bold text-blue-600">
            {testType === 'pressure'
              ? `${realtimePressure.toFixed(1)} kPa`
              : `${realtimeFlow.toFixed(1)} L/min`
            }
          </td>
          <td className="px-4 py-3 font-bold text-orange-800">
            {realtimeCurrent.toFixed(1)} A
          </td>
          <td className="px-4 py-3">{formatTime(elapsedTime)}</td>
        </tr>
      </tbody>
    </table>
  </div>

  {/* 操作按鈕 */}
  <div className="flex gap-4 mt-4">
    <button
      onClick={saveToReferenceDB}
      disabled={!testCompleted}
      className={`px-4 py-2 rounded text-white font-medium shadow transition ${
        testCompleted
          ? 'bg-blue-600 hover:bg-blue-700'
          : 'bg-gray-400 cursor-not-allowed'
      }`}
    >
      儲存至參考資料庫
    </button>

    <button
      onClick={saveToTestDB}
      disabled={!testCompleted}
      className={`px-4 py-2 rounded text-white font-medium shadow transition ${
        testCompleted
          ? 'bg-green-600 hover:bg-green-700'
          : 'bg-gray-400 cursor-not-allowed'
      }`}
    >
      儲存至測試庫
    </button>

    <button
      onClick={exportToCSV}
      disabled={!testCompleted}
      className={`px-4 py-2 rounded text-white font-medium shadow transition ${
        testCompleted
          ? 'bg-purple-600 hover:bg-purple-700'
          : 'bg-gray-400 cursor-not-allowed'
      }`}
    >
      匯出 CSV
    </button>
  </div>
</div>
```

**CSV 匯出功能規格** ⭐ **新增詳細說明**:

```javascript
// CSV 匯出函數
const exportToCSV = async () => {
  if (!testCompleted || chartData.length === 0) return;

  // 1. 檔名格式: {型號}_{測試類型}_{日期}.csv
  const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '');
  const testTypeLabel = testType === 'pressure' ? '壓力測試' : '流量測試';
  const filename = `${testConfig.pumpModel}_${testTypeLabel}_${timestamp}`;

  // 2. CSV 欄位 - 時間序列數據
  const csvHeaders = [
    '時間 (秒)',
    testType === 'pressure'
      ? '壓力 (kPa)'
      : (testMode === 'vacuum' || testMode === 'positive' ? '氣體流量 (L/min)' : '液體流量 (m³/h)'),
    '電流 (A)',
    '時間戳記'
  ];

  // 3. 生成 CSV 內容
  const csvRows = [
    // 表頭
    csvHeaders.join(','),

    // 測試摘要資訊
    `# 幫浦型號: ${testConfig.pumpModel}`,
    `# 測試模式: ${testMode === 'vacuum' ? '真空幫浦' : testMode === 'positive' ? '正壓幫浦' : '手動測試'}`,
    `# 測試類型: ${testTypeLabel}`,
    `# 測試日期: ${new Date().toLocaleString('zh-TW')}`,
    `# 測試時長: ${formatTime(elapsedTime)}`,
    `# 平均值: ${testType === 'pressure' ? avgPressure.toFixed(2) : avgFlow.toFixed(2)}`,
    `# 最大值: ${testType === 'pressure' ? maxPressure.toFixed(2) : maxFlow.toFixed(2)}`,
    '',

    // 數據行
    ...chartData.map(row => [
      row.time.toFixed(2),
      testType === 'pressure' ? row.pressure.toFixed(2) : row.flow.toFixed(2),
      row.current.toFixed(2),
      new Date(row.timestamp).toISOString()
    ].join(','))
  ];

  const csvContent = csvRows.join('\n');
  const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });

  // 4. 同時匯出圖表圖片
  const chartElement = document.querySelector('.recharts-wrapper');
  const chartImage = await html2canvas(chartElement);
  const imageBlob = await new Promise(resolve => chartImage.toBlob(resolve));

  // 5. 打包成 ZIP 檔案
  const JSZip = require('jszip');
  const zip = new JSZip();
  zip.file(`${filename}.csv`, blob);
  zip.file(`${filename}_chart.png`, imageBlob);

  const zipBlob = await zip.generateAsync({ type: 'blob' });

  // 6. 下載
  const link = document.createElement('a');
  link.href = URL.createObjectURL(zipBlob);
  link.download = `${filename}.zip`;
  link.click();

  setToastMessage(`✓ 已匯出: ${filename}.zip (含 CSV + 圖表圖片)`);
};
```

**檔案結構範例**:
```
DMM9200_壓力測試_20251113_143025.zip
├── DMM9200_壓力測試_20251113_143025.csv
└── DMM9200_壓力測試_20251113_143025_chart.png
```

**CSV 內容範例**:
```csv
時間 (秒),壓力 (kPa),電流 (A),時間戳記
# 幫浦型號: DMM9200
# 測試模式: 真空幫浦
# 測試類型: 壓力測試
# 測試日期: 2025/11/13 下午2:30:25
# 測試時長: 00:15:32
# 平均值: -87.35
# 最大值: -95.8

0.00,-0.12,0.05,2025-11-13T14:30:25.123Z
0.50,-5.48,0.82,2025-11-13T14:30:25.623Z
1.00,-12.35,1.45,2025-11-13T14:30:26.123Z
1.50,-18.92,2.18,2025-11-13T14:30:26.623Z
...
```

---

## 5. 測試設定頁面

### 5.1 單頁表單設計 (簡化版)

不使用多步驟 wizard,改用單頁表單,更直觀快速。

```jsx
<div className="p-8 bg-white min-h-screen">

  <h1 className="text-3xl font-bold text-blue-900 text-center mb-8">測試參數設定</h1>

  <div className="max-w-4xl mx-auto bg-gray-100 p-8 rounded shadow-md border border-gray-400">

    {/* 測試模式選擇 */}
    <div className="mb-6">
      <label className="block text-lg font-semibold text-gray-800 mb-3">
        測試模式 <span className="text-red-600">*</span>
      </label>
      <div className="flex gap-4">
        {['vacuum', 'positive', 'manual'].map(mode => (
          <button
            key={mode}
            onClick={() => setFormData({...formData, testMode: mode})}
            className={`flex-1 px-6 py-4 rounded border-2 text-lg font-medium transition ${
              formData.testMode === mode
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white text-gray-700 border-gray-300 hover:border-blue-400'
            }`}
          >
            {mode === 'vacuum' && '真空幫浦'}
            {mode === 'positive' && '正壓幫浦'}
            {mode === 'manual' && '手動測試'}
          </button>
        ))}
      </div>
    </div>

    {/* 測試類型選擇 ⭐ 新增 */}
    <div className="mb-6">
      <label className="block text-lg font-semibold text-gray-800 mb-3">
        測試類型 <span className="text-red-600">*</span>
      </label>
      <div className="flex gap-4">
        {[
          {
            value: 'pressure',
            label: formData.testMode === 'vacuum' || formData.testMode === 'positive'
              ? '壓力測試'
              : '液壓測試',
            desc: formData.testMode === 'vacuum'
              ? '測試真空壓力 (kPa)'
              : formData.testMode === 'positive'
                ? '測試正壓力 (kg/cm²)'
                : '測試液體壓力'
          },
          {
            value: 'flow',
            label: formData.testMode === 'vacuum' || formData.testMode === 'positive'
              ? '氣體流量'
              : '液體流量',
            desc: '測試流量 (L/min)'
          }
        ].map(type => (
          <button
            key={type.value}
            onClick={() => setFormData({...formData, testType: type.value})}
            className={`flex-1 px-6 py-4 rounded border-2 transition ${
              formData.testType === type.value
                ? 'bg-purple-600 text-white border-purple-600'
                : 'bg-white text-gray-700 border-gray-300 hover:border-purple-400'
            }`}
          >
            <p className="text-lg font-medium">{type.label}</p>
            <p className="text-sm mt-1 opacity-80">{type.desc}</p>
          </button>
        ))}
      </div>
      <p className="mt-2 text-sm text-gray-600">
        💡 依照原始 PPT 需求: 空氣部分可測「空壓 or 氣體流量」/ 液體部分可測「液壓 or 液體流量」
      </p>
    </div>

    {/* 幫浦型號 ⭐ 改為可搜尋下拉選單 + 手動輸入 */}
    <div className="mb-6">
      <label className="block text-lg font-semibold text-gray-800 mb-2">
        幫浦型號 <span className="text-red-600">*</span>
      </label>

      {/* 可搜尋下拉選單 */}
      <div className="relative">
        <input
          type="text"
          value={formData.pumpModel}
          onChange={(e) => {
            setFormData({...formData, pumpModel: e.target.value});
            setShowModelSuggestions(true);
            setFilteredModels(
              PUMP_MODELS.filter(model =>
                model.toLowerCase().includes(e.target.value.toLowerCase())
              )
            );
          }}
          onFocus={() => setShowModelSuggestions(true)}
          placeholder="搜尋或輸入幫浦型號 (例: DMM9200)"
          className="w-full px-4 py-3 border border-gray-400 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg"
        />

        {/* 下拉選單圖示 */}
        <button
          type="button"
          onClick={() => setShowModelSuggestions(!showModelSuggestions)}
          className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500"
        >
          ▼
        </button>

        {/* 搜尋建議列表 */}
        {showModelSuggestions && filteredModels.length > 0 && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-gray-400 rounded shadow-lg max-h-64 overflow-y-auto">
            {filteredModels.map((model, index) => (
              <div
                key={index}
                onClick={() => {
                  setFormData({...formData, pumpModel: model});
                  setShowModelSuggestions(false);
                }}
                className="px-4 py-3 hover:bg-blue-50 cursor-pointer border-b border-gray-200 last:border-b-0"
              >
                <div className="font-medium text-gray-800">{model}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {PUMP_MODEL_SPECS[model]?.description || ''}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <p className="mt-2 text-sm text-gray-600">
        💡 支援 50+ 型號快速搜尋，或直接輸入特殊型號
      </p>

      {/* 型號資料庫範例 */}
      <details className="mt-2">
        <summary className="text-sm text-blue-600 cursor-pointer">顯示常用型號列表</summary>
        <div className="mt-2 p-3 bg-gray-50 rounded text-xs max-h-48 overflow-y-auto">
          <p className="font-semibold mb-1">真空幫浦:</p>
          <p>DMM9200, DMM9250, SSU2050, SSU2070, VPX-100, VPX-150...</p>
          <p className="font-semibold mt-2 mb-1">正壓幫浦:</p>
          <p>PPM-5000, PPM-7500, HPU-300, HPU-500, ACP-200...</p>
          <p className="font-semibold mt-2 mb-1">水幫浦:</p>
          <p>WPM-1000, WPM-1500, LPX-250, LPX-350...</p>
        </div>
      </details>
    </div>

    {/* 型號資料庫常數（前端） */}
    <script type="text/javascript">
    const PUMP_MODELS = [
      // 真空幫浦 (20+ models)
      'DMM9200', 'DMM9250', 'DMM9300', 'SSU2050', 'SSU2070', 'SSU2100',
      'VPX-100', 'VPX-150', 'VPX-200', 'VCM-5000', 'VCM-7500',

      // 正壓幫浦 (15+ models)
      'PPM-5000', 'PPM-7500', 'PPM-10K', 'HPU-300', 'HPU-500', 'HPU-750',
      'ACP-200', 'ACP-350', 'ACP-500',

      // 水幫浦 (15+ models)
      'WPM-1000', 'WPM-1500', 'WPM-2000', 'LPX-250', 'LPX-350', 'LPX-500',
      'HWP-300', 'HWP-600'
      // ... 可擴展至 50+ 型號
    ];

    const PUMP_MODEL_SPECS = {
      'DMM9200': { description: '真空幫浦, -100kPa, 1500W', power: 1500 },
      'PPM-5000': { description: '正壓幫浦, 8 kg/cm², 2200W', power: 2200 },
      'WPM-1000': { description: '水幫浦, 液壓/液體流量, 1200W', power: 1200 }
      // ... 更多規格
    };
    </script>

    {/* 電源設定 */}
    <div className="mb-6">
      <label className="block text-lg font-semibold text-gray-800 mb-3">
        電源設定 <span className="text-red-600">*</span>
      </label>

      {/* AC 電源 */}
      <div className="mb-4">
        <p className="text-md font-medium text-gray-700 mb-2">AC 交流電源</p>
        <div className="flex gap-4">
          {[
            { value: 'AC110-1P', label: '110V 單相' },
            { value: 'AC220-1P', label: '220V 單相' },
            { value: 'AC220-3P', label: '220V 三相' }
          ].map(option => (
            <button
              key={option.value}
              onClick={() => setFormData({...formData, powerSource: option.value})}
              className={`px-4 py-2 rounded border text-base transition ${
                formData.powerSource === option.value
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:border-blue-400'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* DC 電源 */}
      <div>
        <p className="text-md font-medium text-gray-700 mb-2">DC 直流電源</p>
        <div className="flex gap-4 items-center">
          {['DC12V', 'DC24V'].map(option => (
            <button
              key={option}
              onClick={() => setFormData({...formData, powerSource: option})}
              className={`px-4 py-2 rounded border text-base transition ${
                formData.powerSource === option
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:border-blue-400'
              }`}
            >
              {option}
            </button>
          ))}
          <span className="text-gray-600">或其他:</span>
          <input
            type="number"
            placeholder="電壓 (V)"
            className="w-24 px-3 py-2 border border-gray-400 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            onChange={(e) => setFormData({...formData, powerSource: `DC${e.target.value}V`})}
          />
          <span className="text-gray-600">V</span>
        </div>
      </div>
    </div>

    {/* 額定電力消耗 */}
    <div className="mb-6">
      <label className="block text-lg font-semibold text-gray-800 mb-2">
        額定電力消耗 (W) <span className="text-red-600">*</span>
      </label>
      <input
        type="number"
        value={formData.ratedPower}
        onChange={(e) => setFormData({...formData, ratedPower: e.target.value})}
        placeholder="例: 1500"
        className="w-full px-4 py-3 border border-gray-400 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg"
      />
    </div>

    {/* 最大電流限制 */}
    <div className="mb-6">
      <label className="block text-lg font-semibold text-gray-800 mb-2">
        最大電流限制 (A)
      </label>
      <input
        type="number"
        value={formData.maxCurrent}
        onChange={(e) => setFormData({...formData, maxCurrent: e.target.value})}
        placeholder="例: 10.0"
        className="w-full px-4 py-3 border border-gray-400 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg"
      />
      <p className="mt-1 text-sm text-gray-600">系統將在電流超過此值時停止測試</p>
    </div>

    {/* 進階設定 (可摺疊) */}
    <div className="mb-6">
      <button
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="flex items-center gap-2 text-lg font-semibold text-blue-600 hover:text-blue-700"
      >
        {showAdvanced ? '▼' : '▶'} 進階設定 (可選)
      </button>

      {showAdvanced && (
        <div className="mt-4 p-4 bg-white rounded border border-gray-300">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-md font-medium text-gray-700 mb-1">
                壓力恆定判斷時間 (分鐘)
              </label>
              <input
                type="number"
                value={formData.stabilityTime}
                onChange={(e) => setFormData({...formData, stabilityTime: e.target.value})}
                placeholder="預設: 5"
                className="w-full px-3 py-2 border border-gray-400 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-md font-medium text-gray-700 mb-1">
                測試超時時間 (分鐘)
              </label>
              <input
                type="number"
                value={formData.timeout}
                onChange={(e) => setFormData({...formData, timeout: e.target.value})}
                placeholder="預設: 60"
                className="w-full px-3 py-2 border border-gray-400 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-md font-medium text-gray-700 mb-1">
                正壓上限 (kg/cm²)
              </label>
              <input
                type="number"
                value={formData.maxPositivePressure}
                onChange={(e) => setFormData({...formData, maxPositivePressure: e.target.value})}
                placeholder="預設: 8"
                className="w-full px-3 py-2 border border-gray-400 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-md font-medium text-gray-700 mb-1">
                負壓上限 (kPa)
              </label>
              <input
                type="number"
                value={formData.maxVacuum}
                onChange={(e) => setFormData({...formData, maxVacuum: e.target.value})}
                placeholder="預設: -100"
                className="w-full px-3 py-2 border border-gray-400 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>
      )}
    </div>

    {/* 儲存目標 */}
    <div className="mb-8">
      <label className="block text-lg font-semibold text-gray-800 mb-3">
        測試結果儲存至
      </label>
      <div className="flex gap-4">
        {[
          { value: 'reference', label: '參考數據庫', desc: '供日後比對使用' },
          { value: 'test', label: '測試庫', desc: '一般測試記錄' }
        ].map(option => (
          <button
            key={option.value}
            onClick={() => setFormData({...formData, saveTarget: option.value})}
            className={`flex-1 px-6 py-4 rounded border-2 transition ${
              formData.saveTarget === option.value
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white text-gray-700 border-gray-300 hover:border-blue-400'
            }`}
          >
            <p className="text-lg font-medium">{option.label}</p>
            <p className="text-sm mt-1 opacity-80">{option.desc}</p>
          </button>
        ))}
      </div>
    </div>

    {/* 預覽摘要 */}
    <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded">
      <h3 className="text-lg font-semibold text-blue-900 mb-2">設定摘要</h3>
      <ul className="text-sm text-blue-800 space-y-1">
        <li>• 測試模式: {formData.testMode === 'vacuum' && '真空幫浦自動測試'}</li>
        <li>• 幫浦型號: {formData.pumpModel || '(未填寫)'}</li>
        <li>• 電源: {formData.powerSource || '(未選擇)'}</li>
        <li>• 額定電力: {formData.ratedPower || '(未填寫)'} W</li>
        <li>• 儲存目標: {formData.saveTarget === 'reference' ? '參考數據庫' : '測試庫'}</li>
      </ul>
    </div>

    {/* 操作按鈕 */}
    <div className="flex gap-4">
      <button
        onClick={handleSaveAndStart}
        disabled={!isFormValid}
        className={`flex-1 px-6 py-3 rounded text-white text-lg font-medium shadow-md transition ${
          isFormValid
            ? 'bg-purple-600 hover:bg-purple-700'
            : 'bg-gray-400 cursor-not-allowed'
        }`}
      >
        儲存並開始測試
      </button>

      <button
        onClick={handleSaveOnly}
        disabled={!isFormValid}
        className={`flex-1 px-6 py-3 rounded text-white text-lg font-medium shadow-md transition ${
          isFormValid
            ? 'bg-blue-600 hover:bg-blue-700'
            : 'bg-gray-400 cursor-not-allowed'
        }`}
      >
        僅儲存設定
      </button>

      <button
        onClick={handleCancel}
        className="px-6 py-3 rounded bg-gray-500 text-white text-lg font-medium shadow-md hover:bg-gray-600 transition"
      >
        取消
      </button>
    </div>

  </div>
</div>
```

---

## 6. 數據管理頁面

### 6.1 Layout 設計

```jsx
<div className="p-8 bg-white min-h-screen">

  <h1 className="text-3xl font-bold text-blue-900 text-center mb-8">測試數據管理</h1>

  {/* Tab 切換 */}
  <div className="max-w-6xl mx-auto mb-6">
    <div className="flex gap-2 border-b border-gray-300">
      {['history', 'reference', 'comparison'].map(tab => (
        <button
          key={tab}
          onClick={() => setActiveTab(tab)}
          className={`px-6 py-3 text-lg font-medium transition ${
            activeTab === tab
              ? 'bg-blue-600 text-white rounded-t'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300 rounded-t'
          }`}
        >
          {tab === 'history' && '歷史記錄'}
          {tab === 'reference' && '參考資料庫'}
          {tab === 'comparison' && '數據比對'}
        </button>
      ))}
    </div>
  </div>

  {/* 內容區 */}
  <div className="max-w-6xl mx-auto">
    {activeTab === 'history' && <HistoryTab />}
    {activeTab === 'reference' && <ReferenceTab />}
    {activeTab === 'comparison' && <ComparisonTab />}
  </div>
</div>
```

### 6.2 歷史記錄 Tab

```jsx
function HistoryTab() {
  return (
    <div className="bg-gray-100 p-6 rounded shadow-md border border-gray-400">

      {/* 搜尋與篩選 */}
      <div className="mb-6 p-4 bg-white rounded border border-gray-300">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">搜尋與篩選</h3>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">幫浦型號</label>
            <input
              type="text"
              placeholder="搜尋型號"
              className="w-full px-3 py-2 border border-gray-400 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">測試日期 (起)</label>
            <input
              type="date"
              className="w-full px-3 py-2 border border-gray-400 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">測試日期 (迄)</label>
            <input
              type="date"
              className="w-full px-3 py-2 border border-gray-400 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        <div className="flex gap-4 mt-4">
          <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            搜尋
          </button>
          <button className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600">
            重置
          </button>
        </div>
      </div>

      {/* 數據表格 */}
      <div className="bg-white rounded border border-gray-300 overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-200">
            <tr>
              <th className="px-4 py-3 text-left">
                <input type="checkbox" />
              </th>
              <th className="px-4 py-3 text-left">日期</th>
              <th className="px-4 py-3 text-left">型號</th>
              <th className="px-4 py-3 text-left">模式</th>
              <th className="px-4 py-3 text-left">電源</th>
              <th className="px-4 py-3 text-left">壓力 (kPa)</th>
              <th className="px-4 py-3 text-left">電流 (A)</th>
              <th className="px-4 py-3 text-left">結果</th>
              <th className="px-4 py-3 text-left">操作</th>
            </tr>
          </thead>
          <tbody>
            {testHistory.map((record, index) => (
              <tr key={index} className="border-b border-gray-200 hover:bg-gray-50">
                <td className="px-4 py-3">
                  <input type="checkbox" />
                </td>
                <td className="px-4 py-3">{record.date}</td>
                <td className="px-4 py-3">{record.model}</td>
                <td className="px-4 py-3">{record.mode}</td>
                <td className="px-4 py-3">{record.power}</td>
                <td className="px-4 py-3 font-bold text-blue-600">{record.pressure}</td>
                <td className="px-4 py-3 font-bold text-orange-800">{record.current}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    record.result === 'PASS'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {record.result}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <button className="text-blue-600 hover:text-blue-700 mr-2">查看</button>
                  <button className="text-red-600 hover:text-red-700">刪除</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 分頁 */}
      <div className="mt-4 flex justify-between items-center">
        <p className="text-sm text-gray-600">顯示 1-20 / 共 156 筆</p>
        <div className="flex gap-2">
          <button className="px-3 py-1 bg-gray-300 rounded hover:bg-gray-400">上一頁</button>
          <button className="px-3 py-1 bg-blue-600 text-white rounded">1</button>
          <button className="px-3 py-1 bg-gray-300 rounded hover:bg-gray-400">2</button>
          <button className="px-3 py-1 bg-gray-300 rounded hover:bg-gray-400">3</button>
          <button className="px-3 py-1 bg-gray-300 rounded hover:bg-gray-400">下一頁</button>
        </div>
      </div>

      {/* 批次操作 */}
      <div className="mt-6 p-4 bg-white rounded border border-gray-300">
        <p className="text-sm text-gray-700 mb-2">已選取 3 筆資料</p>
        <div className="flex gap-4">
          <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            匯出 CSV
          </button>
          <button className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
            加入比對
          </button>
          <button className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
            批次刪除
          </button>
        </div>
      </div>

    </div>
  );
}
```

### 6.3 數據比對 Tab

```jsx
function ComparisonTab() {
  return (
    <div className="bg-gray-100 p-6 rounded shadow-md border border-gray-400">

      <h3 className="text-xl font-bold text-blue-900 mb-4">數據比對</h3>

      {/* 選擇比對數據 */}
      <div className="grid grid-cols-2 gap-6 mb-6">
        {/* 參考數據 */}
        <div className="bg-white p-4 rounded border border-gray-300">
          <h4 className="text-lg font-semibold text-gray-800 mb-2">參考數據</h4>
          <select className="w-full px-3 py-2 border border-gray-400 rounded">
            <option>選擇參考數據...</option>
            <option>DMM9200 - 2025-11-01</option>
            <option>SSU2050 - 2025-10-28</option>
          </select>
          <div className="mt-4 p-3 bg-gray-50 rounded text-sm">
            <p><span className="font-medium">型號:</span> DMM9200</p>
            <p><span className="font-medium">日期:</span> 2025-11-01</p>
            <p><span className="font-medium">壓力:</span> <span className="text-blue-600 font-bold">-95.5 kPa</span></p>
            <p><span className="font-medium">電流:</span> <span className="text-orange-800 font-bold">6.8 A</span></p>
          </div>
        </div>

        {/* 當前數據 */}
        <div className="bg-white p-4 rounded border border-gray-300">
          <h4 className="text-lg font-semibold text-gray-800 mb-2">當前數據</h4>
          <select className="w-full px-3 py-2 border border-gray-400 rounded">
            <option>選擇測試數據...</option>
            <option>DMM9200 - 2025-11-12</option>
          </select>
          <div className="mt-4 p-3 bg-gray-50 rounded text-sm">
            <p><span className="font-medium">型號:</span> DMM9200</p>
            <p><span className="font-medium">日期:</span> 2025-11-12</p>
            <p><span className="font-medium">壓力:</span> <span className="text-blue-600 font-bold">-93.2 kPa</span></p>
            <p><span className="font-medium">電流:</span> <span className="text-orange-800 font-bold">7.1 A</span></p>
          </div>
        </div>
      </div>

      {/* 差異分析 */}
      <div className="bg-white p-6 rounded border border-gray-300 mb-6">
        <h4 className="text-lg font-semibold text-gray-800 mb-4">差異分析</h4>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
            <p className="font-medium text-gray-700">壓力差異</p>
            <p className="text-xl font-bold text-yellow-700 mt-1">-2.3 kPa (2.4%)</p>
            <p className="text-xs text-yellow-600 mt-1">⚠ 注意</p>
          </div>
          <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
            <p className="font-medium text-gray-700">電流差異</p>
            <p className="text-xl font-bold text-yellow-700 mt-1">+0.3 A (4.4%)</p>
            <p className="text-xs text-yellow-600 mt-1">⚠ 注意</p>
          </div>
        </div>
      </div>

      {/* 曲線對比圖 */}
      <div className="bg-white p-6 rounded border border-gray-300">
        <h4 className="text-lg font-semibold text-gray-800 mb-4">壓力曲線對比</h4>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart>
            <CartesianGrid stroke="#ccc" />
            <XAxis dataKey="time" label={{ value: '時間 (秒)', position: 'insideBottom' }} />
            <YAxis label={{ value: '壓力 (kPa)', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            <Line
              data={referenceData}
              type="monotone"
              dataKey="pressure"
              stroke="blue"
              strokeWidth={2}
              name="參考數據"
            />
            <Line
              data={currentData}
              type="monotone"
              dataKey="pressure"
              stroke="red"
              strokeWidth={2}
              strokeDasharray="5 5"
              name="當前數據"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* 操作按鈕 */}
      <div className="mt-6 flex gap-4">
        <button className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
          匯出比對報告
        </button>
        <button className="px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700">
          儲存此比對
        </button>
      </div>

    </div>
  );
}
```

---

## 7. 元件設計規範

### 7.1 狀態指示燈元件

```jsx
// components/StatusIndicator.jsx
function StatusIndicator({
  status,      // 'normal' | 'error'
  label,       // 顯示文字
  size = 'md'  // 'sm' | 'md' | 'lg'
}) {
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-10 h-10'
  };

  return (
    <div className="flex flex-col items-center bg-white p-3 rounded-lg shadow-md border border-gray-300 w-32 text-center">
      <div className={`${sizeClasses[size]} rounded-full shadow-md transition-colors duration-500 ${
        status === 'normal'
          ? 'bg-green-500 slow-flashing'
          : 'bg-red-500 flashing'
      }`}></div>
      <p className="mt-2 text-sm font-bold text-gray-800 break-words leading-tight whitespace-pre-wrap">
        {label}
      </p>
    </div>
  );
}

// 使用方式
<StatusIndicator
  status={pressureStatus === "正常" ? "normal" : "error"}
  label={pressureStatus === "正常" ? "壓力偵測正常" : "壓力傳輸錯誤"}
  size="md"
/>
```

### 7.2 Toggle 開關元件

```jsx
// components/ToggleSwitch.jsx
function ToggleSwitch({
  checked,
  onChange,
  label,
  disabled = false
}) {
  return (
    <label className="flex items-center cursor-pointer">
      <input
        type="checkbox"
        checked={checked}
        onChange={onChange}
        disabled={disabled}
        className="hidden"
      />
      <div className={`w-10 h-5 flex items-center rounded-full p-1 duration-300 ${
        checked ? 'bg-green-500' : 'bg-gray-400'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}>
        <div className={`bg-white w-4 h-4 rounded-full shadow-md transform duration-300 ${
          checked ? 'translate-x-5' : 'translate-x-0'
        }`}></div>
      </div>
      {label && <span className="ml-2 text-gray-700 text-sm">{label}</span>}
    </label>
  );
}

// 使用方式
<ToggleSwitch
  checked={showFlowLine}
  onChange={() => setShowFlowLine(!showFlowLine)}
  label="顯示流量數據"
/>
```

### 7.3 即時數值顯示卡片

```jsx
// components/RealtimeValueCard.jsx
function RealtimeValueCard({
  title,         // 卡片標題
  value,         // 數值
  unit,          // 單位
  valueColor,    // 數值顏色 (text-blue-600, text-orange-800)
  size = 'lg'    // 'md' | 'lg' | 'xl'
}) {
  const sizeClasses = {
    md: 'text-4xl',
    lg: 'text-5xl',
    xl: 'text-6xl'
  };

  return (
    <div className="bg-white p-6 rounded shadow border border-gray-300 text-center">
      <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
      <p className={`${sizeClasses[size]} font-bold ${valueColor} mt-2`}>
        {value}
      </p>
      <p className="text-2xl text-gray-600">{unit}</p>
    </div>
  );
}

// 使用方式
<RealtimeValueCard
  title="即時壓力"
  value={realtimePressure.toFixed(1)}
  unit="kPa"
  valueColor="text-blue-600"
  size="xl"
/>
```

### 7.4 Toast 通知元件

```jsx
// components/Toast.jsx
function Toast({ message, onClose, type = 'success' }) {
  const bgColors = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    info: 'bg-blue-500'
  };

  return (
    <div className={`fixed bottom-28 left-1/2 transform -translate-x-1/2 ${bgColors[type]} text-white p-3 rounded shadow-lg z-50`}>
      {message}
      <button
        className="mt-2 px-4 py-1 bg-gray-800 text-white rounded block mx-auto"
        onClick={onClose}
      >
        關閉
      </button>
    </div>
  );
}

// 使用方式
{toastMessage && (
  <Toast
    message={toastMessage}
    onClose={() => setToastMessage("")}
    type="success"
  />
)}
```

---

## 8. 狀態管理

### 8.1 使用 Context API (不使用 Redux)

基於 Air 專案的簡單性,使用 React Context API 足夠。

```javascript
// context/TestContext.jsx
import React, { createContext, useContext, useState, useRef } from 'react';

const TestContext = createContext();

export function TestProvider({ children }) {
  // 測試控制狀態
  const [testMode, setTestMode] = useState('vacuum'); // 'vacuum' | 'positive' | 'manual'
  const [testType, setTestType] = useState('pressure'); // ⭐ 新增: 'pressure' | 'flow'
  const [testStatus, setTestStatus] = useState('idle'); // 'idle' | 'running' | 'paused' | 'stopped'
  const [testCompleted, setTestCompleted] = useState(false);

  // 即時數據
  const [realtimePressure, setRealtimePressure] = useState(0);
  const [realtimeCurrent, setRealtimeCurrent] = useState(0);
  const [realtimeFlow, setRealtimeFlow] = useState(0); // ⭐ 流量數據

  // 圖表數據
  const [chartData, setChartData] = useState([]);
  const startTimeRef = useRef(null);

  // 系統狀態
  const [sensorStatus, setSensorStatus] = useState('正常'); // ⭐ 統一感測器狀態 (壓力/流量)
  const [currentSensorStatus, setCurrentSensorStatus] = useState('正常');
  const [relayStatus, setRelayStatus] = useState('正常');

  // 電磁閥狀態
  const [valveStatus, setValveStatus] = useState({ A: false, B: false, C: false, D: false });

  // 參考數據 ⭐ 新增
  const [selectedReference, setSelectedReference] = useState(null);
  const [referenceDataList, setReferenceDataList] = useState([]);

  // 測試配置
  const [testConfig, setTestConfig] = useState({
    pumpModel: '',
    testMode: 'vacuum',
    testType: 'pressure', // ⭐ 新增測試類型
    powerSource: '',
    ratedPower: 0,
    maxCurrent: 0,
    saveTarget: 'test'
  });

  const value = {
    // 狀態
    testMode, setTestMode,
    testType, setTestType, // ⭐ 新增
    testStatus, setTestStatus,
    testCompleted, setTestCompleted,
    realtimePressure, setRealtimePressure,
    realtimeCurrent, setRealtimeCurrent,
    realtimeFlow, setRealtimeFlow, // ⭐ 流量
    chartData, setChartData,
    startTimeRef,
    sensorStatus, setSensorStatus, // ⭐ 統一感測器狀態
    currentSensorStatus, setCurrentSensorStatus,
    relayStatus, setRelayStatus,
    valveStatus, setValveStatus,
    selectedReference, setSelectedReference, // ⭐ 參考數據
    referenceDataList, setReferenceDataList, // ⭐ 參考數據列表
    testConfig, setTestConfig
  };

  return (
    <TestContext.Provider value={value}>
      {children}
    </TestContext.Provider>
  );
}

export function useTest() {
  const context = useContext(TestContext);
  if (!context) {
    throw new Error('useTest must be used within TestProvider');
  }
  return context;
}
```

### 8.2 MQTT 整合 (Custom Hook)

```javascript
// hooks/useMQTT.js
import { useEffect, useRef } from 'react';
import mqtt from 'mqtt';
import config from '../pages/config';
import { useTest } from '../context/TestContext';

export function useMQTT() {
  const mqttClient = useRef(null);
  const {
    testType, // ⭐ 新增: 判斷測試類型
    setRealtimePressure,
    setRealtimeCurrent,
    setRealtimeFlow,
    setChartData,
    setValveStatus,
    setSensorStatus, // ⭐ 統一感測器狀態
    setCurrentSensorStatus,
    setRelayStatus,
    startTimeRef,
    testStatus
  } = useTest();

  const lastSensorUpdateRef = useRef(Date.now()); // ⭐ 統一感測器更新時間
  const lastCurrentUpdateRef = useRef(Date.now());
  const lastRelayUpdateRef = useRef(Date.now());

  useEffect(() => {
    // 連接 MQTT
    mqttClient.current = mqtt.connect(config.mqttHost, {
      username: config.mqttUsername,
      password: config.mqttPassword,
      reconnectPeriod: 1000
    });

    mqttClient.current.on('connect', () => {
      console.log('✅ MQTT 連線成功');

      // 訂閱主題
      mqttClient.current.subscribe([
        'pump/sensors/pressure',
        'pump/sensors/current',
        'pump/sensors/flow', // ⭐ 流量感測器
        'pump/valves/status',
        'pump/system/status'
      ]);
    });

    mqttClient.current.on('message', (topic, message) => {
      try {
        const payload = JSON.parse(message.toString());

        if (topic === 'pump/sensors/pressure') {
          lastSensorUpdateRef.current = Date.now();
          setRealtimePressure(payload.value);

          // 如果是壓力測試且測試中,加入圖表數據
          if (testType === 'pressure' && testStatus === 'running' && startTimeRef.current) {
            const elapsedSec = (Date.now() - startTimeRef.current) / 1000;
            setChartData(prev => [...prev, {
              time: parseFloat(elapsedSec.toFixed(2)),
              pressure: payload.value,
              current: prev[prev.length - 1]?.current || 0, // ⭐ 保留電流數據
              timestamp: Date.now()
            }]);
          }
        }

        if (topic === 'pump/sensors/current') {
          lastCurrentUpdateRef.current = Date.now();
          setRealtimeCurrent(payload.value);

          // 更新圖表中的電流數據
          if (testStatus === 'running' && startTimeRef.current) {
            setChartData(prev => {
              if (prev.length === 0) return prev;
              const lastIndex = prev.length - 1;
              const updated = [...prev];
              updated[lastIndex] = { ...updated[lastIndex], current: payload.value };
              return updated;
            });
          }
        }

        if (topic === 'pump/sensors/flow') {
          lastSensorUpdateRef.current = Date.now(); // ⭐ 更新感測器時間
          setRealtimeFlow(payload.value);

          // 如果是流量測試且測試中,加入圖表數據 ⭐ 新增
          if (testType === 'flow' && testStatus === 'running' && startTimeRef.current) {
            const elapsedSec = (Date.now() - startTimeRef.current) / 1000;
            setChartData(prev => [...prev, {
              time: parseFloat(elapsedSec.toFixed(2)),
              flow: payload.value,
              current: prev[prev.length - 1]?.current || 0,
              timestamp: Date.now()
            }]);
          }
        }

        if (topic === 'pump/valves/status') {
          setValveStatus(payload);
        }

        if (topic.startsWith('pump/relay/')) {
          lastRelayUpdateRef.current = Date.now();
        }

      } catch (error) {
        console.error('❌ MQTT 訊息解析錯誤:', error);
      }
    });

    mqttClient.current.on('error', (err) => {
      console.error('❌ MQTT 連線錯誤:', err);
    });

    // 狀態監測定時器
    const statusCheckInterval = setInterval(() => {
      const now = Date.now();

      // ⭐ 檢查壓力/流量感測器 (統一)
      if (now - lastSensorUpdateRef.current > 1500) {
        setSensorStatus('錯誤');
      } else {
        setSensorStatus('正常');
      }

      // 檢查電流感測器
      if (now - lastCurrentUpdateRef.current > 1500) {
        setCurrentSensorStatus('錯誤');
      } else {
        setCurrentSensorStatus('正常');
      }

      // 檢查繼電器
      if (now - lastRelayUpdateRef.current > 1500) {
        setRelayStatus('錯誤');
      } else {
        setRelayStatus('正常');
      }
    }, 1000);

    // 清理
    return () => {
      clearInterval(statusCheckInterval);
      if (mqttClient.current) {
        mqttClient.current.end();
      }
    };
  }, [testStatus, testType]); // ⭐ 添加 testType 依賴

  // 發送 MQTT 指令
  const publishCommand = (topic, message) => {
    if (mqttClient.current && mqttClient.current.connected) {
      mqttClient.current.publish(topic, JSON.stringify(message));
      console.log(`📤 發送 MQTT: ${topic}`, message);
    }
  };

  return { publishCommand };
}
```

---

## 9. 實作計劃

### 9.1 Phase 1: 基礎架構 (Week 1-2)

**目標**: 建立專案骨架與基礎元件

#### Week 1: 專案設置
- [x] 複製 Air 專案結構
- [ ] 清理不需要的頁面 (Flow.js)
- [ ] 設置路由 (/, /setup, /data)
- [ ] 建立 Header 元件
- [ ] 建立 TestContext
- [ ] 整合 MQTT (useMQTT hook)

#### Week 2: 基礎元件
- [ ] StatusIndicator (狀態指示燈)
- [ ] ToggleSwitch (切換開關)
- [ ] RealtimeValueCard (數值顯示卡)
- [ ] Toast (通知)
- [ ] Button (統一按鈕樣式)

**交付物**:
- 可運行的專案骨架
- 基礎元件庫
- MQTT 連線正常

### 9.2 Phase 2: 主控台頁面 (Week 3-4)

#### Week 3: 主控台 Layout
- [ ] 頂部狀態列（含狀態指示燈、測試模式/類型選擇）
- [ ] 測試類型切換（壓力測試 / 流量測試）
- [ ] 電磁閥狀態顯示（A/B/C/D）
- [ ] 手動模式安全檢查邏輯
- [ ] 控制按鈕區
- [ ] 縱向 Layout 結構（參考數據 → 圖表 → 當前數據）

#### Week 4: 圖表與即時數值
- [ ] 參考數據表格區（頂部，可選擇比對數據）
- [ ] Recharts 壓力/流量曲線圖（動態切換）
- [ ] 流量單位區分（氣體 L/min / 液體 m³/h）
- [ ] 圖表右下角即時數值顯示
- [ ] 當前測試數據表格（底部）
- [ ] 圖表儲存功能（html2canvas + CSV 匯出）
- [ ] 參考數據即時比對與差異顯示

**交付物**:
- 完整的主控台頁面（縱向佈局）
- 壓力/流量測試雙模式支援
- 即時數據顯示與參考比對
- 圖表繪製與 CSV 匯出

### 9.3 Phase 3: 測試設定頁面 (Week 5)

- [ ] 單頁表單設計
- [ ] 表單驗證邏輯
- [ ] Cookie 持久化 (js-cookie)
- [ ] 與主控台整合

**交付物**:
- 完整的測試設定頁面
- 設定數據傳遞至主控台

### 9.4 Phase 4: 數據管理頁面 (Week 6-7)

#### Week 6: 歷史記錄 & 參考資料庫
- [ ] Tab 切換
- [ ] 搜尋與篩選
- [ ] 數據表格 (可排序、分頁)
- [ ] CSV 匯出

#### Week 7: 數據比對
- [ ] 選擇比對數據
- [ ] 差異分析
- [ ] 曲線對比圖
- [ ] 比對報告匯出

**交付物**:
- 完整的數據管理頁面
- 數據比對功能

### 9.5 Phase 5: 整合測試 (Week 8)

- [ ] MQTT 與 Python 後端整合測試
- [ ] 真實硬體連線測試
- [ ] 效能優化
- [ ] Bug 修復
- [ ] 使用者測試與回饋

**交付物**:
- 可部署的完整系統
- 測試報告

---

## 10. 總結

### 10.1 關鍵決策

1. **技術棧**: 完全沿用 Air 專案 (Tailwind + Recharts)
2. **設計風格**: 淺色背景 + 藍灰色系,工業化設計
3. **狀態管理**: Context API (簡單足夠)
4. **無需登入**: 專注於核心測試功能
5. **簡化頁面**: 3 個主要頁面 (主控台/設定/數據)

### 10.2 設計亮點

- ✅ 沿用團隊熟悉的技術棧,降低學習曲線
- ✅ 工業級 UI: 大字體、高對比、狀態指示燈
- ✅ **雙測試類型支援**: 壓力測試 + 流量測試（氣體/液體單位區分）
- ✅ **即時數據可視化**: Recharts 壓力/流量曲線（動態切換 Y 軸）
- ✅ **參考數據即時比對**: 測試中顯示參考值 vs 即時值差異分析
- ✅ **手動模式安全檢查**: 電磁閥組合驗證，防止錯誤操作
- ✅ **完整的數據管理**: 歷史記錄、比對、CSV 匯出（含圖表圖片）
- ✅ **可搜尋型號選單**: 支援 50+ 型號快速搜尋 + 手動輸入
- ✅ 安全性優先: 多重狀態檢查、禁用邏輯、錯誤提示

### 10.3 開發時程

**總計**: 8 週 (2 個月)

```
Week 1-2: 基礎架構與元件
Week 3-4: 主控台頁面
Week 5:   測試設定頁面
Week 6-7: 數據管理頁面
Week 8:   整合測試與部署
```

---

**文件版本**: 2.0
**建立日期**: 2025.11.13
**更新日期**: 2025.11.13
**負責人**: [待填寫]
**狀態**: 基於 Air 專案的設計方案

---

**附註**: 本文件完全基於現有 **AIR_Aries** 專案進行設計,可直接複用現有代碼與元件,大幅縮短開發時間。

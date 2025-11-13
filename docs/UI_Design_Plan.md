# 幫浦測試平台 - React 前端 UI 設計規劃
## Air and Water Pump Testing Platform - Frontend Design Plan

**專案**: 氣體/液體幫浦測試平台
**客戶**: Micron Technology
**開發商**: 岡泰技研有限公司
**文件版本**: 1.0
**更新日期**: 2025.11.13
**機密等級**: Confidential

---

## 目錄

1. [UI 架構總覽](#1-ui-架構總覽)
2. [頁面結構與導航](#2-頁面結構與導航)
3. [主要畫面設計](#3-主要畫面設計)
4. [使用者流程圖](#4-使用者流程圖)
5. [元件架構](#5-元件架構)
6. [技術棧與工具](#6-技術棧與工具)
7. [Layout 與響應式設計](#7-layout-與響應式設計)
8. [狀態管理策略](#8-狀態管理策略)
9. [實作優先順序](#9-實作優先順序)

---

## 1. UI 架構總覽

### 1.1 整體架構

```
幫浦測試平台 (Pump Testing Platform)
│
├── 主控台介面 (Main Dashboard)
│   ├── 頂部控制列 (Top Control Bar)
│   ├── 系統狀態面板 (System Status Panel)
│   ├── 測試數據區 (Test Data Area)
│   ├── 即時監控區 (Real-time Monitoring)
│   └── 壓力曲線圖表區 (Pressure Chart Area)
│
├── 測試設定介面 (Test Configuration)
│   ├── 基本設定表單 (Basic Settings Form)
│   ├── 電源選擇介面 (Power Selection)
│   ├── 進階參數設定 (Advanced Parameters)
│   └── 幫浦資料庫選擇 (Database Selection)
│
├── 數據管理介面 (Data Management)
│   ├── 歷史記錄查詢 (History Search)
│   ├── 數據比對功能 (Data Comparison)
│   ├── 參考資料庫管理 (Reference Database)
│   └── 匯出/備份功能 (Export/Backup)
│
├── 系統設定介面 (System Settings)
│   ├── 感測器校正 (Sensor Calibration)
│   ├── 系統參數調整 (System Parameters)
│   ├── 使用者權限管理 (User Management)
│   └── 系統診斷工具 (Diagnostics)
│
└── 警示/通知系統 (Alert & Notification)
    ├── 即時警示彈窗 (Alert Modals)
    ├── 系統通知列 (Notification Bar)
    └── 錯誤日誌查看 (Error Logs)
```

### 1.2 設計原則

1. **工業化設計風格**
   - 清晰明瞭的資訊階層
   - 高對比度配色方案
   - 大尺寸可觸控按鈕 (≥48px)
   - 即時狀態回饋

2. **操作效率優先**
   - 最多 3 層導航深度
   - 常用功能快捷鍵支援
   - 單手觸控操作友善
   - 5 分鐘完成測試設定

3. **安全性設計**
   - 危險操作二次確認
   - 視覺化安全警示
   - 操作鎖定機制
   - 即時系統狀態顯示

4. **數據可視化**
   - 即時曲線繪製
   - 關鍵數值大字體顯示
   - 歷史數據疊加對比
   - 異常值紅色標示

---

## 2. 頁面結構與導航

### 2.1 頁面層級架構

```
/                           → 主控台 (Main Dashboard) - 測試執行頁面
├── /setup                  → 測試設定頁面
├── /data                   → 數據管理
│   ├── /data/history       → 歷史記錄
│   ├── /data/reference     → 參考資料庫
│   └── /data/comparison    → 數據比對
├── /settings               → 系統設定
│   ├── /settings/sensor    → 感測器校正
│   ├── /settings/system    → 系統參數
│   └── /settings/users     → 使用者管理
└── /logs                   → 系統日誌
```

### 2.2 導航模式

**主導航 (Top Navigation Bar)**
```
┌─────────────────────────────────────────────────────────────┐
│ [LOGO] 岡泰幫浦測試平台                                       │
│                                                             │
│  [主控台] [測試設定] [數據管理] [系統設定] [日誌]            │
│                                                             │
│  系統時間: 2025-11-13 14:30:15    [操作員: XXX] [登出]     │
└─────────────────────────────────────────────────────────────┘
```

**快速操作工具列 (Quick Action Bar)**
- 位於畫面右側/底部
- 包含: 急停按鈕、暫停、停止、參數設定快捷鍵

---

## 3. 主要畫面設計

### 3.1 主控台介面 (Main Dashboard) - 最重要

#### Layout 配置 (1920x1080 全螢幕)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Top Navigation Bar (高度: 80px)                                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│ ┌──────────────────────────────────────────────────────────────────┐   │
│ │ 控制列 (Control Bar) - 高度: 120px                               │   │
│ │                                                                  │   │
│ │ ┌─測試模式選擇─────────┐  ┌─系統狀態─┐  ┌─控制按鈕──────┐   │   │
│ │ │ ○ 真空幫浦           │  │ 🟢 就緒  │  │ [啟動測試]    │   │   │
│ │ │ ○ 正壓幫浦           │  │ 急停: ✓  │  │ [暫停測試]    │   │   │
│ │ │ ○ 手動測試           │  │ 蓋: ✓    │  │ [停止測試]    │   │   │
│ │ └─────────────────────┘  └──────────┘  └───────────────┘   │   │
│ └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│ ┌───────────────────────────────────┬──────────────────────────────┐   │
│ │                                   │  即時數值顯示區              │   │
│ │   壓力曲線圖表區                  │  (Real-time Values)          │   │
│ │   (Pressure Chart Area)           │  ┌──────────────────────┐   │   │
│ │   高度: 500px                      │  │ 即時壓力             │   │   │
│ │                                   │  │ -85.5 kPa            │   │   │
│ │   [即時繪製壓力變化曲線]          │  │ (大字體 48px)        │   │   │
│ │                                   │  └──────────────────────┘   │   │
│ │   X軸: 時間 (秒/分)               │  ┌──────────────────────┐   │   │
│ │   Y軸: 壓力 (kPa / kg/cm²)        │  │ 即時電流             │   │   │
│ │                                   │  │ 6.8 A                │   │   │
│ │   支援: 放大/縮小/拖曳/導出       │  │ (大字體 48px)        │   │   │
│ │                                   │  └──────────────────────┘   │   │
│ │                                   │  ┌──────────────────────┐   │   │
│ │                                   │  │ 測試時間             │   │   │
│ │                                   │  │ 00:15:32             │   │   │
│ │                                   │  └──────────────────────┘   │   │
│ │                                   │  ┌──────────────────────┐   │   │
│ │                                   │  │ 幫浦狀態             │   │   │
│ │                                   │  │ 🟢 運轉中            │   │   │
│ │                                   │  └──────────────────────┘   │   │
│ └───────────────────────────────────┴──────────────────────────────┘   │
│                                                                          │
│ ┌──────────────────────────────────────────────────────────────────┐   │
│ │ 參考數據區 (Reference Data Table) - 高度: 150px                  │   │
│ │ ┌─ 比對資料庫 ────────────────────────────────┐                 │   │
│ │ │ 型號 │功能│運轉方式│電源│電力消耗│壓力值│恆壓電流│日期 │       │   │
│ │ │ DMM..│真空│自動    │AC..│1500W   │-95kPa│6.8A   │11/12│       │   │
│ │ └────────────────────────────────────────────┘ [刪除此筆資料]   │   │
│ └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│ ┌──────────────────────────────────────────────────────────────────┐   │
│ │ 當前測試數據區 (Current Test Data Table) - 高度: 150px          │   │
│ │ ┌─ 當前測試資料 ──────────────────────────────┐                 │   │
│ │ │ 型號 │功能│運轉方式│電源│電力消耗│即時壓力│即時電流│時間 │       │   │
│ │ │ DMM..│真空│自動    │AC..│1500W   │-85.5kPa│6.8A   │00:15│       │   │
│ │ └────────────────────────────────────────────┘ [儲存至比對資料庫] │   │
│ └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

#### 區域說明

**A. 控制列 (Control Bar)**
- **位置**: 頂部,導航列下方
- **高度**: 120px
- **內容**:
  - 測試模式選擇 (Radio Button Group): 真空幫浦 / 正壓幫浦 / 手動測試
  - 系統狀態指示燈: 就緒/測試中/警告/錯誤
  - 安全狀態: 急停開關狀態 / 測試蓋狀態
  - 控制按鈕: 啟動測試(綠) / 暫停測試(黃) / 停止測試(紅)
  - 快捷按鈕: [參數設定] [數據查詢]

**B. 壓力曲線圖表區 (Pressure Chart Area)**
- **位置**: 左側主區域
- **尺寸**: 寬70% × 高500px
- **技術**: Recharts / Chart.js
- **功能**:
  - 即時繪製壓力變化曲線 (1Hz 更新頻率)
  - X軸: 時間軸 (自動調整 秒/分/時)
  - Y軸: 壓力值 (自動切換 kPa / kg/cm²)
  - 支援放大/縮小/拖曳
  - 壓力恆定區標示 (綠色陰影區)
  - 異常值標記 (紅點)
  - 導出為圖片功能
  - 可疊加歷史數據曲線對比

**C. 即時數值顯示區 (Real-time Values Panel)**
- **位置**: 右側
- **尺寸**: 寬30% × 高500px
- **內容**:
  ```
  ┌────────────────────┐
  │  即時壓力          │
  │  -85.5            │  ← 48px 字體, 粗體
  │  kPa              │  ← 24px 字體
  ├────────────────────┤
  │  即時電流          │
  │  6.8              │  ← 48px 字體, 粗體
  │  A                │  ← 24px 字體
  ├────────────────────┤
  │  測試時間          │
  │  00:15:32         │  ← 36px 字體
  ├────────────────────┤
  │  幫浦狀態          │
  │  🟢 運轉中         │  ← 24px, 動態icon
  ├────────────────────┤
  │  最大壓力          │
  │  -95.2 kPa        │
  ├────────────────────┤
  │  平均電流          │
  │  6.5 A            │
  ├────────────────────┤
  │  電磁閥狀態        │
  │  A:關 B:開         │
  │  C:關 D:開         │
  └────────────────────┘
  ```

**D. 參考數據區 (Reference Data Table)**
- **位置**: 中下方
- **高度**: 150px
- **功能**:
  - 顯示從"比對資料庫"載入的參考數據
  - 表格形式: 可排序、可搜尋
  - 欄位: 型號 | 功能 | 運轉方式 | 電源 | 電力消耗 | 壓力值 | 恆壓電流 | 日期
  - 操作: 載入幫浦資料 / 刪除當前顯示資料
  - 可與當前測試數據自動比對差異 (差異用顏色標示)

**E. 當前測試數據區 (Current Test Data Table)**
- **位置**: 底部
- **高度**: 150px
- **功能**:
  - 顯示當前正在執行的測試數據
  - 表格形式: 即時更新
  - 欄位: 型號 | 功能 | 運轉方式 | 電源 | 電力消耗 | 即時壓力 | 即時電流 | 測試時間
  - 操作: 儲存至比對資料庫 / 儲存至測試庫 / 匯出CSV
  - 測試完成後顯示 PASS/FAIL 判定

---

### 3.2 測試設定介面 (Test Configuration Page)

#### Layout 配置

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Top Navigation Bar                                                       │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│ ┌──────────────────────────────────────────────────────────────────┐   │
│ │ 頁面標題: 測試參數設定                    [返回主控台] [說明]   │   │
│ └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│ ┌────────────────────┬───────────────────────────────────────────┐     │
│ │                    │                                           │     │
│ │  設定流程導航      │   設定表單區                              │     │
│ │  (Step Indicator)  │   (Configuration Form)                    │     │
│ │                    │                                           │     │
│ │  1. ✓ 測試模式     │   ┌──────────────────────────────────┐  │     │
│ │  2. → 幫浦資訊     │   │ 步驟 2: 幫浦資訊                 │  │     │
│ │  3.   電源設定     │   │                                  │  │     │
│ │  4.   參數調整     │   │ 幫浦型號:                        │  │     │
│ │  5.   確認儲存     │   │ [___________] 或 [選擇型號▼]    │  │     │
│ │                    │   │                                  │  │     │
│ │                    │   │ 幫浦功能:                        │  │     │
│ │                    │   │ ○ 真空幫浦                       │  │     │
│ │                    │   │ ○ 正壓幫浦                       │  │     │
│ │                    │   │ ○ 液體幫浦                       │  │     │
│ │                    │   │                                  │  │     │
│ │                    │   │ 幫浦運轉方式:                    │  │     │
│ │                    │   │ ○ 連續運轉                       │  │     │
│ │                    │   │ ○ 間歇運轉                       │  │     │
│ │                    │   │                                  │  │     │
│ │                    │   └──────────────────────────────────┘  │     │
│ │                    │                                           │     │
│ │                    │   [< 上一步]  [下一步 >]  [取消]        │     │
│ │                    │                                           │     │
│ └────────────────────┴───────────────────────────────────────────┘     │
│                                                                          │
│ ┌──────────────────────────────────────────────────────────────────┐   │
│ │ 預覽區 (Preview Panel)                                           │   │
│ │ ┌────────────────────────────────────────────────────────────┐   │   │
│ │ │ 當前設定預覽:                                              │   │   │
│ │ │ • 測試模式: 真空幫浦自動測試                               │   │   │
│ │ │ • 幫浦型號: DMM9200                                        │   │   │
│ │ │ • 電源: AC 220V 三相                                       │   │   │
│ │ │ • 額定電力: 1500W                                          │   │   │
│ │ └────────────────────────────────────────────────────────────┘   │   │
│ └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

#### 設定流程步驟

**步驟 1: 測試模式選擇**
```
┌─────────────────────────────────────┐
│ 請選擇測試模式:                     │
│                                     │
│  ┌──────────┐  ┌──────────┐        │
│  │ 真空幫浦 │  │ 正壓幫浦 │        │
│  │ Vacuum   │  │ Positive │        │
│  │   [圖示] │  │   [圖示] │        │
│  └──────────┘  └──────────┘        │
│                                     │
│  ┌──────────┐                       │
│  │ 手動測試 │                       │
│  │ Manual   │                       │
│  │   [圖示] │                       │
│  └──────────┘                       │
└─────────────────────────────────────┘
```

**步驟 2: 幫浦資訊**
- 幫浦型號 (下拉選單 + 手動輸入)
- 幫浦功能 (真空/正壓/液體)
- 幫浦運轉方式 (連續/間歇)

**步驟 3: 電源設定**
```
┌─────────────────────────────────────┐
│ 電源選擇:                           │
│                                     │
│ AC 電源:                            │
│ □ 110V 單相                         │
│ □ 220V 單相                         │
│ □ 220V 三相  ← 選中                 │
│                                     │
│ DC 電源:                            │
│ □ 12V                               │
│ □ 24V                               │
│ □ 其他: [____] V                    │
│                                     │
│ 額定電力消耗:                       │
│ [1500] W                            │
│                                     │
│ 最大電流限制:                       │
│ [10.0] A                            │
└─────────────────────────────────────┘
```

**步驟 4: 進階參數調整 (可選)**
```
┌─────────────────────────────────────┐
│ ☑ 修改壓力上下限                    │
│   正壓上限: [8.0] kg/cm²           │
│   負壓上限: [-100] kPa              │
│                                     │
│ ☑ 修改測試時間參數                  │
│   壓力恆定判斷時間: [5] 分鐘       │
│   測試超時時間: [60] 分鐘          │
│                                     │
│ □ 修改電磁閥控制邏輯                │
└─────────────────────────────────────┘
```

**步驟 5: 儲存目標與確認**
```
┌─────────────────────────────────────┐
│ 測試結果儲存至:                     │
│                                     │
│ ○ 參考數據庫 (供日後比對使用)      │
│ ○ 測試庫 (一般測試記錄)            │
│                                     │
│ ─────────────────────────────────   │
│                                     │
│ 設定摘要:                           │
│ • 測試模式: 真空幫浦自動測試        │
│ • 幫浦型號: DMM9200                 │
│ • 電源: AC 220V 三相                │
│ • 額定電力: 1500W                   │
│ • 壓力上限: -100 kPa                │
│ • 超時時間: 60 分鐘                 │
│                                     │
│ [儲存並開始測試]  [僅儲存設定]     │
└─────────────────────────────────────┘
```

---

### 3.3 數據管理介面 (Data Management Page)

#### Layout 配置

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Top Navigation Bar                                                       │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│ ┌──────────────────────────────────────────────────────────────────┐   │
│ │ 數據管理                                                         │   │
│ │                                                                  │   │
│ │ Tab: [歷史記錄] [參考資料庫] [數據比對] [匯出/備份]             │   │
│ └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│ ┌──────────────────────────────────────────────────────────────────┐   │
│ │ 搜尋與篩選區                                                     │   │
│ │                                                                  │   │
│ │ 幫浦型號: [搜尋框]  日期範圍: [起] ~ [迄]  測試結果: [全部▼]   │   │
│ │                                                                  │   │
│ │ [搜尋] [重置] [進階篩選]                                        │   │
│ └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│ ┌──────────────────────────────────────────────────────────────────┐   │
│ │ 數據表格區 (可排序、分頁)                                        │   │
│ │ ┌────┬──────┬──────┬──────┬──────┬──────┬──────┬────────┐      │   │
│ │ │ □  │日期  │型號  │模式  │電源  │壓力  │電流  │結果    │      │   │
│ │ ├────┼──────┼──────┼──────┼──────┼──────┼──────┼────────┤      │   │
│ │ │ □  │11/12 │DMM.. │真空  │AC220 │-95.5 │6.8A  │PASS ✓  │      │   │
│ │ │ □  │11/11 │SSU.. │正壓  │AC110 │7.2   │15.2A │PASS ✓  │      │   │
│ │ │ □  │11/10 │IXM.. │真空  │DC24  │-88.3 │2.1A  │FAIL ✗  │      │   │
│ │ │... │...   │...   │...   │...   │...   │...   │...     │      │   │
│ │ └────┴──────┴──────┴──────┴──────┴──────┴──────┴────────┘      │   │
│ │                                                                  │   │
│ │ 顯示 1-20 / 共 156 筆   [< 上一頁] [1] [2] [3] ... [下一頁 >]  │   │
│ └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│ ┌──────────────────────────────────────────────────────────────────┐   │
│ │ 批次操作區                                                       │   │
│ │                                                                  │   │
│ │ 已選取 3 筆資料                                                  │   │
│ │                                                                  │   │
│ │ [匯出為CSV] [批次刪除] [加入比對] [生成報表]                    │   │
│ └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

#### 數據比對功能

```
┌──────────────────────────────────────────────────────────────┐
│ 數據比對                                                     │
│                                                              │
│ 參考數據 (Reference):                                        │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ 型號: DMM9200  日期: 2025-11-01  壓力: -95.5 kPa     │   │
│ │ 電源: AC220V-3P  電流: 6.8A  結果: PASS              │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                              │
│ 當前數據 (Current):                                          │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ 型號: DMM9200  日期: 2025-11-12  壓力: -93.2 kPa     │   │
│ │ 電源: AC220V-3P  電流: 7.1A  結果: PASS              │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                              │
│ 差異分析:                                                    │
│ • 壓力差異: -2.3 kPa (2.4%)  ⚠ 注意                       │
│ • 電流差異: +0.3 A (4.4%)    ⚠ 注意                       │
│                                                              │
│ [壓力曲線對比圖]                                             │
│ ┌────────────────────────────────────┐                      │
│ │  [參考曲線 vs 當前曲線疊加顯示]    │                      │
│ └────────────────────────────────────┘                      │
│                                                              │
│ [匯出比對報告] [儲存此比對]                                 │
└──────────────────────────────────────────────────────────────┘
```

---

### 3.4 系統警示與通知

#### 全螢幕警示 Modal (Critical Alerts)

**急停觸發**
```
┌────────────────────────────────────────┐
│                                        │
│         🛑 緊急停止                     │
│                                        │
│    急停開關已被觸發                    │
│    所有操作已鎖定                      │
│    系統已自動洩壓                      │
│                                        │
│    請確認安全後解除急停開關            │
│                                        │
│          [確認已解除]                  │
│                                        │
└────────────────────────────────────────┘
```

**過載警告**
```
┌────────────────────────────────────────┐
│                                        │
│         ⚠️ 電流超載                     │
│                                        │
│    檢測到電流超過設定值                │
│    當前電流: 12.5A                     │
│    設定上限: 10.0A                     │
│                                        │
│    系統已停止測試並洩壓                │
│                                        │
│    建議:                               │
│    1. 檢查幫浦電力規格                 │
│    2. 重新設定電流上限                 │
│    3. 檢查幫浦是否異常                 │
│                                        │
│    [查看詳細日誌] [返回主控台]        │
│                                        │
└────────────────────────────────────────┘
```

#### Toast 通知 (非關鍵性訊息)

```
右上角浮動通知:

┌──────────────────────────────┐
│ ✓ 測試設定已儲存             │
└──────────────────────────────┘

┌──────────────────────────────┐
│ ℹ 數據已匯出至 USB           │
└──────────────────────────────┘

┌──────────────────────────────┐
│ ⚠ 壓力感測器通訊延遲          │
└──────────────────────────────┘
```

---

## 4. 使用者流程圖

### 4.1 完整測試流程 (Happy Path)

```
┌─────────────┐
│ 開啟系統    │
│ 登入        │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 進入測試    │
│ 設定頁面    │◄──────┐
└──────┬──────┘       │
       │              │ 修改
       ▼              │ 設定
┌─────────────┐       │
│ 步驟1:      │       │
│ 選擇測試    │       │
│ 模式        │       │
└──────┬──────┘       │
       │              │
       ▼              │
┌─────────────┐       │
│ 步驟2:      │       │
│ 輸入幫浦    │       │
│ 資訊        │       │
└──────┬──────┘       │
       │              │
       ▼              │
┌─────────────┐       │
│ 步驟3:      │       │
│ 選擇電源    │       │
│ 設定        │       │
└──────┬──────┘       │
       │              │
       ▼              │
┌─────────────┐       │
│ 步驟4:      │       │
│ 進階參數    │       │
│ (可選)      │       │
└──────┬──────┘       │
       │              │
       ▼              │
┌─────────────┐       │
│ 步驟5:      │       │
│ 確認並儲存  │       │
└──────┬──────┘       │
       │              │
       ▼              │
┌─────────────┐       │
│ 返回主控台  │       │
│ (設定已載入)│       │
└──────┬──────┘       │
       │              │
       ▼              │
┌─────────────┐       │
│ 實體操作:   │       │
│ 安裝幫浦    │       │
│ 連接管路    │       │
│ 連接電源    │       │
└──────┬──────┘       │
       │              │
       ▼              │
┌─────────────┐       │
│ 關閉測試蓋  │       │
│ (聯鎖確認)  │       │
└──────┬──────┘       │
       │              │
       ▼              │
┌─────────────┐       │
│ 點擊        │       │
│ [啟動測試]  │       │
└──────┬──────┘       │
       │              │
       ▼              │
┌─────────────┐       │
│ 系統執行:   │       │
│ • 控制電磁閥│       │
│ • 供電幫浦  │       │
│ • 開始監測  │       │
└──────┬──────┘       │
       │              │
       ▼              │
┌─────────────┐       │
│ 即時監控:   │       │
│ • 壓力曲線  │       │
│ • 電流數值  │       │
│ • 測試時間  │       │
└──────┬──────┘       │
       │              │
       ▼              │
    ┌──────┐          │
    │壓力  │ Yes      │
    │恆定? ├──────┐   │
    └───┬──┘      │   │
        │ No      ▼   │
        │    ┌─────────┐
        │    │測試完成 │
        │    │自動洩壓 │
        │    └────┬────┘
        │         │
        ▼         │
    ┌──────┐     │
    │超時? │ Yes │
    └───┬──┘     │
        │ No     │
        │        │
        │◄───────┘
        │
        ▼
┌─────────────┐
│ 顯示測試    │
│ 結果摘要    │
│ PASS/FAIL   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 選擇:       │
│ □儲存至資料庫│───┐
│ □匯出CSV    │   │
│ □列印報表   │   │
└──────┬──────┘   │
       │          │
       │◄─────────┘
       │
       ▼
┌─────────────┐
│ 拆卸幫浦    │
│ 準備下一次  │
│ 測試        │
└─────────────┘
```

### 4.2 異常流程 (Error Handling)

```
測試執行中...
     │
     ▼
  ┌──────┐
  │檢測到│
  │異常? │
  └───┬──┘
      │
  ┌───┴───┬──────────┬──────────┬──────────┐
  │       │          │          │          │
  ▼       ▼          ▼          ▼          ▼
急停觸發  測試蓋開啟 電流超載   壓力異常   通訊中斷
  │       │          │          │          │
  ▼       ▼          ▼          ▼          ▼
立即停止  暫停測試   停止測試   警告顯示   錯誤提示
鎖定操作  可恢復     洩壓       記錄事件   重試連線
  │       │          │          │          │
  ▼       ▼          ▼          ▼          ▼
顯示警示 Modal → 記錄日誌 → 通知管理員
  │                              │
  ▼                              ▼
等待解除                    排除故障
  │                              │
  └──────────┬───────────────────┘
             │
             ▼
       確認安全後
       可選擇:
       • 繼續測試
       • 重新開始
       • 放棄測試
```

---

## 5. 元件架構

### 5.1 元件樹狀結構

```
App
├── Layout
│   ├── TopNavigation
│   │   ├── Logo
│   │   ├── NavMenu
│   │   ├── SystemTime
│   │   └── UserInfo
│   │
│   └── MainContent
│       └── [各頁面路由]
│
├── Pages
│   ├── MainDashboard (主控台)
│   │   ├── ControlBar
│   │   │   ├── TestModeSelector
│   │   │   ├── SystemStatusPanel
│   │   │   └── ControlButtons
│   │   │
│   │   ├── MainContentArea
│   │   │   ├── PressureChartArea
│   │   │   │   ├── PressureChart (Recharts)
│   │   │   │   └── ChartControls
│   │   │   │
│   │   │   └── RealtimeValuePanel
│   │   │       ├── PressureDisplay
│   │   │       ├── CurrentDisplay
│   │   │       ├── TimerDisplay
│   │   │       ├── PumpStatusIndicator
│   │   │       └── ValveStatusDisplay
│   │   │
│   │   ├── ReferenceDataTable
│   │   │   ├── DataTable
│   │   │   └── ActionButtons
│   │   │
│   │   └── CurrentTestDataTable
│   │       ├── DataTable
│   │       └── ActionButtons
│   │
│   ├── TestConfiguration (測試設定)
│   │   ├── StepIndicator
│   │   ├── ConfigurationForm
│   │   │   ├── Step1_TestMode
│   │   │   ├── Step2_PumpInfo
│   │   │   ├── Step3_PowerSettings
│   │   │   ├── Step4_AdvancedParams
│   │   │   └── Step5_Confirmation
│   │   │
│   │   └── PreviewPanel
│   │
│   ├── DataManagement (數據管理)
│   │   ├── TabNavigation
│   │   ├── SearchFilters
│   │   ├── DataTable
│   │   ├── PaginationControls
│   │   └── BatchOperations
│   │
│   └── SystemSettings (系統設定)
│       ├── SensorCalibration
│       ├── SystemParameters
│       └── UserManagement
│
├── Components (共用元件)
│   ├── Button
│   ├── Input
│   ├── Select
│   ├── RadioGroup
│   ├── Checkbox
│   ├── Table
│   ├── Modal
│   ├── Toast
│   ├── Loading
│   ├── StatusIndicator
│   └── Card
│
├── Features (功能模組)
│   ├── TestControl
│   │   ├── useTestControl.js (hook)
│   │   └── testControlSlice.js (Redux slice)
│   │
│   ├── DataDisplay
│   │   ├── useRealtimeData.js
│   │   └── dataDisplaySlice.js
│   │
│   ├── Configuration
│   │   ├── useConfiguration.js
│   │   └── configurationSlice.js
│   │
│   └── Alerts
│       ├── useAlerts.js
│       └── alertsSlice.js
│
└── Services
    ├── mqttService.js (MQTT 通訊)
    ├── apiService.js (可能的 REST API)
    ├── csvExportService.js (CSV 匯出)
    └── dataStorage.js (localStorage/IndexedDB)
```

### 5.2 核心元件設計

#### A. PressureChart 元件

```jsx
// 功能: 即時繪製壓力曲線
// 技術: Recharts

<PressureChart
  data={realtimeData}           // 即時數據陣列
  referenceData={refData}       // 參考數據 (可選)
  xAxisUnit="second|minute"     // X軸單位
  yAxisUnit="kPa|kg/cm²"        // Y軸單位
  showGrid={true}               // 顯示網格
  enableZoom={true}             // 啟用縮放
  enableExport={true}           // 啟用匯出
  onExport={handleExport}       // 匯出回調
  height={500}
  width="100%"
/>
```

#### B. ControlButtons 元件

```jsx
// 功能: 測試控制按鈕組

<ControlButtons
  testStatus="idle|running|paused|stopped"
  onStart={handleStart}
  onPause={handlePause}
  onStop={handleStop}
  disabled={!safetyChecks.passed}
  emergencyStopActive={emergencyStop}
/>
```

#### C. SystemStatusPanel 元件

```jsx
// 功能: 系統狀態指示

<SystemStatusPanel
  status={{
    overall: "ready|testing|warning|error",
    emergencyStop: boolean,
    coverClosed: boolean,
    communication: "ok|error",
    sensors: { pressure: boolean, current: boolean, flow: boolean }
  }}
/>
```

#### D. ConfigurationForm 元件

```jsx
// 功能: 多步驟設定表單

<ConfigurationForm
  currentStep={2}
  totalSteps={5}
  onNext={handleNext}
  onPrevious={handlePrevious}
  onCancel={handleCancel}
  onSubmit={handleSubmit}
  values={formValues}
  onChange={handleChange}
/>
```

---

## 6. 技術棧與工具

### 6.1 前端技術棧

#### 核心框架
```
React 19.0.0
├── React Router v6 (路由管理)
├── Redux Toolkit (狀態管理)
└── React Hooks (功能組合)
```

#### UI 框架與元件庫
```
選項 A: Material-UI (MUI) v5
  • 優點: 元件豐富, 文檔完善, 工業風主題支援
  • 適合: 快速開發, 需要大量表單元件

選項 B: Ant Design v5
  • 優點: 專業企業級 UI, 表格功能強大
  • 適合: 數據密集型應用

選項 C: Tailwind CSS + Headless UI
  • 優點: 高度客製化, 輕量級
  • 適合: 需要完全客製化設計

推薦: Ant Design (原因: 表格、表單功能強大, 適合工業應用)
```

#### 圖表庫
```
Recharts v2.15.1 (專案已使用)
├── LineChart (壓力曲線)
├── AreaChart (區域圖)
└── ComposedChart (複合圖表)

備選: Chart.js / Apache ECharts (更多圖表類型)
```

#### 通訊層
```
MQTT.js v5.10.3 (專案已使用)
  • WebSocket 連線: ws://localhost:9500
  • 訂閱主題: air/flow, usbrelay/state, heater/temp
  • 發布控制指令

Axios (未來可能的 REST API)
```

#### 數據處理
```
date-fns (日期時間處理)
lodash (工具函數)
```

#### 開發工具
```
Vite / Create React App (已使用 react-scripts)
ESLint + Prettier (程式碼規範)
```

### 6.2 狀態管理架構

#### Redux Store 結構

```javascript
{
  testControl: {
    mode: "vacuum" | "positive" | "manual",
    status: "idle" | "running" | "paused" | "stopped",
    startTime: timestamp,
    elapsedTime: seconds,
    valveStatus: { A: boolean, B: boolean, C: boolean, D: boolean },
    pumpStatus: "on" | "off"
  },

  realtimeData: {
    pressure: {
      current: number,
      max: number,
      min: number,
      average: number,
      history: [ { time: timestamp, value: number }, ... ]
    },
    current: {
      current: number,
      max: number,
      average: number,
      history: [ ... ]
    },
    flow: {
      current: number,
      history: [ ... ]
    }
  },

  configuration: {
    pumpModel: string,
    pumpFunction: "vacuum" | "positive" | "liquid",
    powerSource: {
      type: "AC" | "DC",
      voltage: number,
      phase: "single" | "three"
    },
    ratedPower: number,
    limits: {
      maxPressure: number,
      maxCurrent: number,
      timeout: number
    }
  },

  database: {
    referenceData: [ ... ],
    testHistory: [ ... ],
    selectedForComparison: [ ... ]
  },

  system: {
    emergencyStop: boolean,
    coverClosed: boolean,
    communication: {
      mqtt: "connected" | "disconnected",
      sensors: { pressure: boolean, current: boolean, flow: boolean }
    },
    alerts: [ { type, message, timestamp }, ... ]
  }
}
```

### 6.3 MQTT 整合

#### Topic 訂閱與發布

```javascript
// 訂閱主題 (Subscribe)
const topics = {
  pressure: "pump/sensors/pressure",      // 壓力數據
  current: "pump/sensors/current",        // 電流數據
  flow: "pump/sensors/flow",              // 流量數據
  valveStatus: "pump/valves/status",      // 電磁閥狀態
  systemStatus: "pump/system/status",     // 系統狀態
  emergencyStop: "pump/safety/emergency", // 急停
  coverStatus: "pump/safety/cover"        // 測試蓋
};

// 發布指令 (Publish)
const commands = {
  startTest: "pump/control/start",
  pauseTest: "pump/control/pause",
  stopTest: "pump/control/stop",
  setValve: "pump/valves/control",
  setPower: "pump/power/control"
};

// 數據格式範例
// pump/sensors/pressure → { value: -85.5, unit: "kPa", timestamp: 1699876543210 }
// pump/control/start → { mode: "vacuum", config: {...} }
```

---

## 7. Layout 與響應式設計

### 7.1 支援解析度

```
主要目標解析度:
• 1920x1080 (Full HD) - 主要工業觸控螢幕
• 1280x1024 (SXGA) - 備用螢幕

次要支援:
• 1366x768 (HD+) - 筆記型電腦
• 1024x768 (XGA) - 小尺寸螢幕 (最低支援)
```

### 7.2 響應式斷點

```css
/* Tailwind / MUI 斷點 */
xs: 0px      // 手機 (不支援)
sm: 600px    // 小平板 (不支援)
md: 900px    // 平板 (有限支援)
lg: 1200px   // 桌面 (完整支援)
xl: 1536px   // 大桌面 (最佳體驗)

/* 建議: 最低 1024px, 推薦 1920px */
```

### 7.3 字體與間距

```css
/* 字體大小 */
--font-xs: 12px;    // 次要資訊
--font-sm: 14px;    // 一般文字
--font-base: 16px;  // 預設大小
--font-lg: 18px;    // 標題
--font-xl: 24px;    // 小標題
--font-2xl: 36px;   // 即時數值
--font-3xl: 48px;   // 大型即時數值

/* 按鈕尺寸 */
--button-sm: 36px;  // 小按鈕
--button-md: 48px;  // 標準按鈕
--button-lg: 64px;  // 大按鈕 (觸控)

/* 間距 */
--space-xs: 4px;
--space-sm: 8px;
--space-md: 16px;
--space-lg: 24px;
--space-xl: 32px;
```

### 7.4 配色方案

```css
/* 工業風配色 */

/* 主要色彩 */
--primary: #1976d2;      // 藍色 (主要操作)
--success: #2e7d32;      // 綠色 (啟動、正常)
--warning: #ed6c02;      // 橙色 (警告、暫停)
--error: #d32f2f;        // 紅色 (停止、錯誤)
--info: #0288d1;         // 淺藍 (資訊)

/* 狀態色彩 */
--status-ready: #4caf50;    // 就緒 (綠)
--status-running: #2196f3;  // 運行中 (藍)
--status-paused: #ff9800;   // 暫停 (橙)
--status-error: #f44336;    // 錯誤 (紅)

/* 背景色彩 */
--bg-primary: #121212;      // 深色背景 (可選深色模式)
--bg-secondary: #1e1e1e;
--bg-paper: #ffffff;        // 卡片背景

/* 文字色彩 */
--text-primary: rgba(0, 0, 0, 0.87);
--text-secondary: rgba(0, 0, 0, 0.6);
--text-disabled: rgba(0, 0, 0, 0.38);

/* 邊框 */
--border-color: #e0e0e0;
```

---

## 8. 狀態管理策略

### 8.1 Local State vs Global State

#### Local State (useState, useReducer)
- 表單輸入值
- UI 互動狀態 (modal open/close, dropdown)
- 單一元件內部狀態

#### Global State (Redux)
- 測試控制狀態 (testControl)
- 即時數據 (realtimeData)
- 系統設定 (configuration)
- 數據庫資料 (database)
- 系統狀態 (system alerts, safety status)

### 8.2 資料流向

```
[MQTT Broker]
     ↓
[MQTT Service]
     ↓
dispatch(updateRealtimeData())
     ↓
[Redux Store]
     ↓
useSelector()
     ↓
[React Components]
     ↓
[UI Update]
```

### 8.3 優化策略

#### A. 效能優化
```javascript
// 1. 使用 React.memo 避免不必要的重繪
const PressureChart = React.memo(({ data }) => {
  // ...
});

// 2. 使用 useMemo 快取計算結果
const averagePressure = useMemo(() => {
  return calculateAverage(pressureHistory);
}, [pressureHistory]);

// 3. 使用 useCallback 快取回調函數
const handleStart = useCallback(() => {
  // ...
}, [dependencies]);

// 4. 虛擬滾動 (大量數據表格)
import { FixedSizeList } from 'react-window';
```

#### B. 數據更新策略
```javascript
// 即時數據緩衝 (避免頻繁更新 Redux)
const BUFFER_INTERVAL = 100; // ms
const HISTORY_LIMIT = 3600;  // 保留 1 小時數據 (1Hz)

// 使用 throttle/debounce
import { throttle } from 'lodash';
const throttledUpdate = throttle(updateChart, 100);
```

---

## 9. 實作優先順序

### Phase 1: 核心功能 MVP (2-3 週)

#### Week 1: 基礎架構
- [x] 專案初始化 (React + Router + Redux)
- [ ] 基礎 Layout (TopNav, MainContent)
- [ ] MQTT 服務整合
- [ ] Redux Store 基礎結構

#### Week 2: 主控台頁面
- [ ] 控制列 (Control Bar)
- [ ] 壓力曲線圖 (基本版 Recharts)
- [ ] 即時數值顯示面板
- [ ] 控制按鈕 (啟動/暫停/停止)
- [ ] 基本測試流程邏輯

#### Week 3: 測試設定頁面
- [ ] 多步驟表單框架
- [ ] 基本設定表單 (步驟 1-3)
- [ ] 設定資料與主控台整合

### Phase 2: 完整功能 (3-4 週)

#### Week 4: 數據管理
- [ ] 歷史記錄查詢介面
- [ ] 數據表格 (可排序、分頁)
- [ ] CSV 匯出功能
- [ ] LocalStorage / IndexedDB 資料儲存

#### Week 5: 進階功能
- [ ] 進階參數設定 (步驟 4)
- [ ] 數據比對功能
- [ ] 壓力曲線疊加對比
- [ ] 參考資料庫管理

#### Week 6: 安全與警示
- [ ] 急停警示 Modal
- [ ] 過載/異常警示系統
- [ ] Toast 通知系統
- [ ] 錯誤處理與日誌

#### Week 7: 系統設定
- [ ] 感測器校正介面
- [ ] 系統參數調整
- [ ] 使用者管理 (基礎)

### Phase 3: 優化與測試 (2-3 週)

#### Week 8-9: UI/UX 優化
- [ ] 響應式調整
- [ ] 動畫與過場效果
- [ ] 觸控操作優化
- [ ] 無障礙功能 (Accessibility)

#### Week 10: 整合測試
- [ ] 與 Python 後端整合測試
- [ ] 真實硬體連線測試
- [ ] 效能測試與優化
- [ ] 使用者測試與回饋

---

## 10. 開發指引

### 10.1 資料夾結構

```
air/quasar_dev/
├── src/
│   ├── app/
│   │   ├── App.js
│   │   ├── store.js (Redux store)
│   │   └── routes.js
│   │
│   ├── pages/
│   │   ├── MainDashboard/
│   │   │   ├── index.js
│   │   │   ├── ControlBar.js
│   │   │   ├── PressureChartArea.js
│   │   │   ├── RealtimeValuePanel.js
│   │   │   └── DataTables.js
│   │   │
│   │   ├── TestConfiguration/
│   │   │   ├── index.js
│   │   │   ├── StepIndicator.js
│   │   │   └── ConfigurationForm.js
│   │   │
│   │   ├── DataManagement/
│   │   └── SystemSettings/
│   │
│   ├── components/
│   │   ├── common/
│   │   │   ├── Button.js
│   │   │   ├── Input.js
│   │   │   └── ...
│   │   │
│   │   └── charts/
│   │       ├── PressureChart.js
│   │       └── ...
│   │
│   ├── features/
│   │   ├── testControl/
│   │   │   ├── testControlSlice.js
│   │   │   └── useTestControl.js
│   │   │
│   │   ├── realtimeData/
│   │   ├── configuration/
│   │   └── alerts/
│   │
│   ├── services/
│   │   ├── mqttService.js
│   │   ├── csvExportService.js
│   │   └── dataStorageService.js
│   │
│   ├── utils/
│   │   ├── dateHelpers.js
│   │   ├── dataProcessing.js
│   │   └── constants.js
│   │
│   └── styles/
│       ├── theme.js
│       ├── globalStyles.css
│       └── variables.css
│
├── public/
└── package.json
```

### 10.2 命名規範

```javascript
// 元件: PascalCase
PressureChart.js
ControlBar.js

// Hooks: camelCase + use 前綴
useTestControl.js
useRealtimeData.js

// Redux Slices: camelCase + Slice 後綴
testControlSlice.js
realtimeDataSlice.js

// 常數: UPPER_SNAKE_CASE
const MAX_PRESSURE = 8.0;
const MQTT_HOST = "ws://localhost:9500";

// 函數: camelCase
handleStartTest()
calculateAverage()
```

### 10.3 程式碼範例

#### Redux Slice 範例

```javascript
// features/testControl/testControlSlice.js
import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  mode: null,
  status: 'idle',
  startTime: null,
  elapsedTime: 0,
  valveStatus: { A: false, B: false, C: false, D: false },
  pumpStatus: 'off'
};

const testControlSlice = createSlice({
  name: 'testControl',
  initialState,
  reducers: {
    setMode: (state, action) => {
      state.mode = action.payload;
    },
    startTest: (state) => {
      state.status = 'running';
      state.startTime = Date.now();
    },
    pauseTest: (state) => {
      state.status = 'paused';
    },
    stopTest: (state) => {
      state.status = 'stopped';
      state.elapsedTime = 0;
    },
    updateValveStatus: (state, action) => {
      state.valveStatus = action.payload;
    },
    setPumpStatus: (state, action) => {
      state.pumpStatus = action.payload;
    }
  }
});

export const { setMode, startTest, pauseTest, stopTest, updateValveStatus, setPumpStatus } = testControlSlice.actions;
export default testControlSlice.reducer;
```

#### Custom Hook 範例

```javascript
// features/testControl/useTestControl.js
import { useDispatch, useSelector } from 'react-redux';
import { startTest, pauseTest, stopTest } from './testControlSlice';
import { mqttPublish } from '../../services/mqttService';

export const useTestControl = () => {
  const dispatch = useDispatch();
  const testControl = useSelector(state => state.testControl);
  const safetyStatus = useSelector(state => state.system);

  const handleStartTest = () => {
    // 安全檢查
    if (!safetyStatus.coverClosed) {
      alert('請關閉測試蓋');
      return;
    }
    if (safetyStatus.emergencyStop) {
      alert('急停開關已觸發');
      return;
    }

    // 發送 MQTT 指令
    mqttPublish('pump/control/start', {
      mode: testControl.mode,
      config: { /* ... */ }
    });

    // 更新 Redux 狀態
    dispatch(startTest());
  };

  const handlePauseTest = () => {
    mqttPublish('pump/control/pause', {});
    dispatch(pauseTest());
  };

  const handleStopTest = () => {
    mqttPublish('pump/control/stop', {});
    dispatch(stopTest());
  };

  return {
    testControl,
    handleStartTest,
    handlePauseTest,
    handleStopTest
  };
};
```

#### MQTT Service 範例

```javascript
// services/mqttService.js
import mqtt from 'mqtt';
import store from '../app/store';
import { updateRealtimeData } from '../features/realtimeData/realtimeDataSlice';

let client = null;

export const connectMQTT = (host, username, password) => {
  client = mqtt.connect(host, {
    username,
    password,
    reconnectPeriod: 1000
  });

  client.on('connect', () => {
    console.log('MQTT 連線成功');

    // 訂閱主題
    client.subscribe('pump/sensors/pressure');
    client.subscribe('pump/sensors/current');
    client.subscribe('pump/system/status');
  });

  client.on('message', (topic, message) => {
    const data = JSON.parse(message.toString());

    switch(topic) {
      case 'pump/sensors/pressure':
        store.dispatch(updateRealtimeData({
          type: 'pressure',
          value: data.value,
          timestamp: data.timestamp
        }));
        break;

      case 'pump/sensors/current':
        store.dispatch(updateRealtimeData({
          type: 'current',
          value: data.value,
          timestamp: data.timestamp
        }));
        break;

      // ... 其他主題
    }
  });

  client.on('error', (error) => {
    console.error('MQTT 錯誤:', error);
  });
};

export const mqttPublish = (topic, message) => {
  if (client && client.connected) {
    client.publish(topic, JSON.stringify(message));
  }
};

export const disconnectMQTT = () => {
  if (client) {
    client.end();
  }
};
```

---

## 11. 總結

### 11.1 關鍵特色

1. **工業級 UI 設計**
   - 高對比度、大字體、清晰階層
   - 適合觸控螢幕操作
   - 即時數據可視化

2. **安全性優先**
   - 多重安全檢查
   - 視覺化警示系統
   - 操作鎖定機制

3. **數據驅動**
   - 即時監控與歷史數據
   - 數據比對與分析
   - 完整的數據管理功能

4. **模組化架構**
   - Redux 狀態管理
   - 可複用元件
   - 易於擴充與維護

### 11.2 下一步討論重點

1. **UI 細節確認**
   - 配色方案偏好 (淺色/深色模式)
   - 圖表樣式偏好
   - 按鈕與表單風格

2. **功能優先順序**
   - 哪些功能是 MVP 必須的?
   - 哪些功能可以延後實作?

3. **整合方式**
   - 與現有 Python 後端的整合方式
   - MQTT Topic 命名慣例
   - 數據格式標準

4. **測試環境**
   - 是否有測試用的硬體?
   - Mock 數據需求?

---

**文件版本**: 1.0
**建立日期**: 2025.11.13
**負責人**: [待填寫]
**狀態**: 初版待審核

---

**附註**: 本文件為前端 UI 設計規劃,僅涵蓋前端層面。後端 Python 服務與硬體控制邏輯不在本文件範圍內。

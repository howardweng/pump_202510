# 氣體 / 液體 Pump 測試平台
## For Micron Technology

**Date:** 2025.11.12
**Status:** Confidential

**Company:** 岡泰技研有限公司 (Gong-Tai Technology Co. LTD.)

---

## Request

- 測定 AIR / Vacum Pump 於上產線安裝前該 Pump 之規格數據
- 測定 Water Pump 於上產線安裝前該 Pump 之規格數據
- **新增測定 PUMP 於測試時之功率消耗**

---

## Request Air/Vacuum and Water Pump List

| Description | Detail | Pump Type |
|------------|--------|-----------|
| VACUUM PUMP, DMM9200, LRXV-110016-1 | Musubi機台真空幫浦 | Air/Vacuum |
| PUMP, VACUUM (DISCO GNDR MAIN) | 8761 Grind main vacuum pump | Air/Vacuum |
| WATER PUMP, WHEEL COOLANT | 8761 DTU Wheel coolant pump | Water |
| CHILLER UNIT, SPINDLE COOLANT | 8761 DTU Spindle coolant pump | Water |
| VACUUM PUMP, DFM2800 | DFM2800 Vacuum pump | Air/Vacuum |
| PUMP, EMEC METERING KPLUS1802, 110V | DSD636X 藥水機pump | Water |
| PUMP, EMEC METERING KPLUS1802, 220V | DSD636X 藥水機pump | Water |
| COATING PUMP | 幫浦 KOGANEI P/N:F-EPB40-1W | Water |
| MK02-C-M4-X | ATI WIND vacuum pump | Air/Vacuum |
| MK01-C-M4-X | ATI WIND vacuum pump | Air/Vacuum |
| MK01-C-M4-X-X | ATI WIND vacuum pump | Air/Vacuum |
| ASSY, DRY PUMP FLEXTRAK | WB plasma真空pump | Air/Vacuum |
| PUMP, SSU2050,15HP,(LEFT) | 水洗機高壓PUMP(左) | Water |
| PUMP, SSU2050,15HP,(RIGHT) | 水洗機高壓PUMP(右) | Water |
| PUMP, KASHIYAMA PUMP | 真空泵浦 (5HP) | Air/Vacuum |
| PUMP, WTR PUMP MTR WIRED AND EXT | 抽水泵浦 | Water |
| PUMP, NIKUNI PUMP | 真空泵浦 (3HP) | Air/Vacuum |
| PUMP, RETURN PUMP-(NORDSON) | 排水泵浦 | Water |
| PIAB VACUUM PUMP, PICLASSIC PIX3 | 真空產生器 | Air/Vacuum |
| PUMP,VACUUM PUMP-(NORDSON) | 真空泵浦 | Air/Vacuum |
| HIGH PRESSURE BLOWER, DG-800-16R 7.5HP | 高壓風車 | Air/Vacuum |
| MAIN AIR 4-VACUUM PUMP | | Air/Vacuum |
| WATER PUMP, CVS 20-8 (UL) 20HP | | Water |
| PUMP, MD-55RM-220EN | 無軸封泵浦MD-55RM-220EN | Water |
| PUMP, MD-15RM-220EN | 無軸封泵浦MD-15RM-220EN | Water |
| HIGH-PRESSURE WINDMILL, DG-600-26R 5HP | DG626高壓風車 | Air/Vacuum |
| HIGH-PRESSURE WINDMILL, DG-800-26R 10HP | DG826高壓風車 | Air/Vacuum |
| iXH610 MK1 LV SM44 | 乾式真空幫浦（Dry Vacuum Pump by Edwards Vacuum | Air/Vacuum |
| iXH1210H MK1 LV SM+44 | Dry Vacuum Pump | Air/Vacuum |
| BOOSTER PUMP, LEVIBOOST 140 PILLAR | UPW 加壓 Pump<br>壓力提升與控制系統, 核心組件構成: 無軸承磁浮幫浦（Bearingless Pump & 壓力感測器（Pressure Transducer） | Water |
| NeoDry36EU-024C | Dry Vacuum Pump | Air/Vacuum |
| RPV063-90T200-22-42-6 | VACUUM PUMP | Air/Vacuum |
| Pump Leybold D65BCS + WSU251 | Vacuum pump | Air/Vacuum |
| PCT pump HV-115-2 | TEL coater PCT 光阻噴塗pump | Other |
| COT pump CRD | TEL coater COT 光阻噴塗pump | Other |
| IPUMP,nXDS6i 100-127/200-240v 1ph 50/60Hz | Dry Vacuum Pump | Air/Vacuum |
| IPUMP,nXD106i 100-127/200-240v 1ph 50/60Hz | Dry Vacuum Pump | Air/Vacuum |
| VACUUM PUMP, ACP15G 110-230v 50/60HZ | Dry Vacuum Pump | Air/Vacuum |
| YAMADA DIAPHRAGM PUMP,NDP-15BPC | HELLER 抽甲酸 DIAPHRAGM PUMP | Other |
| VACUUM PUMP,NEODRY36EU-019C | Dry Vacuum Pump | Air/Vacuum |
| VACUUM PUMP,NEODRY15EU-031C | Dry Vacuum Pump | Air/Vacuum |
| DUCLEAN PUMP | DUCLEAN PUMP | Air/Vacuum |
| PUMP,CRS 4-2(UL),60HZ,265V-Y460V/220V verder | 高壓風車 | Air/Vacuum |
| VGS870.07-SSET-3-N | gear pump | Water |
| PUMP,CHS 12-10,1HP,60HZ,265V-Y460V | 高壓風車 | Air/Vacuum |
| DRY PUMP (1700L.MIN),SSH-150 | Dry Vacuum Pump | Air/Vacuum |
| BELLOWS PUMP, LPAS-021535-2 | coating pump | Other |
| IXL1000N | Dry Vacuum Pump | Air/Vacuum |
| Vacuum Pump For Chamber(1000L/min) | Dry Vacuum Pump | Air/Vacuum |
| IXM600 | Dry Vacuum Pump | Air/Vacuum |
| IXM1200 MK2 LV | Dry Vacuum Pump | Air/Vacuum |
| GX600N | Dry Vacuum Pump | Air/Vacuum |
| IH1000 | Dry Vacuum Pump | Air/Vacuum |
| IXL600N 200-460V 50/60Hz | Dry Vacuum Pump | Air/Vacuum |
| PUMP,VACUUM,DRY,BOC EPX180L (208V, 1/4 water pipe) | Dry Vacuum Pump | Air/Vacuum |

---

## 測試功能規劃：1. 幫浦電源選擇單元

### AC Power
- 2 phase / 3 Phase select (單相 /3 相選擇)

### DC power Supply
- (可選擇電壓式)

### 功能說明：

- 測試站設置測試幫浦用交流 (單相 / 三相) 與直流電源, 可依據待測幫浦選擇使用相對應之電源
- 交流電源與直流電源輸出均設置超載電流保護裝置
- 提供待測幫浦測試之電源, 設置電源電壓顯示提供操作人員辨識
- 交流電源可選擇電壓與單相 / 三相 (測試場地須提供交流單相 / 三相電源)
- 直流電源提供多段電壓, 可以依照待測幫浦電壓需求選擇使用 (基本提供 DC12 與 DC24V 可增加電壓段數)

---

## 測試功能規劃：2. 幫浦消耗電流量測

### AC Power
- 2 phase / 3 Phase select (單相 /3 相選擇)

### DC power Supply
- (可選擇電壓式)

### 功能說明：

- 測試站設置測試幫浦耗電流偵測功能, 提供耗電流數據
- **實際 Pump 耗電流數據可以比對原始 Pump 之耗電規格, 作為該 Pump 品質判斷**

---

## 液體 PUMP 測試系統

### 系統組成：

```
PC ↔ PC to RS485 ↔ 電流消耗感測器 APD-03 ↔ 水壓 or 流量感測器 ← 待測 Pump

AC Power (2 phase / 3 Phase select 單相/3相選擇)
DC power Supply (可選擇電壓式)
```

---

## 氣體 PUMP 測試系統

### 系統組成：

```
PC ↔ PC to RS485 ↔ 電流消耗感測器 APD-03 ↔ 空壓 or 流量感測器 ← 待測 Pump

AC Power (2 phase / 3 Phase select 單相/3相選擇)
DC power Supply (可選擇電壓式)
```

---

## 初步規劃 PUMP 測試系統流程

1. 開啟測試平台電源與筆電
2. PUMP 參數輸入
3. 幫浦置於測試平台
4. Pump 管路安裝
5. 幫浦電源接入
6. 確認管線與電源無誤
7. 按下電腦啟動測試按鍵
8. 系統測試完成確認測試數據
9. 確認水壓與空壓是否已洩壓
10. 拆卸幫浦電源與管路
11. 測試完成

---

## 氣體 PUMP 測試管路配置

### 真空 PUMP 測試管路配置

```
待測 PUMP
├── 電力輸入端
│   ├── 供電連接
│   └── 馬達驅動器 (依照馬達型式選擇供電控制或是使用馬達驅動器)
│
├── 幫浦輸入端
│   ├── 0.5L 氣體儲氣筒 A
│   │   └── 負壓壓力計
│   └── 電磁閥 A
│       └── 末端空氣過濾器
│
└── 幫浦輸出端 (當幫浦有空氣輸入標準接頭時可以連接此測試單元做輸入輸出同時測試)
    └── 三通
        ├── 電磁閥 B → 氣體流量計 (幫浦輸出端) → 末端空氣過濾器
        ├── 電磁閥 C → 逆止閥 → 0.5L 氣體儲氣筒 B → 壓力計
        └── 洩壓電磁閥 D → 洩壓消音器
```

---

## 氣體 PUMP 測試電氣裝置配置

### PC 控制系統：

```
PC
├── USB to RS485 (上方)
│   ├── RS485 to Relay / DI
│   │   ├── 控制電磁閥 A/B/C/D
│   │   ├── 控制驅動器 RUN/Stop 控制
│   │   ├── 控制電力供電與不供電
│   │   ├── 測試蓋偵測開關
│   │   └── 緊急停止開關
│   │
│   └── DC 電力監測
│       AC 110V 單相電力監測
│       AC 220V 單相電力監測
│       AC 220V 三相電力監測
│
└── USB to RS485 (下方)
    ├── 讀取壓壓力計
    └── 讀取空氣流量計
```

---

## 選擇測試模式：真空幫浦與正壓幫浦測試系統相關動作

### 真空幫浦測試流程：

1. 真空幫浦測試
2. 電磁閥 A/C 關閉, B/D 開啟
3. 操作人員輸入待測幫浦參數
4. 操作人員啟動測試
5. 偵測測試蓋是否關閉, 正確關閉才准予啟動
6. 偵測壓力是否恆定
   - 如果壓力恆定持續 5 分鐘 (時間可以設定) 則自動停止測試
   - 如果壓力一直未恆定持續 5 分鐘則系統在 1 小時後 (時間可以設定) 自動停止測試

### 正壓壓力幫浦測試流程：

1. 正壓壓力幫浦測試
2. 電磁閥 B/D 關閉, A/C 開啟
3. 操作人員輸入待測幫浦參數
4. 操作人員啟動測試
5. 偵測測試蓋是否關閉, 正確關閉才准予啟動
6. 偵測壓力是否恆定
   - 如果壓力恆定持續 5 分鐘 (時間可以設定) 則自動停止測試
   - 如果壓力一直未恆定持續 5 分鐘則系統在 1 小時後 (時間可以設定) 自動停止測試

### 安全注意事項：

※ 急停開關於系統通電就開始偵測直到系統關電, 如有偵測到急停開關被啟動, 則系統會在螢幕顯示"緊急停止", 並將馬達停止, 儲氣筒洩壓, 並禁止操作, 直到急停開關被關閉

※ 測試蓋需蓋上才能啟動測試, 測試途中開蓋僅將馬達停止供電, 進入暫時停止狀態, 系統仍可操作

---

## 選擇測試模式：手動模式相關動作

### 手動模式流程：

1. 手動模式
2. 電磁閥 A/B/C/D 可以手動開啟或關閉
3. 測試流量時手動電磁閥 C/D 關閉, A/B 開啟
4. 操作人員輸入待測幫浦參數
5. 操作人員手動輸入測試時間 (最長為 12 小時)
6. 操作人員啟動測試
7. 偵測測試蓋是否關閉, 正確關閉才准予啟動
8. 測試時間達到手動輸入時間時自動停止測試
9. 儲氣筒洩壓

### 安全注意事項：

※ 急停開關於系統通電就開始偵測直到系統關電, 如有偵測到急停開關被啟動, 則系統會在螢幕顯示"緊急停止", 並將馬達停止, 儲氣筒洩壓, 並禁止操作, 直到急停開關被關閉

※ 測試蓋需蓋上才能啟動測試, 測試途中開蓋僅將馬達停止供電, 進入暫時停止狀態, 系統仍可操作

---

## 系統相關偵測動作

### 1. 急停開關
於系統通電就開始偵測直到系統關電, 如有偵測到急停開關被啟動, 則系統會在螢幕顯示"緊急停止", 並將馬達停止, 儲氣筒洩壓, 並禁止所有操作, 直到急停開關被關閉

### 2. 測試蓋開關
需蓋上才能啟動測試, 測試途中開蓋僅將馬達停止供電, 進入暫時停止狀態, 系統仍可操作

### 3. 過載停止
過載停止為以操作人員手動輸入之消耗電力值為依據, 在 Pump 測試過程中, 系統會讀取電力監測器的數值, 如果 Pump 運轉中之電力監測讀值超過操作人員輸入之數值時則顯示超載, 並停止測試並顯示"超載停止" (馬達停止, 除氣筒洩壓)

### 4. Pump 運轉電力與輸入電力不符
當運轉測試時發現有消耗電力的電力數值與操作人員輸入的電力不同時則停止測試運轉 (如電力輸入選擇為 AC110V 時, 於啟動測試為 AC220V 有電力消耗讀值時則停止測試, 並顯示"Pump 電力參數與配接電力不符"

### 5. 正壓壓力最高為 8kg/cm² (預設值)
當正壓壓力表讀取值達到此壓力時須暫時停止馬達運轉 (停止供電 Pump), 直到壓力值低於 8kg/cm² 時再啟動馬達運轉 (可以手動修改此上限值, 須注意 8kg/cm² 為系統最高上限值)

### 6. 負壓 (真空) 壓力最高為 100kPa
當負壓壓力表讀取值達到 100kPa 時須暫時停止馬達運轉 (停止供電 Pump)

---

## PUMP 測試前參數設定

### 設定流程：

1. 選擇 PUMP 測試模式
2. 輸入 PUMP 型號
3. 選擇供電電源 (AC or DC)
4. PUMP 電力消耗數值輸入
5. 是否修改系統上下限壓力值
6. 是否修改系統相關測試時間
7. 測試結果選擇儲存為參考數據庫或是測試庫 (2 icon)
8. 儲存

---

## PC 操作介面 (概約樣式)

### 主介面功能：

#### 模式選擇按鈕：
- 真空幫浦
- 正壓幫浦
- 手動測試

#### 控制按鈕：
- 目前狀態指示
- 啟動測試
- 暫停測試
- 停止測試

#### 資料區 (上方)：
**比對資料庫**
- 幫浦型號
- 幫浦功能
- 幫浦運轉方式
- 測試電源
- 幫浦電力消耗
- 壓力測試植
- 恆壓時消耗電流
- 資料儲存日期

**刪除當前顯示資料**

#### 資料區 (下方)：
- 幫浦型號
- 幫浦功能
- 幫浦運轉方式
- 測試電源
- 幫浦電力消耗
- 即時壓力測試值
- 即時電力消耗 (A)
- **儲存至比對資料庫**

#### 壓力曲線區
顯示即時壓力變化曲線圖

### 操作說明：

- 按下真空幫浦測試模式可以再按下手動測試來設定需要測試的時間, 如 8 小時
- 如未按下手動測試時, 則測試會在當壓力持續 1 分鐘不再增加時則自動停止測試

---

## PC Interface (UI)

### 系統控制部分：

1. 選擇操作模式時系統將相關電磁閥開啟與關閉
2. 測試結束, 將自動將電磁閥 A/B 開啟, 以釋放儲氣筒之壓力
3. 測試啟動時將待測幫浦供電, 使其運轉
4. 待補充

---

## PC Interface (UI) - 操作部分

### 操作功能：

1. **水壓測試啟動鍵螢幕按鍵式操作 / 空壓測試啟動鍵螢幕按鍵操作**

2. **測試功能選擇：**
   - 空氣部分：空壓 or 氣體流量
   - 液體部分：液壓 or 液體流量

3. **幫浦電力消耗測試數據紀錄** (儲存為 CSV 檔)

4. **氣體流量 / 液體流量數據紀錄** (儲存為 CSV 檔)

### 測試流程：

- 按下水壓啟動測定鍵後由電腦端顯示即時水壓 / 流量, 以及電力消耗, 測試完成後並顯示最後測試值, 並記錄於 PC

- 按下空壓啟動測定鍵後由電腦端顯示即時空壓 / 流量, 以及電力消耗, 測試完成後並顯示最後測試值, 並記錄於 PC

- 操作結束後可用 USB 隨身碟存取 CSV 檔以及 FTP 位址

---

## 文件結束

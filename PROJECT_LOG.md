# Project: Bee_ModelBox_Maker
# Status: Active Development

## 🛠 當前進度 (2026-07-02) — v1.3.7
- [x] 修復圖片載入靜默失敗：抓圖失敗時不再吞掉錯誤，改為顯示明確原因
- [x] 修復原圖抓取常見的防盜連問題：改帶來源頁面的 Referer header
- [x] 新增 Pillow 解碼備援：Qt 內建解碼器對特定 WebP 變體解不出來時自動改用 Pillow
- [x] 新增 og:image 解析備援：處理 Instagram 等社群網站回傳 SEO 預覽頁（HTML）而非圖片本體的情況
- [x] 修復 Serper 搜尋結果解析度提示恆為 N/A：欄位名稱應為 `imageWidth`/`imageHeight` 而非 `width`/`height`
- [x] 搜尋改為真正套用大圖尺寸篩選：Serper 使用 `tbs=isz:l`，DuckDuckGo 使用 `size="Large"`（原本只是把 "large" 塞進關鍵字文字，未實際生效）
- [x] 修復右側預覽畫布開啟時未自動撐滿寬度：新增 `showEvent` 觸發初始縮放計算
- [x] 優化 Mac 觸控板縮放手感：改為線性縮放（等量位移 = 等量縮放變化，不受目前縮放比例影響）

## 🛠 當前進度 (2026-02-27)
- [x] 環境建立 (Python 3.14 + PyQt6)
- [x] 自定義字體掛載 (Iori, ChironHeiHK)
- [x] 基礎 UI 實作 (搜尋框、清單、畫布預覽)
- [x] 動態標籤渲染邏輯 (系列+型號)
- [x] UI 優化：將 API 欄位移至齒輪設定對話框 (明碼顯示)
- [x] 設定彈窗優化：增加寬度 (600px) 以完整顯示 API Key
- [ ] 圖片搜尋功能串接 (待驗證 API Key)
- [ ] 標籤導出/列印功能實作 (Downloads 導出測試)

## 📝 專案說明書
- 目錄：`/Users/killbee/Documents/Bee_ModelBox_Maker`
- 主要檔案：`main.py`
- 目的：生成標準化的鋼彈模型紙盒側邊標籤。

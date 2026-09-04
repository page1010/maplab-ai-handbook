# A4 照片轉檔 SOP v1.0（a4-photo-convert-sop）

依據：Owner 2026-09-04 msg 4751「轉檔照片召喚A4 讓他指路做出sop 做成skill」。
執行者：A4（照片管線角色）。腳本：scripts/a4_photo_convert.py。具名制：產出 manifest 標 executed_by=A4。
本 SOP 同時根治缺陷棘輪兩缺陷：素材索引雙重計數（缺陷1）、同名 webp 覆蓋（缺陷2／木地板審稿 R2）。

## 原則

1. **Drive 唯讀**：只讀 MAPLAB_ASSETS 原圖，任何輸出寫本機（handbook data/photo_convert/），不動 Drive。
2. **先去重再編號**：同案多資料夾（如 0621… 與 20260621…）以內容雜湊去重，對「去重後清單」重新編號——一個原檔只對應一個 webp 檔名。
3. **對應表是唯一真相**：manifest.csv 每列含 source_basename、內容雜湊、webp 檔名、尺寸；上傳與 alt 定案都以此表為準，禁止憑檔名猜。
4. **轉檔不需要視覺模型**：HEIC→jpeg 用 macOS 內建 sips，jpeg→webp 用系統 Python 的 PIL（系統 Python 才有 PIL）。ALT 描述另案（A4 視覺後端 gemma/ollama 已於 8/30 卸載，回歸前可走 hermes 免費鏈視覺）。
5. **轉檔≠放行**：webp 出來後仍要過視覺確認閘（人看圖定 alt、查他牌 logo 入鏡），才能上 WP。

## 流程

1. 輸入：案夾路徑（MAPLAB_ASSETS 相對路徑，可多個=同案重複夾）＋目標 slug 前綴（如 maplab-tainan-opening-tea）。
2. 掃描 HEIC/JPG/PNG → 內容雜湊去重（跨夾）。
3. 依原檔名排序重新編號 01..NN，產 manifest.csv（executed_by=A4）。
4. sips 轉 jpeg（暫存）→ PIL 轉 webp（長邊上限 1600、品質 82；featured 另出 1200 寬版本可後補）。
5. 輸出：data/photo_convert/<slug>/NN.webp ＋ manifest.csv；可重跑（已存在的跳過）。
6. 視覺確認閘：人（或視覺模型回歸後）逐張看縮圖 → 定 alt、標 needs_logo_crop 實況 → 回填文章圖表。
7. 上傳 WP（主視窗）：照 manifest 上傳，媒體庫檔名=表內 webp 檔名。

## 首發示範

木地板案 17 張（0621說事實木地板開幕 ＋ 20260621說事實木地板開幕 兩夾去重）→ 供 wp-case-woodfloor-opening-20260903 用圖。

## 已知限制

- 腳本首跑需核准（bot 無頭窗跑不了）→ window-bus 排主視窗執行；跑通後把本 skill 標 v1.0-verified。
- sips 對部分 HEIC 變體可能失敗 → 腳本逐檔容錯，失敗列進 manifest 的 error 欄，不中斷整批。
- Drive 串流模式下讀檔會觸發下載，整批前確認磁碟餘裕（外接冷資料規則見 external-drive 檔）。

## Changelog

- v1.0（2026-09-04）：初版，依 msg 4751 建制；含缺陷1/2 根治設計。

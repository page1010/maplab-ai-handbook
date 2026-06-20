# A8 地端動態運鏡整合技能書 (Local Motion Integration Skills)

> 負責角色：A8 影音內容產線
> 建立：2026-06-20 | 版本：v1.0

---

## 0. 這本技能書解決什麼

為了徹底擺脫對 Higgsfield 等付費雲端影片生成工具的依賴，同時提取其動態相機運鏡與視覺包裝的「精華」，本技能書規範如何在本地（Mac mini 本機環境）利用 `qwen2.5:14b` 本地模型進行分鏡運鏡規劃，並藉由地端 `ffmpeg` 與 `swift` 渲染器生成滑順的動態運鏡 Reels 影片。

---

## 1. 零成本門檻與數據安全 (Zero-Cost Gate)

*   **完全在地化**：本機運鏡與影片合成必須 100% 於地端執行。嚴禁引進任何需要付費 API Key、訂閱制、或雲端點數（credits）的外部服務。
*   **隱私與素材安全**：所有客戶照片與活動原始檔皆保留於本機地端。未經 Owner 與 A1 審核，嚴禁上傳至任何第三方雲端 AI 處理。

---

## 2. 地端動態運鏡 (Camera Motion Styles)

我們使用本機 `ffmpeg` 的 `zoompan` 濾鏡來模擬專業相機的動態軌跡。每個鏡頭片段預設為 2~3 秒，支援以下五種核心運鏡模式：

| 運鏡模式 (`motion`) | FFmpeg 實作原理 | 適用場景 |
| :--- | :--- | :--- |
| **`dolly_in`** | `z='1.0+0.15*on/N'`<br>自 1.0x 慢速放大至 1.15x，中心點錨定。 | 精緻鹹甜點近照、慕斯杯細節、特寫主菜。 |
| **`dolly_out`** | `z='1.15-0.15*on/N'`<br>自 1.15x 慢速縮小至 1.0x，中心點錨定。 | 餐桌整體展現、餐盤特寫拉遠。 |
| **`pan_right`** | `z=1.15`, `x` 從左平滑平移至右。<br>`x='(iw-iw/zoom)*(on/N)'` | 會議茶點長桌、多品項排列擺盤。 |
| **`pan_left`** | `z=1.15`, `x` 從右平滑平移至左。<br>`x='(iw-iw/zoom)*(1-on/N)'` | 飲料吧檯、茶會取餐動線寬景。 |
| **`static`** | `z=1.001`<br>近乎靜態的輕微穩定畫面。 | Outro CTA、開場 Intro 或是輔助場景。 |

*註：`N` 為該分鏡總影格數（例如 2.4 秒 @ 30fps，`N = 72`）。*

---

## 3. 字幕與浮水印靜態疊加 (Transparent Overlay)

為了避免文字、Watermark、CTA 線條跟著照片一起 panning/zooming 產生拉伸與晃動：
1.  **分離渲染**：首先利用 `a8_render_story_frame.swift` 並傳入 `"clear"` 作為背景引數，在透明畫布上單獨繪製該分鏡的字幕與浮水印，產出透明的 `frame.png`。
2.  **FFmpeg 合成**：將靜態圖片經由 `zoompan` 轉成的動態影片片段作為底層，再將透明字幕 PNG 做為頂層，使用 `overlay` 濾鏡完成像素級疊加。
3.  **色彩分級**：最後於疊加完成的影片流上套用 MAPLAB 專屬的 `maplab_ig_soft` 濾鏡，確保文字與畫面完美融合。

---

## 4. 地端 Storyboard 與運鏡規劃 (Ollama Pipeline)

1.  **模型規劃**：本地 Ollama 執行 `qwen2.5:14b`，依據 WordPress 案例素材規劃 `storyboard` JSON。
2.  **Motion Spec 沿用**：引導模型為每個分鏡分配 `"motion"`（例如 `dolly_in`、`pan_right`），並確保其不包含任何禁用詞。
3.  **執行命令**：
    ```bash
    python3 tools/ai_workbook/a8_local_model_video_pipeline.py \
      --manifest [MANIFEST_JSON] \
      --metadata [METADATA_JSON] \
      --motion-spec [MOTION_SPEC_MD] \
      --out-dir [OUTPUT_DIR] \
      --model qwen2.5:14b
    ```

---

## 5. 影片組裝與發布

1.  **地端 MP4 產出**：合成出的各分鏡影片片段將使用 ffmpeg `xfade=fade`（0.35s 轉場）拼接成完整的 9:16 短片。
2.  **音軌與發布**：本地產出的草稿影片為無聲。上傳至 YouTube Shorts / TikTok / Instagram 前，必須使用平台內建的授權音樂庫配樂，嚴禁在本地封裝未授權配樂。

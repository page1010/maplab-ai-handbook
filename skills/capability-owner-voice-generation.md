# Skill:Owner 聲音生成(語音克隆 TTS)

- 建立:2026-08-25|作者:A0/Fable5|狀態:**待建(本機無既有資產)**|Owner 指示:msg 3992
- 用途:用 Owner 的聲音生成語音——短影音旁白(A8 剪片線)、maplabkitchen 客服語音、導覽解說。

## 現況(2026-08-25 盤點)

- 三個 repo 都沒有現成的聲音克隆資產;tools/ai_workbook 的 a8_* 是配樂/混音工具,不是語音克隆。
- 要落地需要兩樣:①Owner 的聲音樣本(乾淨錄音 1-3 分鐘)②一個 TTS 供應商或本地模型。

## 方案(建好後由 Owner 選)

- 雲端:ElevenLabs(品質最好,免費層有限,克隆通常要付費層=Owner 的錢);MiniMax/fish-audio 類(中文佳,同樣要帳號)。
- 本地:開源方案(如 fish-speech / GPT-SoVITS 類)跑 Mac,零月費但要裝環境+品質需實測;不佔 Claude 額度,適合 hermes/免費算力線接手跑。

## 紅線(比其他 skill 嚴)

- Owner 聲音樣本與克隆模型 = **L0 等級資產**(等同生物特徵):只存本機 repo 外目錄,不上傳到任何免費促銷算力、不進 git、不給第三方 worker。
- 生成內容每支都要 Owner 聽過才對外(聲音冒用風險);對外發布物標註 AI 生成照平台規範。
- 供應商註冊/付費 = Owner 決定;貼 key 照 OpenRouter 兩畫面模式。

## 下一步

額度回來後(或派 Codex):先做本地開源方案評測(一段 Owner 樣本→三個方案各出同一段話→Owner 盲聽選),再決定要不要花錢上雲端。

# Curriculum Inventory — JOB-LOCAL-MODEL-EVOLUTION-20260719

| Curriculum | 路徑 | Eval cases | 訓練樣本 | 狀態 |
|---|---|---|---|---|
| Investment report/current-state | `local_model_evolution/curricula/investment-report-current-state/` | 24 | 0（第一輪禁止先建） | dataset_ready (eval only) |
| SEO ranking/keyword | `local_model_evolution/curricula/seo-ranking-keyword/` | 24 | 0 | dataset_ready (eval only) |

兩者皆為去識別化合成資料（synthetic，非真實 Investment OS 部位或真實 GSC 匯出），
理由與範圍見對應 `CURRICULUM.md` 的「Eval Cases」段落。P1（客服/報價/現金流）
本輪未建立，依原始 prompt 排序留到 P0 兩個 curriculum 有真實 baseline 之後。

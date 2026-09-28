OUTPUT: data/free-quota/outputs/review-verdict-typed-spec.md
CONTEXT: data/free-quota/reviews/40-image-prompt_20260927_001.review.md

設計「免費鏈審稿型別化判定」規格(Jev 決策層思路:小判斷不寫散文,回固定型別)。要求:
1. 判定只允許三個固定值:PASS / FAIL / NEEDS_HUMAN。
2. 理由碼表至少 8 碼,每碼一行說明與觸發條件,必含:事實新增、數字無來源、含客戶個資、格式不符、離題、品質不足、涉紅線詞、其他(OTHER 需附一句自由文字)。
3. 定義單行 JSON 輸出格式(欄位:verdict、reason_codes 陣列、note),給出格式的 JSON Schema 式欄位說明。
4. 用 CONTEXT 附的真實審稿檔示範:把那份散文式審稿意見改寫成 3 個符合本規格的示範判定(一個 PASS、一個 FAIL、一個 NEEDS_HUMAN,內容可假想但格式必須嚴格合規)。
5. 末段列「下放條件」:哪些判定可純程式做(關鍵字/正規表達式即可攔)、哪些留給免費模型、哪些必須 NEEDS_HUMAN 升級。

鐵律:不得出現真實客戶姓名、電話、地址、價格、金鑰;全文 900 字內。

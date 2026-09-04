# secrets/ — 本機金鑰存放處（整個資料夾不進 git）

規則：key 只放這裡，不貼聊天、不進 repo、不進 prompt/log。檔案放對名字我就讀得到。

| 檔名 | 放什麼 | 用途 |
|---|---|---|
| google_oauth_client.json | Google Cloud Console 下載的 OAuth client JSON（原檔改名放入） | YouTube API 自動上傳（youtube.upload scope） |
| gmail.env | 一行：GMAIL_APP_PASSWORD=你的16碼應用程式密碼 | 寄功課/報告到 pagewu1010@gmail.com |
| pinterest.env | 一行：PINTEREST_ACCESS_TOKEN=你的token | Pinterest 自動發 Pin |

放好後在 Telegram 回一句「key放好了」即可，我會自己驗證能不能用，驗證結果回報你。

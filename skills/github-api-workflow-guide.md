# GitHub API Workflow Guide
版本：v1.0 | 2026-03-17 | A4 Pipeline Agent

改編自 superpowers writing-plans + executing-plans + finishing-a-development-branch。
適配：無本機 git，全部透過 GitHub REST API。

---

## 標準流程（7 步）

### Step 1: 拿 main SHA
GET /repos/{owner}/{repo}/git/ref/heads/main → object.sha

### Step 2: 建 branch
POST /repos/{owner}/{repo}/git/refs
命名：work/{project}/{agent}/{task}

### Step 3: 寫檔案
PUT /repos/{owner}/{repo}/contents/{path}
- 新檔案不需要 sha
- 更新需帶 sha（先 GET 拿）
- content = btoa(unescape(encodeURIComponent(text)))
- 一個 session 最多 2-3 個檔案

### Step 4: 確認成功
response.content.name 有值 = 成功。不要重讀整檔確認。

### Step 5: 開 PR
POST /repos/{owner}/{repo}/pulls

### Step 6: Merge
PUT /repos/{owner}/{repo}/pulls/{n}/merge
merged === true = 成功

### Step 7: 更新 project_state.md
每次 merge 後必做。

---

## JS fetch 範本

```javascript
// GET
fetch(url, { headers: { Authorization: 'token ' + PAT } })
.then(function(r) { return r.json(); })
.then(function(d) { window._sha = d.sha; });

// PUT
var enc = btoa(unescape(encodeURIComponent(content)));
fetch(url, { method: 'PUT', headers: { Authorization: 'token ' + PAT }, body: JSON.stringify({ message, content: enc, sha, branch }) })
.then(function(r) { return r.json(); })
.then(function(d) { window._r = d.content ? d.content.name : d.message; });
```

---

## 踩坑紀錄

| 坑 | 解法 |
|-----|------|
| btoa 中文亂碼 | btoa(unescape(encodeURIComponent(text))) |
| window 變數消失 | navigate 換頁後清空 → 同一頁做完 |
| async/await 不能用 | 用 .then() + window 變數 |
| SHA 409 conflict | 重新 GET sha |
| template literal 出錯 | 用 var + 字串拼接 |

---

## NEVER

- NEVER commit .env / credentials / tokens
- NEVER push 到 main（永遠 branch + PR）
- NEVER 在 GitHub web UI 編輯 .py
- NEVER 印出整個 API response

| v1.0 | 2026-03-17 | 初始版本 | A4 |
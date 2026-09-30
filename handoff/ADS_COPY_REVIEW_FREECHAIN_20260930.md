# 廣告文案審查結果(免費線單一模型)

**這份不是 Owner 指名的 GPT 審查,而且不是交叉審查。** 兩件事都要講清楚:

1. OpenRouter 免費層的 OpenAI 模型(gpt-oss-120b / gpt-oss-20b)在 2026-09-30 實測
   回 HTTP 404,訊息是「This model is unavailable for free」,付費版才有,
   而付費路線 Owner 6122 已永久關閉。GPT 那一份另走 agent-bus 派工卡。
2. 原本要用兩顆不同家的模型交叉審。實跑結果只有一顆成功:
   - nvidia/nemotron-3-super-120b-a12b:free → HTTP 200,兩段都有回
   - google/gemma-4-31b-it:free → HTTP 429(免費額度已滿)
   - minimax/minimax-m3:free → HTTP 404(這個代號已經不在免費層)
   所以底下的意見全部出自同一顆模型,**沒有第二方交叉驗證**。
   單一模型的判斷會有系統性偏誤,採用前請當成「一個人的意見」而不是「共識」。

受審檔案:handoff/ADS_COPY_FULL_20260930.txt(26 則廣告,文案逐字)

---

## 第 1/2 段 —— 審查模型:nvidia/nemotron-3-super-120b-a12b:free

We need to examine each ad text (the "待審文案") and find problems per categories 1-7. Output only those with problems, each line: "## 廣告名稱" then bullet lines: "- 問題類別 N|原文:「...」|為什麼:...|建議改成:「...」"

We need to identify the ad name (as given in headings). The file includes multiple ad entries with titles like:

- 【Instagram post: #派對實拍場景 | 𝑾𝒆𝒅𝒅𝒊𝒏𝒈 𝑷𝒂𝒓𝒕𝒚 | 點心Bar...】 (this is first ad)
- 【Instagram 貼文：#外燴紀錄 | 中華賓士-愛心慈善捐贈活動｜ESG｜ ...】 (second)
- 【Instagram 貼文：#外燴紀錄 今年夏天，我們又來到麻豆區的邦尼托嬰中心，...】 (third)
- 【MAPLAB 01 P0週歲單圖】 (fourth)
- 【MAPLAB 02 P0週歲輪播4卡】 (fifth)
- 【MAPLAB 03 TA3企業HR茶會】 (sixth)
- 【MAPLAB 04 V1週歲甜點塔影片】 (seventh)
- 【MAPLAB 05 TA2戶外婚禮】 (eighth)
- 【MAPLAB 06 B4公關開幕輪播3卡】 (ninth)
- 【MAPLAB 07 C2入厝派對(備位)】 (tenth)
- 【MAPLAB 08 C3長輩壽宴(備位)】 (eleventh)
- 【MAPLAB 09 B5研討會茶點】 (twelfth)
- 【MAPLAB 10 建商案場活動】 (thirteenth)
- 【MAPLAB 11 TA2婚禮點心Bar實拍影片】 (fourteenth)
- 【MAPLAB 12 TA3企業活動實拍影片】 (fifteenth)
- 【嘉義新竹桃園A】 (sixteenth)
- 【新的品牌認知廣告】 (seventeenth) appears twice? Actually there are two entries: one with status ACTIVE(effective_status=CAMPAIGN_PAUSED) and another with same name but different campaign. We'll treat them as separate ads: first: "新的品牌認知廣告" (with material ID 1429312295633464) and second: also "新的品牌認知廣告" (material ID 742769768863781). They have different internal text. We'll differentiate perhaps by adding the material ID or something, but the instruction: "指名哪一則廣告". Likely we use the heading as name. Since duplicate, we might need to differentiate by adding something like (第一則) etc. But we can just refer to the heading and note it's ambiguous? Better to include the material ID in the name to differentiate. However format expects just "## 廣告名稱". Could use the heading plus the material ID in parentheses.

We'll go through each ad and check for problems.

We need to check categories:

1. 做不到的承諾: writing "多久內一定回覆", "保證", "一定" etc that brand cannot control.

2. 禁用語: specific banned words: 保證、超值、CP值爆高、趕快預約、名額有限、限時優惠、最頂、佛心、便宜又大碗.

3. 按鈕與文案打架: button is "了解更多" leading to webpage, but copy asks to comment or private message.

4. 營運條件外露: low consumption, minimum spend, minimum number of ppl, days advance booking etc should not be in external copy.

5. 文案與場景對不上: copy mentions week-old but scene is corporate, copy mentions 入厝 but scene is wedding.

6. 沒有主體的句子: sentence reads without knowing who is being spoken to or what action they should take.

7. 多版內文彼此重複: multiple versions within same ad just word swaps, no angle change.

We need to examine each ad's multiple versions (if any). For those with 0 versions, we cannot check #7 (multiple version repetition). For those with 4 versions, we check if they are just paraphrases with same angle.

Also need to check for banned words, promises, etc.

Let's go ad by ad.

Ad 1: Instagram post: #派對實拍場景 | 𝑾𝒆𝒅𝒅𝒊𝒏𝒈 𝑷𝒂𝒓𝒕𝒚 | 點心Bar...

It has 4 versions. Let's extract each version text:

Version 1:
#派對實拍場景

 | 𝑾𝒆𝒅𝒅𝒊𝒏𝒈 𝑷𝒂𝒓𝒕𝒚 | 點心Bar |

婚禮，是你們愛情的延伸💍
而點心Bar，是賓客感受儀式美學的起點。

以乾燥花、木質器皿與玻璃擺設，融合經典與自然。

不論是甜食控還是鹹食派，
都能在這裡找到屬於自己的小確幸😋

新人當日就開心與我們回饋點心Bar太搶手、賓客秒掃光！！

¥此場為輕食茶點形式/賓客約80-100人

-Catering service
@maplabkitchen 

——————————————

✅ 精緻外燴｜融合創意料理，讓賓客ㄧ試難忘
✅ 客製菜單｜根據活動需求量身打造，滿足不同味蕾
✅ 專業擺盤｜高顏值餐點，讓美味更有儀式感

➡️洽詢檔期
加入官方Line: @maplab
https://lin.ee/IP8nt4n

#周歲派對 #周歲派對佈置 #周歲派對餐點 #抓周派對 #台南慶生派對 #慶生派對場地 #生日派對佈置 #抓周派對外燴 #台南抓周場地 #抓周儀式 #收涎派對 #收涎派對佈置 #寶寶收涎儀式

Version 2:
婚禮派對的美好瞬間💍
點心Bar是賓客感受儀式美學的起點!

乾燥花、木質器皿與玻璃擺設,
融合經典與自然。

甜食控或鹹食派都能找到小確幸😋

新人當日就開心回饋:點心Bar太搶手!賓客秒掃光!!

輕食茶點形式/約80-100人 
✅ 精緻外燴|創意料理
✅ 客製菜單|滿足不同味蕾
✅ 專業擺盤|高顏值餐點

洽詢檔期:
加入官方Line: @maplab

Version 3:
婚禮點心Bar

新人的愛情故事,從這裡開始💍
乾燥花、木質器皿與玻璃擺設,
融合經典與自然。

甜食控或鹹食派,都能找到屬於自己的小確幸😋
賓客秒掃光!我們的輕食茶點太搶手!

✅ 精緻外燴,讓賓客一試難忘
✅ 客製菜單,滿足不同味蕾
✅ 專業擺盤,高顏值餐點,儀式感十足!

洽詢檔期:加入官方Line: @maplab 
https://lin.ee/IP8nt4n

Version 4:
Wedding Party

婚禮是愛情的延伸💍
點心Bar是賓客感受儀式美學的起點!

乾燥花、木質器皿與玻璃擺設,融合經典與自然。
甜食控或鹹食派,都能找到屬於自己的小確幸😋

新人當日就開心與我們回饋:點心Bar太搶手、賓客秒掃光!!

¥輕食茶點形式/約80-100人
✅ 精緻外燴|創意料理
✅ 客製菜單|根據活動需求量身打造
✅ 專業擺盤|高顏值餐點

➡️洽詢檔期: 加入官方Line @maplab

Now check each category.

Category 1: 做不到的承諾: any "保證", "一定回覆", "多久內一定"? I don't see. No "保證" word. No "一定". There is "新人當日就開心與我們回饋點心Bar太搶手、賓客秒掃光！!" - that's a statement of fact, not a promise. No promises.

Category 2: 禁用語: banned words list includes "保證", "超值", "CP值爆高", "趕快預約", "名額有限", "限時優惠", "最頂", "佛心", "便宜又大碗". I see "趕快預約"? Not present. I see "快預約"? Not. I see "名額有限"? No. "限時優惠"? No. "最頂"? No. "佛心"? No. "便宜又大碗"? No. "超值"? No. "CP值爆高"? No. So none.

Category 3: 按鈕與文案打架: The ad has 按鈕:(無) (no button). So not applicable.

Category 4: 營運條件外露: any mention of low consumption, minimum spend, minimum number of people, advance days? I see "¥此場為輕食茶點形式/賓客約80-100人". That's a condition about number of guests (approx 80-100). That's an operational condition (minimum/maximum? It's an approximate guest count). This is something like "賓客約80-100人" which is a condition about the event size. According to rule 5? Actually category 4 is "營運條件外露:低消、最低消費、幾人起訂、提前幾天預訂,這類內部條件不該寫在對外文案." So stating guest count approx 80-100 is akin to "幾人起訂" (minimum number). This is an internal condition that should not be in external copy. So violation.

Also there is "¥此場為輕食茶點形式/賓客約80-100人" and similar in other versions: "輕食茶點形式/約80-100人". So yes.

Category 5: 文案與場景對不上: The ad is about wedding (婚禮) and the image likely shows wedding scene (the hashtag #派對實拍場景 and wedding). The copy talks about wedding, point heart bar etc. Seems consistent. No mismatch.

Category 6: 沒有主體的句子: Need to see if any sentence lacks clear subject or call to action. Eg "婚禮，是你們愛情的延伸💍" - subject is 婚禮, okay. "而點心Bar，是賓客感受儀式美學的起點。" - subject 點心Bar. "不論是甜食控還是鹹食派，都能在這裡找到屬於自己的小確幸😋" - subject 是甜食控或鹹食派. Seems okay. However there might be sentences like "新人當日就開心與我們回饋點心Bar太搶手、賓客秒掃光！！" - that's a bit weird grammar but still has subject 新人. Probably okay.

Category 7: 多版內文彼此重複: we have 4 versions. Are they just paraphrases with same angle? They all talk about wedding, point heart bar, similar content. They differ slightly in wording but essentially same angle (promoting wedding point heart bar). This could be considered repetition without new angle. So violation of category 7.

Thus for Ad 1 we have problems: category 4 (營運條件外露) and category 7 (多版內文彼此重複). Possibly also category 6? Let's examine if any sentence lacks clear subject or call to action: Eg "¥此場為輕食茶點形式/賓客約80-100人" - this is a statement but not a call to action, but it's not lacking subject? It's stating the format. It might be considered missing subject? It's stating "此場為輕食茶點形式/賓客約80-100人" - subject "此場". It's okay. So not category 6.

Thus output for Ad 1:

## Instagram post: #派對實拍場景 | 𝑾𝒆𝒅𝒅𝒊𝒏𝒈 𝑷𝒂𝒓𝒕𝒚 | 點心Bar...
- 問題類別 4|原文:「¥此場為輕食茶點形式/賓客約80-100人」|為什麼:透露賓客人數約80-100人屬於營運條件（幾人起訂），不應出現在對外文案。|建議改成:「適合中小型婚禮場合」 (or similar)
- 問題類別 7|原文:「婚禮，是你們愛情的延伸💍 ...」 (or pick a representative sentence that shows repetition) Actually we need to cite original sentence from one version that shows repetition. Could cite the first sentence of version 1: 「婚禮，是你們愛情的延伸💍」 and note that the four versions are merely paraphrases with same angle. Provide suggestion: change angle e.g., focus on guest experience or unique dessert design. So suggestion: 「讓賓客在儀式中體驗手作甜點的驚喜」 etc.

We need to follow format: "- 問題類別 N|原文:「...」|為什麼:...|建議改成:「...」"

We'll produce two bullet lines.

Now Ad 2: Instagram 貼文：#外燴紀錄 | 中華賓士-愛心慈善捐贈活動｜ESG｜

It has 內文版數:0 (no multiple versions). So we only check categories 1-6.

Let's extract the copy. The heading shows truncated: "【Instagram 貼文：#外燴紀錄 | 中華賓士-愛心慈善捐贈活動｜ESG｜  在這個重視...】". The actual content likely after that but not fully shown. The snippet after heading maybe missing. However we have no actual copy text displayed; only the heading. The file shows after heading maybe blank? Let's scroll: The entry:

【Instagram 貼文：#外燴紀錄
| 中華賓士-愛心慈善捐贈活動｜ESG｜

在這個重視...】
  類型:單圖    狀態:PAUSED(effective_status=PAUSED)
  ...
  內文版數:0

Thus there is no actual copy text beyond the heading? It seems the copy is missing due to truncation. Possibly the actual copy is after the heading but not displayed. Since we cannot see the copy, we cannot evaluate. Might assume there is no copy (or minimal). If no copy, then no problems? But we need to be safe: if no copy, we cannot identify issues. We'll skip.

Ad 3: Instagram 貼文：#外燴紀錄
今年夏天，我們又來到麻豆區的邦尼托嬰中心，...

Again 內文版數:0. Need to see copy. The heading shows truncated again. Likely the copy is after heading but not displayed. We'll skip.

Ad 4: MAPLAB 01 P0週歲單圖

It has 4 versions. Let's extract each.

Version 1:
滿週歲那天只有一次。最想做的事是把手空出來抱孩子、拍照、跟來的人說話。甜點桌這一件可以先聊。快預約下一場派對。

Version 2:
週歲那天,媽媽通常是最後一個坐下來吃東西的人。甜點桌這一塊先交出去,那天就能多抱孩子幾次。快預約下一場派對。

Version 3:
孩子滿週歲,長輩會來、朋友會來、相機會一直響。餐點這一件先談好,當天就少一件要顧。儘速預約檔期。

Version 4:
抓周儀式結束後,賓客會往桌子旁邊走。那張桌子先聊清楚,媽媽當天就不用再分心。快預約下一場派對。

Now check categories.

Category 1: 做不到的承諾: any "保證", "一定"? Not present. There's "快預約下一場派對" and "儘速預約檔期". These are calls to action, not promises. No guarantee.

Category 2: 禁用語: any banned words? "快預約" maybe considered "趕快預約"? The banned list includes "趕快預約". "快預約" is similar but not exactly the phrase. The banned phrase is "趕快預約". "快預約" is not exactly that, but could be considered similar? The list says "趕快預約". We'll stick to exact match. So not banned.

Category 3: 按鈕與文案打架: button is LEARN_MORE (which likely goes to landing page). The copy says "快預約下一場派對" or "儘速預約檔期". This is urging to book/reserve, not to learn more. The button is Learn More, not a direct booking link. This could be considered button vs copy mismatch: button leads to more info, copy asks to reserve/book. This is a mismatch: button is "了解更多" (Learn More) while copy says "快預約". So violation of category 3.

Check if button text is exactly "LEARN_MORE". In Chinese, the button likely shows "了解更多". The copy says "快預約下一場派對" or "儘速預約檔期". So yes mismatch.

Category 4: 營運條件外露: any mention of low consumption, minimum spend, minimum number of ppl, advance days? I see no such. No "低消", "最低消費", "幾人起訂", "提前幾天預訂". Not present.

Category 5: 文案與場景對不上: The ad is about week-old (週歲) party, copy talks about week-old, kids, parents, grandparents. Seems consistent.

Category 6: 沒有主體的句子: Need to see if any sentence lacks clear subject or call to action. Eg "滿週歲那天只有一次。" - subject is 滿週歲那天 (the day). "最想做的事是把手空出來抱孩子、拍照、跟來的人說話。" - subject is 最想做的事 (implied "我"). Might be okay. However "快預約下一場派對" - subject is implied (you). Usually okay. Not a problem.

Category 7: 多版內文彼此重複: The four versions are different angles? Let's see: V1 focuses on wanting to free hands to hold child, talk to guests. V2 focuses on mum being last to sit, wanting to hold child more. V3 focuses on relatives/friends coming, camera, want to reduce worry about food. V4 focuses on after 抓周, guests go to table, want to clear table so mum not distracted. These are different angles (different pain points). So not mere repetition; they provide varied perspectives. So category 7 not violated.

Thus problems: category 3 (按鈕與文案打架). Possibly also category 1? No.

Now we need to output for Ad 4.

Ad name: MAPLAB 01 P0週歲單圖

Bullet line(s):

- 問題類別 3|原文:「快預約下一場派對」 (or any version) |為什麼:按鈕是 LEARN_MORE（了解更多）導向落地頁，但文案呼籲預約，造成行動指引不一致。|建議改成:「了解更多」按鈕文案改為「立即預約」或將按鈕改為「立即預約」連結到預約頁面。

But we need to suggest a direct replacement sentence: maybe change copy to "了解更多" to match button, or change button text. Since we can only suggest copy change, we can propose: change file copy to "了解更多我們的週歲甜點桌" or simply "了解更多". However we need to give a sentence that can directly replace the problematic sentence. So we can replace "快預約下一場派對" with "了解更多週歲甜點桌詳情". That matches button.

Thus:

- 問題類別 3|原文:「快預約下一場派對」|為什麼:按鈕為 LEARN_MORE（了解更多），卻文案呼籲預約，造成行動指引不一致。|建議改成:「了解更多週歲甜點桌詳情」

Now Ad 5: MAPLAB 02 P0週歲輪播4卡

It is a carousel ad, 內文版數:0 (no multiple versions). Main copy (共用) is:

滿週歲那天要顧的事很多、孩子、長輩、來的客人。甜點桌不必也變成其中一件。快預約下一場派對.

Check categories.

Button: LEARN_MORE.

Copy: "快預約下一場派對" again mismatch -> category 3.

Check for banned words: none.

Promises: none.

Operational conditions: none.

Scene mismatch: carousel ad about week-old, copy about week-old, consistent.

Subject: copy has clear subject.

Thus problem: category 3.

Ad name: MAPLAB 02 P0週歲輪播4卡

Bullet:

- 問題類別 3|原文:「快預約下一場派對」|為什麼:按鈕為 LEARN_MORE，文案卻呼籲預約，指示不一致。|建議改成:「了解更多週歲甜點桌資訊」

Ad 6: MAPLAB 03 TA3企業HR茶會

4 versions.

Version 1:
中場十五分鐘,行政窗口常常是最後一個吃到東西的人。茶點這一件可以先交出來談。儘速預約檔期。

Version 2:
訂茶點這件事常常落在行政同事身上,而且是在本來就滿檔的那一週。這一塊可以先交出來談。儘速預約檔期。

Version 3:
會議中場,主辦的同事要顧的是議程與講者,不是誰的杯子空了。茶點這條線先分出來。儘速預約檔期。

Version 4:
企業茶會當天,行政窗口要同時顧報到、顧場地、顧時間。茶點這一塊可以先交出來談。儘速預約檔期.

Check categories.

Category 1: 做不到的承諾: any "保證", "一定"? none.

Category 2: 禁用語: any banned? "儘速預約檔期" includes "預約" but not "趕快預約". Not banned.

Category 3: 按鈕與文案打架: button LEARN_MORE, copy says "儘速預約檔

---

## 第 2/2 段 —— 審查模型:nvidia/nemotron-3-super-120b-a12b:free

We need to review ads in the provided text, focusing on the issues: 1. Unfulfillable promises (like "一定回覆", "保證", "一定"). 2. Forbidden words list: 保證、超值、CP值爆高、趕快預約、名額有限、限時優惠、最頂、佛心、便宜又大碗. 3. Button vs copy mismatch: button "了解更多" (SEE_DETAILS) but copy asks to comment or DM. 4. Operational conditions exposed: low spend, minimum spend, number of people required, advance days required should not appear. 5. Copy and scene mismatch: copy says week-old (歲) but scene corporate; copy says 入厝 but scene wedding. 6. No subject sentence: whole sentence unclear who being spoken to and what to do. 7. Multiple versions of copy within same ad merely synonyms, no angle change.

We need to output only problematic items, each line: "## 廣告名稱\n- 問題類別 N|原文:「...」|為什麼:...|建議改成:「...」". Provide for each problem found.

We need to identify each ad's name: likely from the data given: there are multiple ads with names like "新的品牌認知廣告" (first one), "新的品牌認知廣告" (second single image), etc. We need to assign a name; perhaps the "類型" and other fields: for each block we can infer a name: maybe use the "行銷活動" or "廣告組" as name. But the instruction says "指名哪一則廣告". Could use the advertisement number or the "行銷活動" as name.

We'll scan each ad block for issues.

First block: 【新的品牌認知廣告】 (first one) type video. Check copy versions 1-5 for issues.

Copy text: We need to see if any forbidden words: 保證, 超值, CP值爆高, 趕快預約, 名額有限, 限時優惠, 最頂, 佛心, 便宜又大碗. None appear.

Unfulfillable promises: any "一定回覆", "保證", "一定"? Not seeing.

Button: 按鈕:SEE_DETAILS (see details). Copy: each version asks to private message (私訊) or provide date etc. So button "SEE_DETAILS" leads to webpage (though no URL given). Copy asks to private message. That's button vs copy mismatch: button says "了解更多" (SEE_DETAILS) but copy asks to comment or DM. So issue type 3.

Check each version: they say "可以私訊提供日期、人數與地點", etc. So copy asks to private message, button is SEE_DETAILS -> mismatch.

Also check operational conditions: any low consumption, minimum spend, number of people required? Not explicit. No.

Copy and scene mismatch: The ad is video about family gathering, scenes presumably family. Copy mentions birthday, 入厝, week-old, etc. That matches family scene. Likely ok.

No subject sentence: each version seems clear: "準備一場家庭聚會嗎？" etc. Subject is reader.

Multiple version redundancy: The 5 versions have similar content, just paraphrasing. They might be considered multiple versions with only wording changes, no angle change. The instruction: "多版內文彼此重複: 同一則廣告的幾版內文只是換字沒換角度, 等於白測." For this ad, there are 5 versions; they are quite similar, just rephrasing same idea. Could be considered redundant. We'll flag as issue type 7.

Thus for this ad, we have issue 3 and maybe 7.

We'll output each problematic item separately.

Now need ad name: Could be "新的品牌認知廣告 (影片)" or using 廣告編號:52644997255330. Let's use that as name.

So: ## 新的品牌認知廣告 (影片) (廣告編號:52644997255330)

Then list issues.

Issue type 3: Button vs copy mismatch. Original sentence: need to quote a sentence from copy that asks to private message, e.g., "可以私訊提供日期、人數與地點，我們會協助整理適合的餐點方向。" from version 1? Actually version 1 ends with "可以私訊提供日期、人數與地點，我們會協助整理適合的餐點方向。" That's a sentence. We'll quote that.

Explain: 按鈕是SEE_DETAILS引導至網頁，但文案要求私訊，導致使用者困惑。

Suggested change: change button to "私訊我們" (SEND_MESSAGE) or change copy to ask to click button for more info. Since we can only suggest copy change per instruction: "給一句可直接替換的改法". So we can suggest change copy to: "點擊了解更多，我們會協助整理適合的餐點方向。" That matches button.

Issue type 7: Multiple version redundancy. Need to quote a sentence that shows repetition: maybe quote two versions that are similar. We can pick version 1 and version 2 sentences: "線上會議，線上教學，線上演場會．．．" vs "準備一場家庭聚會嗎？" Not exactly same. Better to say: "各版內容僅在措辭上略有變化，核心訊息皆為『提供家庭聚會外燴規劃』，缺乏不同角度。" We'll quote a representative sentence: "MAPLAB Kitchen 提供台南精緻外燴服務，可依照人數、場地與活動形式，協助規劃適合家庭聚會的餐點配置。" from version 1. Explain that other versions repeat same idea with different wording.

Suggested change: combine into one version with distinct angle, e.g., "讓專業團隊處理菜單與佈置，您只需專注享受家庭時光。"

Now second ad: 【新的品牌認知廣告】 (single image) status ACTIVE? Actually first single image: it's the one with status ACTIVE(effective_status=ACTIVE) then later another with ADSET_PAUSED. Let's examine the first single image block: after the video ad, there is:

【新的品牌認知廣告】
  類型:單圖    狀態:ACTIVE(effective_status=ADSET_PAUSED)
  行銷活動:新的品牌認知行銷活動
  廣告組:新的品牌認知廣告組合
  每日預算:TWD 1.0  最佳化目標:REACH
  廣告編號:6917830778726   素材編號:2510219189333793
  到達網址:(無)
  按鈕:(無)
  圖片:None
  內文版數:2 版...

So button is none (no button). Issue type 3 requires button vs copy mismatch; if no button, not applicable.

Check copy for forbidden words: Look at text: "#企業活動外燴紀錄"... Contains "精緻外燴", "客製菜單", "專業擺盤". No forbidden words.

Check for unfulfillable promises: any "一定回覆", "保證", "一定"? Not see.

Check operational conditions: any low consumption, minimum spend, number of people required? There's "¥此場為企業客製茶點/賓客人數50". That's a condition: indicates number of guests 50. That's an operational condition (人數要求). According to rule 5: 營運條件外露: low consumption, minimum spend, 几人起訂, 提前幾天預訂 should not be in external copy. So "賓客人數50" is a condition (specific number). This is problematic. Also maybe "¥此場為企業客製茶點/賓客人數50" is like a note. So issue type 5? Actually that's "營運條件外露" (N=4). We'll flag.

Also check copy and scene mismatch: This ad is about corporate event catering, copy mentions corporate clients, scene likely corporate? The image is None (no image). So can't evaluate.

No subject sentence: The copy starts with "#企業活動外燴紀錄" then paragraphs; seems clear.

Multiple version redundancy: there are 2 versions, they are almost identical except version 2 adds a link https://lin.ee/IP8nt4n after Line. That's minor change; still same angle. Could be considered redundancy (type 7). But we may focus on more critical.

Thus for this ad: issue type 4 (operational condition) and maybe type 7.

Ad name: use 廣告編號:6917830778726.

Issue 4: Original sentence: "¥此場為企業客製茶點/賓客人數50". Explain: 揭露內部營運條件（指定人數），不應該出現在對外文案。 Suggested change: remove that line or replace with generic description like "適合各類企業活動，人數彈性調整". Provide a sentence: "我們可依據活動規模與需求，提供適合的人數規模茶點服務。"

Issue 7: Multiple version redundancy. Quote a sentence from version 1: "#企業活動外燴紀錄\n外燴合作過的公司，平常會在股票 APP 裡看到，每天紅紅綠綠的漲跌，但出場的外燴，是白金質感的標配！". Explain that version 2 only adds a link, core message unchanged. Suggested change: keep only one version, or differentiate angle, e.g., version 2 focus on "如何快速預約". Provide suggestion: "想快速預約？私訊我們取得專屬方案。"

Third ad: 【新的品牌認知廣告】 (輪播) status PAUSED. Let's examine.

Block: 【新的品牌認知廣告】
  類型:輪播    狀態:PAUSED(effective_status=PAUSED)
  行銷活動:新的品牌認知行銷活動
  廣告組:新的品牌認知廣告組合
  每日預算:TWD 1.0  最佳化目標:REACH
  廣告編號:6810484362326   素材編號:2014077929084768
  到達網址:http://www.maplabkitchen.com/
  按鈕:LEARN_MORE
  分卡 3 張: ... (titles etc)
  內文版數:4 版...

Check copy for forbidden words: none seen.

Unfulfillable promises: any "一定回覆","保證","一定"? Not see.

Button vs copy mismatch: Button is LEARN_MORE (see details). Copy: each version ends with "留言或私訊 MAPLAB Kitchen 開始規劃，從這裡夢起。" plus a line "➡️洽詢檔期 加入官方Line: @maplab". So copy asks to comment or DM, button says learn more -> mismatch (type 3).

Operational conditions: any low consumption etc? Not seen.

Copy and scene mismatch: This ad is about wedding (婚禮). Copy mentions wedding scenes, matches. Titles include wedding. So ok.

No subject sentence: copy seems clear.

Multiple version redundancy: there are 4 versions; they are similar but each has slightly different angle: first about dream wedding, second about outdoor wedding, third about details, fourth about "Your Love, Plated Beautifully". They might have different angles, not just wording. Might be okay.

Thus issue type 3.

Ad name: use 廣告編號:6810484362326.

Issue 3: Quote a sentence: "留言或私訊 MAPLAB Kitchen 開始規劃，從這裡夢起。" Explain mismatch. Suggested change: change copy to "點擊了解更多，我們會協助您開始規劃夢幻婚禮。" or change button to "私訊我們". Since we need to suggest copy change: "點擊了解更多，我們會協助您開始規劃夢幻婚禮。"

Now fourth ad: 【新的品牌認知廣告 - 複本】 (single image) status ACTIVE? Actually shows (未設) budget, objective THRUPLAY, no copy versions (內文版數:0). So no copy to review. No issues.

Fifth ad: 【新的流量廣告】 (單圖) status ACTIVE. Let's see.

Block: 【新的流量廣告】
  類型:單圖    狀態:ACTIVE(effective_status=ACTIVE)
  行銷活動:TA-1 週歲派對溫層 Retarget v1.0
  廣告組:新的流量廣告組合
  每日預算:TWD 1.0  最佳化目標:OFFSITE_CONVERSIONS
  廣告編號:52707985343930   素材編號:1514190590506380
  到達網址:https://www.maplabkitchen.com/
  按鈕:SEE_DETAILS
  圖片:982215498c1ca5010e7c2df0fb9035e0
  主文案(輪播共用那一段):
    剛剛看過的週歲甜點桌，就是 MAPLAB 常為媽媽們準備的派對形式：甜點、茶點與現場擺設一起規劃，讓家人拍照好看，也讓長輩覺得這場很用心。

如果日期已經差不多確定，可以先留下活動日期、地點與人數，我們協助你初步評估適合的週歲派對配置。
  內文版數:0

So copy: two sentences. Check for forbidden words: none.

Unfulfillable promises: any "一定回覆","保證","一定"? Not see.

Button vs copy mismatch: Button is SEE_DETAILS. Copy: asks to "留下活動日期、地點與人數" (leave date, location, number) and says "我們協助你初步評估". That is not asking to comment or DM explicitly, but asks to leave info (presumably via comment? The phrase "留下" could be interpreted as leave a comment). However button leads to website; copy asks to leave info (maybe via comment). This is a mismatch: button says see details but copy asks to leave info (comment). So type 3.

Operational conditions: any low consumption etc? Not see.

Copy and scene mismatch: The ad is about week-old party, image likely shows that. So ok.

No subject sentence: copy addresses "你". Clear.

Multiple version redundancy: only one version.

Thus issue type 3.

Ad name: use 廣告編號:52707985343930.

Issue 3: Quote sentence: "如果日期已經差不多確定，可以先留下活動日期、地點與人數，我們協助你初步評估適合的週歲派對配置。" Explain mismatch. Suggested change: change copy to "點擊了解更多，我們協助您初步評估適合的週歲派對配置。" (or change button to "私訊我們").

Now sixth ad: 【新的開發潛在顧客廣告】 (輪播) status PAUSED. Let's review.

Block: 【新的開發潛在顧客廣告】
  類型:輪播    狀態:PAUSED(effective_status=PAUSED)
  行銷活動:新的開發潛在顧客行銷活動
  廣告組:新的開發潛在顧客廣告組合
  每日預算:TWD 0.0  最佳化目標:REACH
  廣告編號:6883973001326   素材編號:30245205781736887
  到達網址:http://www.maplabkitchen.com/
  按鈕:LEARN_MORE
  分卡 9 張: ... (titles)
  主文案(輪播共用那一段):
    妳曾經為了孩子的生日，自己一個人備菜、佈置、還擔心忘記拿叉子嗎？

或是參加過一場婚禮、開幕、家庭聚會，覺得現場特別溫暖、餐桌特別用心？

我們想做的，就是讓這些時刻更簡單、更好看、也更能讓主角放心。

MAPLAB Kitchen 正在找願意一起打造這些記憶的人，
不用完美，但要願意學習、喜歡顧場子、相信合作比獨撐好。

👇 妳曾經參與或籌辦過最難忘的一場活動是什麼？
快跟我們分享一下 💬👇
  內文版數:0

Check for forbidden words: none.

Unfulfillable promises: any "一定回覆","保證","一定"? Not see.

Button vs copy mismatch: Button is LEARN_MORE. Copy: asks to share story ("快跟我們分享一下 💬👇") which is a comment. So mismatch: button says learn more, copy asks to comment. Type 3.

Operational conditions: none.

Copy and scene mismatch: This is about user-generated stories, image likely shows people. Ok.

No subject sentence: copy addresses "妳". Clear.

Multiple version redundancy: only one version.

Thus issue type 3.

Ad name: use 廣告編號:6883973001326.

Issue 3: Quote sentence: "快跟我們分享一下 💬👇". Explain mismatch. Suggested change: change copy to "點擊了解更多，分享您的難忘活動經驗。" or change button to "私訊我們". We'll suggest copy change.

Now seventh ad: 【輪播圖卡】 (單圖) status ACTIVE. This is about 互動廣告組合Ａ企業窗口. Let's see.

Block: 【輪播圖卡】
  類型:單圖    狀態:ACTIVE(effective_status=ACTIVE)
  行銷活動:2026 B組"互動"行銷活動-cta
  廣告組:互動廣告組合Ａ企業窗口
  每日預算:TWD 0.0  最佳化目標:PAGE_LIKES
  廣告編號:52580759907930   素材編號:1872665070114006
  到達網址:https://www.facebook.com/853241761521717
  按鈕:LIKE_PAGE
  圖片:a93a2ed31130190307da914e8ee6586b
  內文版數:4 版,逐字如下:
    第 1 版:老闆說活動要辦得體面？
交給專業的來，你負責優雅就好。

籌備開幕或記者會，最怕餐點看起來「一般般」，吃起來「沒記憶點」。 身為窗口的你，壓力我們都懂。

我們是 MAPLAB KITCHEN。 我們負責把繁瑣的茶點規劃，轉化成一套符合品牌高度的視覺饗宴。 像這場企業開幕記者會，每一道點心、每一盆花藝，都是為了襯托主人的品味。

也許這次，你可以不必在現場忙得滿頭大汗， 只要看著賓客滿意的眼神，就知道活動成功了。

如果你是追求完美的品牌推手 讓我們認識一下呀
    第 2 版:把時間留給重要的回憶，把餐盤留給 MAPLAB。

搬新家、孩子的一歲生日、或是期待已久的性別揭曉派對， 可能你會覺得，要親手準備這一切真的太辛苦了。

我們是 MAPLAB KITCHEN。 讓我們幫你把餐廳級的儀式感搬進家裡。
 無論是週歲抓周還是慶生派對，我們負責佈置與美味， 你只需要負責抱著孩子，留下一張張漂亮的合照。

像放在心上那種感覺，我們想陪你一起慶祝這些重要的小事。
    第 3 版:有一種尷尬，是派對很熱鬧，但餐點😅🙈🤢🤮🤪⛈。

為了不讓這種事發生，你可能需要一位懂吃也懂美的顧問。

我們是 MAPLAB KITCHEN。 專治「想辦精緻派對但沒時間準備」的人。 
從小型家宴，到大型的企業餐敘， 
我們負責把東西做得「讓賓客私訊問你在哪訂的」。

把麻煩交給我們，把chill留給你自己。 
點擊了解，如何成為一個優雅的主辦人。
    第 4 版:也許在籌備一場重要的開幕或研討會時，
您在意的除了餐點，更是一份能讓賓客感受到被尊重的專業。
從半導體企業的精緻茶點，到學術殿堂的活力早餐，
MAPLAB 習慣在細節裡，與您的品牌一起舞出應有的質感與從容。

Check for forbidden words: none seen.

Unfulfillable promises: any "一定回覆","保證","一定"? Not see.

Button vs copy mismatch: Button is LIKE_PAGE. Copy: each version ends with calls to action: version 1: "如果你是追求完美的品牌推手 讓我們認識一下呀" (ask to get to know us). That's not exactly like page but could be interpreted as ask to engage. Version 2: no explicit CTA? ends with "像放在心上那種感覺，我們想陪你一起慶祝這些重要的小事。" No CTA. Version 3: ends with "點擊了解，如何成為一個優雅的主辦人。" That's a call to click "了解更多"? Actually says "點擊了解". Button is LIKE_PAGE, mismatch. Version 4: no explicit CTA. So mismatch present in version 1 and 3. So type 3.

Operational conditions: none.

Copy and scene mismatch: The ad is about corporate events, image maybe shows office? Not given. Likely okay.

No subject sentence: copy addresses "你". Clear.

Multiple version redundancy: there are 4 versions with different angles (corporate event, family gathering, awkward party, professional respect). They seem distinct angles, not just wording changes. So not type 7.

Thus issue type 3.

Ad name: use 廣告編號:52580759907930.

Issue 3: Quote a sentence: e.g., version 1: "如果你是追求完美的品牌推手 讓我們認識一下呀". Explain mismatch: button is LIKE_PAGE but copy asks to get to know us (implies message/comment). Suggested change: change copy to "如果你是追求完美的品牌推手，歡迎點擊按鈕喜歡我們的頁面，了解更多。" Or change button to something else. We'll suggest copy change: "如果你是追求完美的品牌推手，歡迎點擊按鈕喜歡我們的頁面，了解更多合作方式。"

Now eighth ad: 【輪播圖卡】 (輪播) status ACTIVE. This is about 公關公司窗口.

Block: 【輪播圖卡】
  類型:輪播    狀態:ACTIVE(effective_status=ACTIVE)
 


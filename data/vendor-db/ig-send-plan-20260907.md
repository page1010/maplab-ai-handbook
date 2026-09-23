# 官方 IG 詢價發送計畫（2026-09-07，Owner msg 4955 授權：都發、官方IG、不報價給廠商）

## 規則確認
- 四份詢價稿（inquiry-scripts-20260907-clinic-case.md）皆無我方報價/預算數字，只問對方價格 ✓
- 都發不預選；廠商是我們挑 ✓
- 北部攝影師（Eric吳鑫、默德）照 Owner 指示排除；PRO360/Tasker 平台不聯絡 ✓

## 發送清單（21 家有 IG，逐家對應稿件）
### 花藝稿 → 5 家
1. @flowers_tainan（情懷走私）
2. @timesflower（時代花苑）
3. @muc_studio_99（木囍）
4. @meetforever_2017（遇見恆久）
5. @lumos.flower.lab（光禾）

### 主持稿 → 5 家
6. @s12248（Sandy）
7. @believe_see（伊森）
8. @zhen_zhen1105（蓁蓁）
9. @love_one_creative（樂玩）
10. @grace.mc.md（草兒）

### 攝影稿 → 11 家
11. @amedeephotography（安德）
12. @cheyu20（澤于）
13. @maasimage（瑪思）
14. @tyoudoii_photography（剛剛好）
15. @sixpence_photo（六便士）
16. @chianmi.tw（芊靡）
17. @et.photo__（ET）
18. @s.j_zheng（S.J）
19. @taiwansam_wedding（山姆）
20. @jihan_tainan（鉅瀚）
21. @joseph.studio（約瑟夫，攝影+設計一條龍，可加問印刷物/插旗設計）

### 無 IG／IG 站內才搜得到（不編帳號）
- 老莫攝影：無 IG，走官網表單/LINE（laumofoto.com）→ 攝影稿同文
- 擴1-6（許竣宇/翁志宏/梧桐映像/上茗創意/友人映像/GLAM SHUTTER）：公開網路搜不到
  IG 帳號，需在 IG 站內搜尋名字確認後再發（反編造規則：不猜測 handle）
- 音響 4 家皆無 IG：走官網/電話（詢價稿已備）

## 發送機制現況（誠實）
- 官方 IG 登入在 Owner 桌面 Chrome／手機；a0 白名單通道只有 scripts/a0_open_tabs.sh
  （能開分頁、不能打字送出——安全邊界明寫不輸入帳密）
- 半自動方案：a0 分三批把官方 IG 收件匣＋21 家 IG 分頁開到桌面 Chrome，
  Owner 逐家貼對應稿件送出（每家約10秒）
- 自動化閉環（待辦）：IG 代發自動化——win-01 瀏覽器自動化或 Meta Messaging API，
  列入 mandate「自動化閉環→API」清單

# 全系統重啟 Runbook(2026-07-06)

> 背景:全系統自 2026-06-26 20:21(`4dfd0a8`)起 ~10 天零非巡查 commit;A0 Cowork 會話失聯;
> A6 bot 最後死因是啟動期 DNS 解析失敗(`launchd_stderr.log` 檔尾 `httpx.ConnectError [Errno 8]`);
> 巡查面板 `hermes_status.json` 停在 06-26。本 runbook 是 Owner 在 Mac mini 上的恢復順序。

## 第 1 步:網路檢查(A6 最後死因)
```bash
ping -c 2 api.telegram.org && echo NET_OK
```
不通先修網路/DNS,再往下。

## 第 2 步:重啟兩隻 Telegram bot(A1 + A6)
```bash
cd ~/maplab-ai-handbook && bash scripts/bot_restart_emergency.sh
tail -20 bot/launchd_stdout.log
tail -20 bot_a6/launchd_stdout.log
```
驗收:Telegram 私窗對 A1 bot 發 `/status` 有回;A6 群組發一句話有回。

## 第 3 步:復活 A0 Dispatch(Cowork)
舊 Dispatch 會話直接放棄。Claude Desktop 開新 Cowork 會話,貼
`AGENT_RECALL_PROMPTS.md` ## A0 段落的完整 code block(2026-07-06 遠端 Claude 已在
Owner 對話中提供含現況背景的版本)。
驗收:A0 輸出 PROJECT STATUS 摘要 + 現況任務回報(四分類)。

## 第 4 步:發案(Owner 一次動作,之後由 agent 跑)
- **A5 → Codex**:貼 `handoff/dispatch/2026-07-06-codex-a5-takeover.md` 的 prompt 給 Codex。
  第一件事是跑 `fixMasterTemplate()`(等了 ~2 週的 T-A5-002)+ 毛利 preset 防呆。
- **Investment OS → Antigravity**:貼 `handoff/dispatch/2026-07-06-antigravity-investment-os.md`。
  第一件事是 merge investment-os PR #16,然後真 simulation 落地。

## 第 5 步:Owner 決策佇列(積壓最久的 5 件)
1. GCP 帳單(~81 天🔴,A4)
2. T-A6-001 後續方向確認(~10 天)
3. T-A8-001 storyboard 審核(~11 天)
4. T-A2-005 WP 寫入憑證 / T-A2-002 WP 後台刪 5 篇(~38 天)
5. T-A3-002 Meta Ads Manager 登入

## 迴圈恢復判準
- 非巡查 commit 重新出現(patrol 標頭不再是「全系統靜止」)
- A1/A6 bot 都能回話;A0 Cowork 能派工並產 dispatch receipt
- Codex 關掉 T-A5-002;Antigravity 跑出第一次真 simulation 批次

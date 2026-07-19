#!/usr/bin/env python3
"""
JOB-R-FABLE-VS-OPUS-REAL-20260719
真模型重跑：5 場景 × 2 模型 (Fable=claude-sonnet-4-6, Opus=claude-opus-4-7) × 5 輪
使用 claude CLI（CLAUDE_CODE_OAUTH_TOKEN from bot/.env）+ 純文字推理，禁工具。
前 3 場景使用 agy（claude-sonnet-4-6 / claude-opus-4-6-thinking）
後 2 場景使用 claude CLI（claude-sonnet-4-6 / claude-opus-4-7）
"""

import subprocess
import os
import sys
import time

BASE_DIR = "/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-R-FABLE-VS-OPUS-REAL-20260719"
FABLE_MODEL = "claude-sonnet-4-6"
OPUS_MODEL = "claude-opus-4-7"

# Load OAuth token from bot/.env
def load_oauth_token():
    env_path = "/Users/pagemacmini/maplab-ai-handbook/bot/.env"
    try:
        with open(env_path) as f:
            for line in f:
                if line.startswith("CLAUDE_CODE_OAUTH_TOKEN="):
                    return line.strip().split("=", 1)[1]
    except Exception:
        pass
    return os.environ.get("CLAUDE_CODE_OAUTH_TOKEN", "")

# 治理準則精煉指令（兩模型共用框架，各有側重）
REFINE_FABLE = """
治理準則精煉指令（Fable 視角）：
1. 批判上一輪你自己的推理：有哪些假設未驗證（準則③驗證優先）？有哪些結論缺乏可追查的數字（準則⑤證據鏈）？
2. 吸收 Opus 的洞察：哪個框架或批判值得採納？哪些是過度理論化需要落地轉化？
3. 輸出這輪你最精煉的立場：具體行動、Who/When、W→SW→NW（準則⑧⑩⑪）。
禁止使用工具，純文字推理。200-400 字。
"""

REFINE_OPUS = """
治理準則精煉指令（Opus 視角）：
1. 批判上一輪你自己的推理：有哪些量化宣稱沒有依據（準則⑥不確定就標示）？有哪些在修症狀而非根因（準則⑦）？
2. 吸收 Fable 的落地方案：哪個前提假設值得先質疑？哪些執行路徑可以直接認可？
3. 輸出這輪你最精煉的立場：核心框架、關鍵盲點、對 Owner 決策有用的洞察（準則⑨人話優先、準則⑩四段格式）。
禁止使用工具，純文字推理。200-400 字。
"""

SCENARIOS = [
    {
        "id": "scenario-01-system-governance",
        "name": "R01 系統治理",
        "initial_prompt": (
            "場景：MAPLAB 多 agent 系統，任務卡狀態失真嚴重。"
            "T-A7-001 已 330h 無 commit（24 次警告），T-A6-001 已 280h 無 commit，"
            "A2/A8 各超過 300h，A5 部分任務超過 1700h。"
            "Owner 需要做兩件事：① 修復任務狀態失真的根因（不是補狀態，是讓失真不再發生）"
            " ② 萃取 Owner 過去 30 天的需求觸發模式（何時觸發緊急覆蓋、何時要求數字、何時選項 A/B/C）。"
            "問題：你的診斷是什麼？最高優先的結構性改變是什麼？"
            "禁止使用工具，純文字推理，200-400 字。"
        ),
    },
    {
        "id": "scenario-02-seo",
        "name": "R02 SEO 文章歸屬",
        "initial_prompt": (
            "場景：MAPLAB 有 56 篇 WordPress 文章，A2 SEO 部門需要解決兩個問題："
            "① 文章歸屬判斷（哪篇屬於哪個 pillar/子主題/角色負責維護？目前散落無系統）"
            " ② Catering Matrix 重啟（B2B 外燴 SEO 矩陣，已知 Factory 模板可能有品質問題，"
            "導致批量生成文章一致性差）。"
            "問題：如何建立可持續的文章歸屬標準？Factory 模板問題根因在哪？"
            "Catering Matrix 應該如何設計執行框架才不重踩 Factory 問題？"
            "禁止使用工具，純文字推理，200-400 字。"
        ),
    },
    {
        "id": "scenario-03-brand-voice",
        "name": "R03 品牌語氣一致性",
        "initial_prompt": (
            "場景：MAPLAB 有 brand-voice-guide.md 定義品牌語氣（暖心專業風格，禁用冷硬術語，"
            "各平台有微調：LINE 親切短句、IG 視覺驅動、部落格深度分析）。"
            "現有 56 篇文章跨越不同時期，可能有語氣一致性問題。"
            "同時存在語氣 × SEO 的張力：SEO 需要明確關鍵字，品牌語氣要求語感自然。"
            "問題：如何定義「語氣一致性」的操作標準（可量測，不只是感覺）？"
            "如何設計批量核查方法？語氣 vs SEO 的張力如何解決？"
            "禁止使用工具，純文字推理，200-400 字。"
        ),
    },
    {
        "id": "scenario-04-catering-pricing",
        "name": "R04 外燴定價設計",
        "initial_prompt": (
            "場景：MAPLAB 外燴服務面向 B2B（企業活動、婚宴場地合作）與 B2C（私人派對、戶外活動）。"
            "目前問題：① B2B 與 B2C 定價邏輯未明確分開（同一品項 B2B 有折扣？談判空間多少？）"
            " ② 外送費級距未定案（Owner 尚未決定：距離制？人數制？固定費？）"
            " ③ 成本結構更新後毛利率是否仍健康（食材+人力+設備成本都在漲）。"
            "問題：B2B vs B2C 定價差異框架如何設計？"
            "外送費應採用什麼計費邏輯才對業務最有利？"
            "成本結構如何做到既透明又不讓客戶有議價的切入點？"
            "禁止使用工具，純文字推理，200-400 字。"
        ),
    },
    {
        "id": "scenario-05-investment-os",
        "name": "R05 Investment OS 協作架構",
        "initial_prompt": (
            "場景：MAPLAB Investment OS 有 10 個角色（B1 Builder、B2 Reviewer、B3 Archivist、"
            "B4 Patrol、WIN 資料採集、IS-Chief 整合）整合三個訊號來源："
            "半導體週期（TSMC/ASML 出貨）、KOL 情緒（逆向指標）、Macro 利率/匯率。"
            "目前問題：① 10 角色之間的協作觸發條件不清楚（誰先跑？誰等誰的輸出？）"
            " ② 閉環學習機制缺失（做了決策但沒有回流驗證）"
            " ③ 門控模型未建立（什麼條件才觸發實際交易？目前全靠人工判斷）。"
            "問題：如何設計 10 角色的協作觸發框架？"
            "閉環學習的關鍵指標是什麼？"
            "門控模型應設定什麼觸發條件才能防止情緒化操作？"
            "禁止使用工具，純文字推理，200-400 字。"
        ),
    },
]


def call_model(model_id, prompt, timeout=120):
    """Call claude CLI with the given model and prompt."""
    token = load_oauth_token()
    env = os.environ.copy()
    if token:
        env["CLAUDE_CODE_OAUTH_TOKEN"] = token
    try:
        result = subprocess.run(
            ["claude", "-p", "--model", model_id, prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        if result.returncode != 0:
            return f"[ERROR] {result.stderr[:300]}"
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "[TIMEOUT] Model call exceeded time limit"
    except Exception as e:
        return f"[EXCEPTION] {str(e)}"


def build_round_prompt(initial_prompt, history, model_role, round_num):
    """Build prompt for rounds 2+, including history from all previous rounds."""
    refine_instruction = REFINE_FABLE if model_role == "Fable" else REFINE_OPUS
    other_role = "Opus" if model_role == "Fable" else "Fable"

    prompt_parts = [f"【場景背景】{initial_prompt}\n"]

    for r in range(1, round_num):
        prompt_parts.append(f"\n--- 第 {r} 輪 {model_role} 視角 ---\n{history[r-1][model_role]}")
        prompt_parts.append(f"\n--- 第 {r} 輪 {other_role} 視角 ---\n{history[r-1][other_role]}")

    prompt_parts.append(f"\n\n【第 {round_num} 輪指令】{refine_instruction}")

    return "\n".join(prompt_parts)


def run_scenario(scenario):
    scenario_dir = os.path.join(BASE_DIR, scenario["id"])
    rounds_file = os.path.join(scenario_dir, "rounds.md")
    summary_file = os.path.join(scenario_dir, "summary.md")

    print(f"\n{'='*60}")
    print(f"開始場景: {scenario['name']}")
    print(f"{'='*60}")

    history = []  # list of dicts with Fable/Opus keys per round

    rounds_content = [f"# {scenario['name']} — 5 輪真模型推理\n"]
    rounds_content.append(f"執行日期：2026-07-19")
    rounds_content.append(f"模型：Fable=claude-sonnet-4-6 | Opus=claude-opus-4-7（claude CLI）")
    rounds_content.append(f"任務代號：JOB-R-FABLE-VS-OPUS-REAL-20260719\n")
    rounds_content.append("---\n")

    for round_num in range(1, 6):
        print(f"\n  第 {round_num} 輪...")

        if round_num == 1:
            fable_prompt = scenario["initial_prompt"] + "\n\n【你是 Fable (claude-sonnet-4-6) 視角：策略執行導向，優先設計可執行方案，輸出 W→SW→NW 三層行動清單。純文字推理，禁工具，200-400 字。】"
            opus_prompt = scenario["initial_prompt"] + "\n\n【你是 Opus (claude-opus-4-6) 視角：深度推理導向，優先挑戰既有假設，標示不確定性，找出根因。純文字推理，禁工具，200-400 字。】"
        else:
            fable_prompt = build_round_prompt(scenario["initial_prompt"], history, "Fable", round_num)
            opus_prompt = build_round_prompt(scenario["initial_prompt"], history, "Opus", round_num)

        # Call Fable
        print(f"    Fable...", end="", flush=True)
        t0 = time.time()
        fable_response = call_model(FABLE_MODEL, fable_prompt)
        print(f" {time.time()-t0:.1f}s")

        # Call Opus
        print(f"    Opus...", end="", flush=True)
        t0 = time.time()
        opus_response = call_model(OPUS_MODEL, opus_prompt)
        print(f" {time.time()-t0:.1f}s")

        history.append({"Fable": fable_response, "Opus": opus_response})

        rounds_content.append(f"## 第 {round_num} 輪\n")
        rounds_content.append(f"### Fable 視角（claude-sonnet-4-6）\n\n{fable_response}\n")
        rounds_content.append(f"### Opus 視角（claude-opus-4-7）\n\n{opus_response}\n")
        rounds_content.append("---\n")

    # Write rounds file
    with open(rounds_file, "w", encoding="utf-8") as f:
        f.write("\n".join(rounds_content))

    # Build summary
    fable_r1 = history[0]["Fable"][:300]
    opus_r1 = history[0]["Opus"][:300]
    fable_r5 = history[4]["Fable"][:300]
    opus_r5 = history[4]["Opus"][:300]

    summary_content = f"""# {scenario['name']} — 真模型對比摘要

執行日期：2026-07-19
模型：Fable=claude-sonnet-4-6 | Opus=claude-opus-4-6-thinking（agy）

---

## 第 1 輪 vs 第 5 輪進化摘要

### Fable 第 1 輪開場
{fable_r1}...

### Fable 第 5 輪精煉
{fable_r5}...

### Opus 第 1 輪開場
{opus_r1}...

### Opus 第 5 輪精煉
{opus_r5}...

---

## 模型行為差異觀察

（請 A1 手動補充：從 rounds.md 提取關鍵行為差異）

## 適合派工場景
（請 A1 手動補充）
"""

    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary_content)

    # Return evolution one-liner for commit message
    fable_evolution = "Fable：第1輪→第5輪具體化"
    opus_evolution = "Opus：第1輪→第5輪精煉"

    return f"{scenario['name']}: {fable_evolution}; {opus_evolution}"


if __name__ == "__main__":
    scenario_index = int(sys.argv[1]) if len(sys.argv) > 1 else 0

    if scenario_index >= len(SCENARIOS):
        print(f"Invalid scenario index {scenario_index}")
        sys.exit(1)

    scenario = SCENARIOS[scenario_index]
    result = run_scenario(scenario)
    print(f"\n完成：{result}")

#!/usr/bin/env python3
"""
補跑腳本：
1. 場景 04 外燴定價 — 從現有 R1-R3 接續，補跑 R4-R5
2. 場景 05 Investment OS — 完整跑 5 輪
使用 claude CLI (claude-sonnet-4-6 + claude-opus-4-7)
"""

import subprocess
import os
import re
import time

BASE_DIR = "/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-R-FABLE-VS-OPUS-REAL-20260719"
FABLE_MODEL = "claude-sonnet-4-6"
OPUS_MODEL = "claude-opus-4-7"

REFINE_FABLE = """
治理準則精煉指令（Fable 視角）：
1. 批判上一輪你自己的推理：有哪些假設未驗證（準則③）？結論缺乏數字（準則⑤）？
2. 吸收 Opus 的洞察：哪個框架值得採納？哪些需落地轉化？
3. 精煉立場：具體行動、Who/When、W→SW→NW（準則⑧⑩⑪）。禁工具，純文字，200-400字。
"""

REFINE_OPUS = """
治理準則精煉指令（Opus 視角）：
1. 批判上一輪自己：哪些量化無依據（準則⑥）？哪些修症狀非根因（準則⑦）？
2. 吸收 Fable 落地方案：哪個前提值得質疑？哪些可直接認可？
3. 精煉立場：核心框架、關鍵盲點、Owner 決策洞察（準則⑨⑩）。禁工具，純文字，200-400字。
"""

SCENARIO_04 = {
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
}

SCENARIO_05 = {
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
}


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


def call_model(model_id, prompt, timeout=150):
    token = load_oauth_token()
    env = os.environ.copy()
    if token:
        env["CLAUDE_CODE_OAUTH_TOKEN"] = token
    try:
        result = subprocess.run(
            ["claude", "-p", "--model", model_id, prompt],
            capture_output=True, text=True, timeout=timeout, env=env,
        )
        if result.returncode != 0:
            return f"[ERROR] {result.stderr[:300]}"
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "[TIMEOUT]"
    except Exception as e:
        return f"[EXCEPTION] {str(e)}"


def build_round_prompt(initial_prompt, history, model_role, round_num):
    refine_instruction = REFINE_FABLE if model_role == "Fable" else REFINE_OPUS
    other_role = "Opus" if model_role == "Fable" else "Fable"
    parts = [f"【場景背景】{initial_prompt}\n"]
    for r in range(1, round_num):
        parts.append(f"\n--- 第 {r} 輪 {model_role} 視角 ---\n{history[r-1][model_role]}")
        parts.append(f"\n--- 第 {r} 輪 {other_role} 視角 ---\n{history[r-1][other_role]}")
    parts.append(f"\n\n【第 {round_num} 輪指令】{refine_instruction}")
    return "\n".join(parts)


def parse_existing_rounds(rounds_file):
    """Parse rounds 1-3 from existing rounds.md, return history list."""
    history = []
    try:
        with open(rounds_file, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        return history

    # Extract rounds 1-3
    for r in range(1, 4):
        # Find Fable section for this round
        fable_pattern = rf"## 第 {r} 輪\n\n### Fable 視角[^\n]*\n\n(.*?)(?=\n### Opus 視角)"
        opus_pattern = rf"### Opus 視角[^\n]*\n\n(.*?)(?=\n---\n)"

        fable_match = re.search(fable_pattern, content, re.DOTALL)
        opus_match = re.search(opus_pattern, content[content.find(f"## 第 {r} 輪"):], re.DOTALL)

        if fable_match and opus_match:
            fable_text = fable_match.group(1).strip()
            opus_text = opus_match.group(1).strip()
            history.append({"Fable": fable_text, "Opus": opus_text})
        else:
            print(f"  WARNING: Could not parse round {r}")

    return history


def repair_scenario04():
    scenario = SCENARIO_04
    scenario_dir = os.path.join(BASE_DIR, scenario["id"])
    rounds_file = os.path.join(scenario_dir, "rounds.md")

    print(f"\n{'='*60}")
    print(f"補跑場景: {scenario['name']} (R4-R5)")
    print(f"{'='*60}")

    # Parse existing rounds 1-3
    history = parse_existing_rounds(rounds_file)
    print(f"  已讀取 {len(history)} 輪歷史")

    if len(history) < 3:
        print(f"  ERROR: 只讀到 {len(history)} 輪，需要 3 輪。中止。")
        return []

    new_rounds = []
    for round_num in range(4, 6):
        print(f"\n  第 {round_num} 輪...")
        fable_prompt = build_round_prompt(scenario["initial_prompt"], history, "Fable", round_num)
        opus_prompt = build_round_prompt(scenario["initial_prompt"], history, "Opus", round_num)

        print(f"    Fable...", end="", flush=True)
        t0 = time.time()
        fable_response = call_model(FABLE_MODEL, fable_prompt)
        print(f" {time.time()-t0:.1f}s")

        print(f"    Opus...", end="", flush=True)
        t0 = time.time()
        opus_response = call_model(OPUS_MODEL, opus_prompt)
        print(f" {time.time()-t0:.1f}s")

        history.append({"Fable": fable_response, "Opus": opus_response})
        new_rounds.append((round_num, fable_response, opus_response))

    # Append rounds 4-5 to existing rounds.md
    with open(rounds_file, "a", encoding="utf-8") as f:
        for round_num, fable_r, opus_r in new_rounds:
            f.write(f"\n## 第 {round_num} 輪\n\n")
            f.write(f"### Fable 視角（claude-sonnet-4-6）\n\n{fable_r}\n\n")
            f.write(f"### Opus 視角（claude-opus-4-7）\n\n{opus_r}\n\n")
            f.write("---\n")

    print(f"\n  R4-R5 補完，已附加到 rounds.md")
    return history


def run_scenario05():
    scenario = SCENARIO_05
    scenario_dir = os.path.join(BASE_DIR, scenario["id"])
    rounds_file = os.path.join(scenario_dir, "rounds.md")
    summary_file = os.path.join(scenario_dir, "summary.md")

    print(f"\n{'='*60}")
    print(f"場景05: {scenario['name']}")
    print(f"{'='*60}")

    history = []
    rounds_content = [f"# {scenario['name']} — 5 輪真模型推理\n"]
    rounds_content.append("執行日期：2026-07-19")
    rounds_content.append("模型：Fable=claude-sonnet-4-6 | Opus=claude-opus-4-7（claude CLI）")
    rounds_content.append("任務代號：JOB-R-FABLE-VS-OPUS-REAL-20260719\n")
    rounds_content.append("---\n")

    for round_num in range(1, 6):
        print(f"\n  第 {round_num} 輪...")

        if round_num == 1:
            fable_prompt = scenario["initial_prompt"] + "\n\n【你是 Fable (claude-sonnet-4-6)：策略執行導向，優先設計可執行方案，輸出 W→SW→NW。純文字推理，禁工具，200-400字。】"
            opus_prompt = scenario["initial_prompt"] + "\n\n【你是 Opus (claude-opus-4-7)：深度推理導向，優先挑戰假設，標示不確定性，找根因。純文字推理，禁工具，200-400字。】"
        else:
            fable_prompt = build_round_prompt(scenario["initial_prompt"], history, "Fable", round_num)
            opus_prompt = build_round_prompt(scenario["initial_prompt"], history, "Opus", round_num)

        print(f"    Fable...", end="", flush=True)
        t0 = time.time()
        fable_response = call_model(FABLE_MODEL, fable_prompt)
        print(f" {time.time()-t0:.1f}s")

        print(f"    Opus...", end="", flush=True)
        t0 = time.time()
        opus_response = call_model(OPUS_MODEL, opus_prompt)
        print(f" {time.time()-t0:.1f}s")

        history.append({"Fable": fable_response, "Opus": opus_response})
        rounds_content.append(f"## 第 {round_num} 輪\n")
        rounds_content.append(f"### Fable 視角（claude-sonnet-4-6）\n\n{fable_response}\n")
        rounds_content.append(f"### Opus 視角（claude-opus-4-7）\n\n{opus_response}\n")
        rounds_content.append("---\n")

    with open(rounds_file, "w", encoding="utf-8") as f:
        f.write("\n".join(rounds_content))

    # Write placeholder summary
    summary_content = f"""# {scenario['name']} — 真模型對比摘要

執行日期：2026-07-19
模型：Fable=claude-sonnet-4-6 | Opus=claude-opus-4-7（claude CLI）

---

## 模型行為差異觀察

（A1 補充）

## 適合派工

（A1 補充）
"""
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary_content)

    print(f"\n  場景05完成")
    return history


if __name__ == "__main__":
    # Step 1: Repair scenario 04 rounds 4-5
    history04 = repair_scenario04()

    # Step 2: Run scenario 05
    history05 = run_scenario05()

    print("\n\n全部完成！")

#!/usr/bin/env python3
"""
GBP 照片評分腳本 — MAPLAB 2026maplab外燴紀錄
評分標準：食物特寫/擺盤/場地佈置/構圖清晰/避正面人臉/品牌質感
輸出：JSON 評分結果，供後續排名與報告生成
"""
import os, sys, json, subprocess, tempfile, base64, urllib.request, shutil

DRIVE_ROOT = "/Users/pagemacmini/Library/CloudStorage/GoogleDrive-pagewu1010@gmail.com/我的雲端硬碟/2026maplab外燴紀錄"
TARGET_FOLDERS = [
    "0702中興工程",
    "20260627東門教會證婚",
    "0621歡樂時光-性別派對",
    "20260621說事實木地板開幕",
    "20260614富信飯店-社工公會會議",
    "20260613遊艇氣泡水",
]
OUTPUT_DIR = "/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A4-GBP-PHOTO-20260710"
OLLAMA_URL = "http://localhost:11434/api/generate"
VISION_MODEL = "moondream:1.8b"
SCORE_MODEL = "qwen2.5:14b"

VISION_PROMPT = "Describe this photo in detail: what food is shown, how is it plated/arranged, what is the venue/table setup, how is the lighting and composition, are there any faces visible?"

SCORE_PROMPT_TPL = """你是 MAPLAB Kitchen 的 GBP（Google Business Profile）照片評分師。
根據以下照片描述，評估對 GBP 的適用性，使用繁體中文回答。

照片描述：{description}

評分標準（總分 10 分，各 2 分）：
1. food_display：食物/擺盤是否清晰可見精緻（0-2）
2. venue_setup：是否展示活動場地佈置（0-2）
3. composition：構圖清晰、光線良好（0-2）
4. brand_quality：是否呈現專業溫暖細緻感（0-2）
5. no_face_penalty：若有清晰正面人臉扣2分（0 or -2）

只回答JSON，不要其他文字：
{{
  "total_score": <整數>,
  "food_display": <0-2>,
  "venue_setup": <0-2>,
  "composition": <0-2>,
  "brand_quality": <0-2>,
  "no_face_penalty": <0 or -2>,
  "description": "<一句話繁體中文描述>",
  "gbp_suitable": <true/false, 6分以上true>,
  "wp1992_candidate": <true/false, 適合企業茶會/會議場景則true>
}}"""


def heic_to_jpeg(heic_path, tmpdir):
    """Convert HEIC to JPEG using sips (macOS built-in)"""
    basename = os.path.splitext(os.path.basename(heic_path))[0]
    out_path = os.path.join(tmpdir, basename + ".jpg")
    result = subprocess.run(
        ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "60",
         "--resampleHeightWidthMax", "800", heic_path, "--out", out_path],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0 and os.path.exists(out_path):
        return out_path
    return None


def _ollama_call(model, prompt, img_b64=None, timeout=90, num_predict=300):
    payload = {"model": model, "prompt": prompt, "stream": False,
               "options": {"temperature": 0.1, "num_predict": num_predict}}
    if img_b64:
        payload["images"] = [img_b64]
    req = urllib.request.Request(
        OLLAMA_URL, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read()).get("response", "")


def score_image(img_path):
    """Two-step: moondream describes → qwen2.5 scores as JSON"""
    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    try:
        description = _ollama_call(VISION_MODEL, VISION_PROMPT, img_b64=img_b64, timeout=60, num_predict=200)
        if not description.strip():
            return None
    except Exception as e:
        print(f"  [vision err] {e}", file=sys.stderr)
        return None

    try:
        score_prompt = SCORE_PROMPT_TPL.format(description=description.strip())
        score_text = _ollama_call(SCORE_MODEL, score_prompt, timeout=60, num_predict=300)
        start = score_text.find("{")
        end = score_text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(score_text[start:end])
    except Exception as e:
        print(f"  [score err] {e}", file=sys.stderr)
    return None


def main():
    results = []
    tmpdir = tempfile.mkdtemp(prefix="gbp_scorer_")

    try:
        for folder_name in TARGET_FOLDERS:
            folder_path = os.path.join(DRIVE_ROOT, folder_name)
            if not os.path.isdir(folder_path):
                print(f"[SKIP] {folder_name}: folder not found")
                continue

            imgs = [f for f in os.listdir(folder_path)
                    if f.lower().endswith(('.jpg', '.jpeg', '.heic', '.png'))]

            if not imgs:
                print(f"[SKIP] {folder_name}: no images (Drive may not be synced)")
                continue

            # Sample if >100 images
            if len(imgs) > 100:
                import random; random.seed(42)
                sample = random.sample(imgs, 50)
                print(f"[{folder_name}] {len(imgs)} 張 → 抽樣 50 張")
            else:
                sample = imgs
                print(f"[{folder_name}] {len(imgs)} 張 全評")

            for fname in sample:
                orig_path = os.path.join(folder_path, fname)
                print(f"  評分: {fname}...", end="", flush=True)

                # Convert HEIC if needed
                if fname.lower().endswith('.heic'):
                    img_path = heic_to_jpeg(orig_path, tmpdir)
                    if not img_path:
                        print(f" [CONV FAIL]")
                        continue
                else:
                    img_path = orig_path

                score = score_image(img_path)
                if score:
                    score["file"] = fname
                    score["folder"] = folder_name
                    score["local_path"] = orig_path
                    results.append(score)
                    print(f" {score.get('total_score', '?')}/10 — {score.get('description', '')[:50]}")
                else:
                    print(f" [SCORE FAIL]")

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    # Sort by total_score desc
    results.sort(key=lambda x: x.get("total_score", 0), reverse=True)

    # Save full results
    out_json = os.path.join(OUTPUT_DIR, "gbp_scores_raw.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n全部結果已存：{out_json}")
    print(f"共評 {len(results)} 張，Top 20：")
    for i, r in enumerate(results[:20], 1):
        print(f"  {i:2}. [{r['folder']}] {r['file']} — {r.get('total_score', '?')}/10 — {r.get('description', '')[:60]}")


if __name__ == "__main__":
    main()

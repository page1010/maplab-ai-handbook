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

PROMPT = """你是 MAPLAB Kitchen 的 GBP（Google Business Profile）照片評分師。
請評估這張照片對 GBP 的適用性，使用繁體中文回答。

評分標準（總分 10 分，各 2 分）：
1. 食物特寫/擺盤：食物是否清晰可見、擺盤精緻
2. 場地佈置：是否展示活動場地、桌面布置
3. 構圖清晰：照片是否清晰、光線良好、角度佳
4. 品牌質感：是否呈現 MAPLAB 的專業、溫暖、細緻感
5. 無正面人臉：扣分如果有清晰正面人臉（背影/側臉OK）

請回答格式（JSON）：
{
  "total_score": <0-10的整數>,
  "food_display": <0-2>,
  "venue_setup": <0-2>,
  "composition": <0-2>,
  "brand_quality": <0-2>,
  "no_face_penalty": <0 or -2>,
  "description": "<一句話描述照片主要內容>",
  "gbp_suitable": <true/false>,
  "wp1992_candidate": <true/false, 若適合企業茶會/會議場景則true>
}
只回答JSON，不要其他文字。"""


def heic_to_jpeg(heic_path, tmpdir):
    """Convert HEIC to JPEG using sips (macOS built-in)"""
    basename = os.path.splitext(os.path.basename(heic_path))[0]
    out_path = os.path.join(tmpdir, basename + ".jpg")
    result = subprocess.run(
        ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "60",
         "--resampleLongSide", "800", heic_path, "--out", out_path],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0 and os.path.exists(out_path):
        return out_path
    return None


def score_image(img_path):
    """Send image to Ollama gemma4 for GBP scoring"""
    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    payload = {
        "model": "gemma4:latest",
        "prompt": PROMPT,
        "images": [img_b64],
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 256}
    }
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            response_text = result.get("response", "")
            # Extract JSON from response
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response_text[start:end])
    except Exception as e:
        print(f"  Error scoring {img_path}: {e}", file=sys.stderr)
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

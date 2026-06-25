#!/usr/bin/env python3
"""Incremental Video Checklist Updater

Scans a Google Drive folder (via a manifest JSON file) and updates:
  - checklist/videos.json   : metadata + version history for each video
  - checklist/rubric.md    : aggregated common issues

Usage:
  python3 scripts/update_checklist.py --manifest <path/to/drive_manifest.json>

The manifest JSON must be an array of objects, each containing:
  {
    "name": "filename.mp4",
    "id": "<drive_file_id>",
    "modifiedTime": "2026-06-21T15:32:10Z",
    "webViewLink": "https://drive.google.com/file/d/<id>/view"
  }
"""
import argparse, json, os, sys, datetime, collections
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
CHECKLIST_DIR = BASE_DIR / "checklist"
VIDEOS_JSON = CHECKLIST_DIR / "videos.json"
RUBRIC_MD = CHECKLIST_DIR / "rubric.md"

def load_videos():
    if VIDEOS_JSON.exists():
        with open(VIDEOS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"videos": []}

def save_videos(data):
    with open(VIDEOS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_manifest(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def find_video_record(videos, name):
    for rec in videos:
        if rec["filename"] == name:
            return rec
    return None

def update_videos(manifest, existing):
    updated = 0
    added = 0
    for item in manifest:
        name = item.get("name")
        link = item.get("webViewLink")
        mod_time = item.get("modifiedTime")
        if not name or not link:
            continue
        rec = find_video_record(existing["videos"], name)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        if rec is None:
            # new video
            rec = {
                "filename": name,
                "versions": [
                    {
                        "version": 1,
                        "date": today,
                        "status": "completed",
                        "notes": "initial upload",
                        "link": link
                    }
                ],
                "current_version": 1
            }
            existing["videos"].append(rec)
            added += 1
        else:
            # check if newer
            last_version = rec["versions"][-1]
            last_date_str = last_version.get("date")
            # use modifiedTime as proxy for newer
            last_mod = last_version.get("link")
            # if the link differs we assume an update (simple heuristic)
            if link != last_version.get("link"):
                new_version = {
                    "version": last_version["version"] + 1,
                    "date": today,
                    "status": "revised",
                    "notes": "auto‑detected update",
                    "link": link
                }
                rec["versions"].append(new_version)
                rec["current_version"] = new_version["version"]
                updated += 1
    return added, updated

def generate_rubric(videos):
    # collect all notes
    notes_counter = collections.Counter()
    for rec in videos["videos"]:
        for v in rec["versions"]:
            note = v.get("notes", "").lower()
            # simple token split by punctuation/space
            for token in note.split():
                notes_counter[token] += 1
    # keep tokens that appear >=2 times and are not trivial
    common = [tok for tok, cnt in notes_counter.items() if cnt >= 2 and len(tok) > 3]
    with open(RUBRIC_MD, "w", encoding="utf-8") as f:
        f.write("# 影片製作 Checklist / Rubric\n\n")
        f.write("## 常見問題 (自動萃取)\n\n")
        if common:
            for tok in sorted(common):
                f.write(f"- {tok}\n")
        else:
            f.write("_目前無足夠的重複筆記，可稍後再觀察_\n")
        f.write("\n## 建議做法\n\n- 在每次修正後手動填寫 `notes`，以便系統自動彙整。\n")

def ensure_structure():
    CHECKLIST_DIR.mkdir(parents=True, exist_ok=True)
    if not VIDEOS_JSON.exists():
        with open(VIDEOS_JSON, "w", encoding="utf-8") as f:
            json.dump({"videos": []}, f, ensure_ascii=False, indent=2)
    if not RUBRIC_MD.exists():
        RUBRIC_MD.write_text("# 影片製作 Checklist / Rubric\n\n待產生\n", encoding="utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, help="Path to Drive manifest JSON file")
    args = parser.parse_args()
    ensure_structure()
    existing = load_videos()
    manifest = load_manifest(args.manifest)
    added, updated = update_videos(manifest, existing)
    save_videos(existing)
    generate_rubric(existing)
    print(json.dumps({
        "summary": {
            "total_videos": len(existing["videos"]),
            "added": added,
            "updated": updated
        }
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

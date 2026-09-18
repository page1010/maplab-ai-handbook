#!/usr/bin/env python3
"""Build a private, evidence-labelled photo handoff. No network or original writes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
from urllib.parse import quote


JOINS = {
    "N001": "quote-2026-09-16-afternoon-180",
    "H002": "quote-2025-11-22-main-25-servings",
    "H005": "quote-2025-11-26-amd-240",
    "H004": "quote-2025-02-08-main-25",
}
YEAR_INFERENCES = {
    "H002": {"year": 2025, "basis": "11/22（六）與2025日曆一致；2025分類桶、11/22主食25份及180×90桌面候選報價一致。不是原檔日期證明。"},
    "H004": {"year": 2025, "basis": "2/8（六）與2025日曆一致；2025分類桶、2/8主食25份候選報價一致。不是原檔日期證明。"},
    "H005": {"year": 2025, "basis": "2025分類桶與2025/11/26 AMD開幕、240件候選報價一致。仍缺獨立案件鍵或原檔日期。"},
}
LABELS = {
    "gold-wire-round-riser": "金線圓形高低展示台",
    "gold-ring-three-tier": "金色圓環多層架",
    "white-round-pedestal": "白色單柱圓台",
    "black-singlebite-dish": "黑色單口小碟",
    "clear-singlebite-cup": "透明單口杯",
    "wood-vertical-display": "直立木展示板",
    "log-round-riser": "原木圓形增高台",
    "woven-basket": "藤編籃",
    "white-rectangular-dish": "白色長方深盤",
    "white-wood-crate": "白色木箱展示架",
    "gold-frame-long-tray": "金框長托盤",
    "gold-footed-dish": "金色高腳盤",
    "cream-scalloped-plate": "奶油色波浪盤",
    "flower-vase": "花器與花藝",
    "rectangular-gold-riser": "金色長方展示台",
    "gold-long-platter": "金色長盤",
    "hex-donut-rack": "六角甜甜圈架",
    "deep-round-bowl": "深圓碗",
    "white-long-platter": "白色長盤",
    "wood-long-riser": "木質長形增高台",
    "cross-frame-riser": "交叉支架增高台",
    "wood-handle-tray": "有把手木托盤",
    "gold-geometric-tray": "金色幾何托盤",
    "ornate-oval-tray": "雕花橢圓托盤",
    "ornate-square-riser": "雕花方形增高台",
    "gold-perforated-tray": "金色鏤空托盤",
    "rectangular-three-tier": "長方多層架",
    "white-singlebite-spoon": "白色單口湯匙皿",
    "white-oval-bowl": "白色橢圓碗",
    "white-round-platter": "白色圓盤",
    "wood-crate": "原木箱架",
    "wood-long-platter": "木質長盤",
    "white-small-bowl": "白色小碗",
    "white-two-tier": "白色雙層架",
    "wood-black-pedestal": "木面黑腳台",
    "wood-house-display": "木製屋形展示架",
    "white-rectangular-platter": "白色長方淺盤",
    "white-oval-platter": "白色橢圓淺盤",
    "gold-frame-rectangular-riser": "金框長方台（待與歷史分類去重）",
    "white-stair-riser": "白色階梯架",
    "wood-rectangular-tray": "木質長方托盤",
    "gold-leaf-tray": "金色葉形盤",
    "gold-wire-tray": "金色框網盤",
    "floral-vase": "花器與花藝（待與歷史分類去重）",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.exists() and path.read_text(encoding="utf-8") == text:
        path.chmod(0o600)
        return
    fd, tmp = tempfile.mkstemp(prefix=".prelayout-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
        path.chmod(0o600)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def write_json(path, value):
    atomic_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def inside(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Collection path escapes private root")
    return path


def capture_label(photo):
    if photo.get("capture_time"):
        return f"EXIF：{photo['capture_time']}；時區 {photo.get('capture_timezone', 'UNKNOWN')}"
    album_date = photo.get("date_evidence", {}).get("google_photos_displayed_datetime")
    if album_date:
        return f"Google Photos：{album_date}（非已下載原檔 EXIF）"
    return f"年份待核；分類桶 {photo.get('source_year_bucket', '未知')} 不是拍攝證據"


def link(path, label):
    return f"[{label}]({quote(str(path), safe=':/#?=&%')})"


def verify_photos(root, photos):
    ids, hashes, originals_checked = set(), set(), 0
    for photo in photos:
        if photo["id"] in ids:
            raise ValueError("Duplicate photo ID")
        ids.add(photo["id"])
        path = inside(root, photo["local_relative_path"])
        digest = sha(path)
        if digest != photo["sha256"] or path.stat().st_size != photo["byte_size"]:
            raise ValueError(f"Photo integrity mismatch: {photo['id']}")
        if digest in hashes:
            raise ValueError("Duplicate primary photo bytes")
        hashes.add(digest)
        if path.stat().st_mode & 0o777 != 0o600:
            raise ValueError(f"Private mode mismatch: {photo['id']}")
        source = Path(photo["source_path"])
        if source.exists():
            if sha(source) != digest:
                raise ValueError(f"Source copy mismatch: {photo['id']}")
            originals_checked += 1
        for variant in photo.get("variants", []):
            variant_path = inside(root, variant["local_relative_path"])
            if sha(variant_path) != variant["sha256"]:
                raise ValueError("Variant hash mismatch")
            if variant_path.stat().st_mode & 0o777 != 0o600:
                raise ValueError("Variant private mode mismatch")
    return originals_checked


def build(root):
    root = root.resolve()
    inputs = [root / "資料" / name for name in
              ("historical-photos.json", "current-photo.json", "quotes.json")]
    history, current, quote_data = map(read_json, inputs)
    photos = history["photos"] + current["photos"]
    quotes = {q["local_evidence_id"]: q for q in quote_data["quotes"]}
    source_count = verify_photos(root, photos)
    for q in quotes.values():
        assert q["photo_join_status"] == "CANDIDATE_INFERENCE_NOT_CONFIRMED"
        if q.get("menu_quantity_sum_matches_declared"):
            assert sum(m["quantity"] for m in q["menu"]) == q["total_food_pieces"]["value"]

    families = {}
    for photo in photos:
        for family in photo["catalog_family_ids"]:
            families.setdefault(family, []).append(photo["id"])
        q = quotes.get(JOINS.get(photo["id"]))
        photo["quote_candidate_id"] = q["local_evidence_id"] if q else None
        photo["quote_join_status"] = "CANDIDATE_INFERENCE_NOT_CONFIRMED" if q else "NO_CANDIDATE"
        photo["year_inference"] = YEAR_INFERENCES.get(photo["id"])
        img = inside(root, photo["local_relative_path"])
        details = [f"# {photo['id']} · {photo['title']}", "",
                   link(img.name, "開啟照片"), "", f"![照片]({quote(img.name)})", "",
                   "## 已觀察與日期依據", "", f"- 拍攝時間：{capture_label(photo)}",
                   f"- 照片原文：{'；'.join(photo['date_evidence'].get('visible_overlay', [])) or '無可用日期字樣'}",
                   "- 活動日期和拍攝日期分開；未經案件核對，不把活動文字提升為確定日期。",
                   f"- 檔案層級：{photo['source_variant']}",
                   f"- 視覺說明：{photo['visual_description']}", "",
                   "## 報價單對照", ""]
        if photo["year_inference"]:
            inference = photo["year_inference"]
            details += [f"推定年份：{inference['year']}，未確認。{inference['basis']}", ""]
        if q:
            details += [f"候選，尚未確認同案：{link(q['source_url'], q['source_title'])}", "",
                        f"報價單明載活動日期：{q['event_date']}。此日期不能代替照片原始時間。",
                        "逐品餐點、人數／份數／總件數、桌面原文與衝突見[核對摘要](../資料/核對摘要.md)。"]
        else:
            details += ["尚無核對上的報價單；不得用照片中的數字自動當人數、尺寸或庫存。"]
        details += ["", "## 器具線索", "",
                    *[f"- {LABELS.get(f, f)}（{f}）" for f in photo["catalog_family_ids"]],
                    "", "以上是視覺分類，不是已量測 SKU。每種長寬高、數量、可盛餐點件數均待確認。", "",
                    "## 來源與可重現性", "",
                    f"- 來源：`{photo['source_path']}`",
                    f"- 檔案 SHA-256：`{photo['sha256']}`",
                    f"- 位元組：{photo['byte_size']}",
                    "- 本檔為新整理副本；上游檔案未改名、未移動、未刪除。"]
        if photo.get("source_url"):
            details += [f"- 相簿：{link(photo['source_url'], 'Mina Google Photos 原項目')}"]
        details += ["", "## 尚缺資料", "",
                    *[f"- {field}" for field in photo["missing_fields"]], ""]
        atomic_text(img.with_suffix(".md"), "\n".join(details))

    catalog = {"status": "VISUAL_FAMILIES_NOT_MEASURED_INVENTORY", "families": [
        {"family_id": family, "name": LABELS.get(family, family), "photo_ids": refs,
         "physical_inventory_id": None, "width_cm": None, "depth_cm": None,
         "height_cm": None, "current_stock_count": None, "food_capacity": None,
         "confidence": "VISUAL_ONLY", "simulation_fit_eligible": False}
        for family, refs in sorted(families.items())]}
    write_json(root / "資料/equipment-candidates.json", catalog)
    write_json(root / "資料/collection.json", {
        "scope": "FIRST_VERIFIED_BATCH_NOT_EXHAUSTIVE", "photos": photos,
        "input_sha256": {p.name: sha(p) for p in inputs},
        "coverage": history["unscanned_coverage"],
        "quote_joins": "All candidate; no confirmed case identity"})
    table = ["# 器具量測與去重清單", "",
             "先對照照片確認是否同一器具，再填尺寸。歷史照片只證明當時出現，不證明現在庫存。",
             "量測底座最大占地、上層最大伸出、總高、多層可用層面、每道食品實測容量。",
             "金框長方台／金色長方展示台、兩個花器分類可能同類；未核對前不自動合併。", "",
             "| 視覺類型 | 照片 ID | 確認器具 ID | 底座寬×深 cm | 最大伸出 cm | 高 cm | 現有數量 | 餐點/容量 |",
             "|---|---|---|---|---|---|---|---|"]
    table += [f"| {LABELS.get(f, f)} | {', '.join(refs)} | 待核 | 待量 | 待量 | 待量 | 待盤 | 待測 |"
              for f, refs in sorted(families.items())]
    atomic_text(root / "器具量測清單.md", "\n".join(table) + "\n")
    readme = ["# MAPLAB 外燴預擺資料包", "",
              "第一批已整理，2026-09-18。11 張預擺／器皿配置照片集中在「照片」，1 張特寫在「器具參考」。",
              "每張旁邊的同名 .md 是日期依據、來源、器具說明、候選報價與缺口；原始相簿和上游檔案保持不動。", "",
              "## 先看這些", "",
              "- [四案餐點／份數／桌面核對摘要](資料/核對摘要.md)",
              "- [器具量測與去重清單](器具量測清單.md)",
              "- [完整機器可讀索引](資料/collection.json)", "",
              "## 照片索引", "",
              "| ID | 照片與細節 | 拍攝日期依據 | 報價對應 |",
              "|---|---|---|---|"]
    for photo in sorted(photos, key=lambda p: (p["id"] != "N001", p["id"])):
        p = Path(photo["local_relative_path"])
        readme.append(f"| {photo['id']} | {link(p, photo['title'])} · {link(p.with_suffix('.md'), '細節')} | {capture_label(photo)} | {'候選，未確認' if JOINS.get(photo['id']) else '未核對'} |")
    readme += ["", "## 已確認與未確認", "",
               "- 四張歷史照片有 EXIF 日期；七張仍只有分類桶或文字線索。N001 的 2026/9/15 來自 Google Photos 實際頁面，尚非本地原檔 EXIF。",
               "- 其中 H002／H004／H005 可推定為2025年：分類桶、活動日期／星期、餐點或桌面線索與候選報價相容；此推定另列，未混進已核日期。",
               "- N001 使用者提供副本與相簿頁面影像已比對；原檔下載未成功。本地同名 IMG_3327.JPG 是不同圖片，已排除。",
               "- 四份報價單已讀回，但照片與報價之間仍是候選關聯，未找到獨立案件鍵。不得把候選人數寫進已確認檔名。",
               "- 180／240 是候選報價單的點心總件數。25 可能是每道規劃份數，不能都當人數。",
               "- 桌長寬依原文保留，未列單位就不補 cm；照片透視、商品截圖及擺放數量不能代替實測尺寸、庫存與食品容量。", "",
               "## 命名與年份規則", "",
               "1. 先核對圖片本身、像素與來源；相機檔名會重複，不能當唯一 ID。",
               "2. 檔案 EXIF DateTimeOriginal 優先，時區缺失保持 UNKNOWN；Google Photos 日期另列，不混成 EXIF。",
               "3. 分清拍攝日期、圖片上活動日期、報價單活動日期、檔案修改時間。資料夾年份不是拍攝證據。",
               "4. 沒年份就標年份待核；用月份、星期、活動類型、餐點、份數和桌面交叉核對，但推定仍標推定。",
               "5. H 系列保留的是歷史已改名素材檔名，不冒稱相機原始檔名。相同 SHA 不重複收錄；只改新副本名稱。", "",
               "## 收集涵蓋與下一步", "",
               "- 已收：歷史逐張目視 11 份 + 本次範例 1 份；相簿頁面縮圖另作證據，不重複計張。",
               "- 未完成：June–July 2026 備份已有 472 份檔案清單（未去重、未逐張檢視）；Mina 完整相簿未全庫掃描。不能宣稱已收齊。",
               "- 下一步：按近期活動夾逐批篩出空器皿預擺，再查原檔／Takeout sidecar 時間；優先補 H002/H004/H005 的日期與案件關聯。",
               "- 模擬器下一步：從重複出現的金環架、金線圓台、白木箱、白色圓台量測起；未量測前可做示意，不可宣稱桌面放得下。",
               "- 尺寸、庫存、清洗／運輸、同日跨場調度須分開。H007 可作跨場補器皿的案例。", "",
               "## 後續接手", "",
               "先讀本檔、同名照片說明與核對摘要；不要重新把180當人數、不要依同名IMG配圖，也不要把所有視覺分類當獨立SKU。",
               "資料僅存本機私有資料夾，不寄送到 OpenRouter／DeerFlow，不改動相簿、不發送客戶訊息。",
               "接續任務卡：[T-A4-PRELAYOUT-SIMULATOR-001](/Users/pagemacmini/maplab-ai-handbook/handoff/tasks/T-A4-PRELAYOUT-SIMULATOR-001.md)。", ""]
    atomic_text(root / "README.md", "\n".join(readme))
    receipt = {"status": "PASS", "primary_photos": len(photos),
               "prelayout_photos": sum(p["kind"] == "prelayout_photo" for p in photos),
               "equipment_references": sum(p["kind"] == "equipment_reference" for p in photos),
               "source_copy_hash_matches": source_count,
               "exif_dated_photos": sum(bool(p.get("capture_time")) for p in photos),
               "album_dated_photos": sum(bool(p.get("date_evidence", {}).get("google_photos_displayed_datetime")) for p in photos),
               "candidate_quote_count": len(quotes), "confirmed_photo_quote_joins": 0,
               "visual_family_labels_not_stock_items": len(families),
               "measured_equipment_count": 0, "input_sha256": {p.name: sha(p) for p in inputs}}
    write_json(root / "資料/verification.json", receipt)
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.root), ensure_ascii=False, indent=2))

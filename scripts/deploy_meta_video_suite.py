#!/usr/bin/env python3
"""
deploy_meta_video_suite.py — 將 YouTube/桌面的 10 檔高轉化 15 秒實拍影片全面部屬至 Meta Ads
================================================================================
1. 上傳 V01~V10 (9:16 直式短影音) 至 Meta Ads 廣告帳號 (act_318634712)
2. 輪詢確認 Meta 伺服器端解碼轉檔完成 (video_status == 'ready')
3. 取得高解析度縮圖 URI，依受眾痛點生成各檔專屬文案之 AdCreative (帶完整 UTM 參數)
4. 將新影片廣告全面加入對應的廣告組，全開投產
5. 執行「廣告直接拆預算」：將總日預算重分配為 590 TWD/日 (嚴格低於 616 TWD 上限)，
   重點傾斜至高客單企業/公關/展會旺季
6. 驗證並回讀全部 AdSet 與 Ad 的最新 LIVE 狀態，產出報表
"""

import os
import sys
import json
import re
import time
import urllib.request
import urllib.parse

ENVF = "/Users/pagemacmini/maplab-ai-handbook/bot/.env"
ACT = "act_318634712"
PAGE_ID = "853241761521717"
GRAPH_BASE = "https://graph.facebook.com/v21.0"
VIDEO_BASE = "https://graph-video.facebook.com/v21.0"
DESKTOP_DIR = "/Users/pagemacmini/Desktop/Meta廣告素材_十案整理"
UTM_TEMPLATE = "utm_source=facebook&utm_medium=paid&utm_campaign={{campaign.name}}&utm_content={{ad.name}}"

def get_token():
    with open(ENVF) as f:
        for line in f:
            m = re.match(r"^META_ADS_TOKEN=(.+)$", line.strip())
            if m:
                return m.group(1)
    raise SystemExit("no-token-in-env")

TOK = get_token()

def get(path, params=None):
    p = dict(params or {})
    p["access_token"] = TOK
    url = f"{GRAPH_BASE}/{path}?" + urllib.parse.urlencode(p)
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500].replace(TOK, "<TOKEN>")
        return e.code, {"error_body": body}
    except Exception as e:
        return 500, {"error": str(e)}

def post(path, params):
    p = dict(params)
    p["access_token"] = TOK
    data = urllib.parse.urlencode(p).encode()
    req = urllib.request.Request(f"{GRAPH_BASE}/{path}", data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500].replace(TOK, "<TOKEN>")
        return e.code, {"error_body": body}
    except Exception as e:
        return 500, {"error": str(e)}

def upload_video_file(file_path, title):
    url = f"{VIDEO_BASE}/{ACT}/advideos"
    boundary = f"----WebKitFormBoundary{int(time.time()*1000)}"
    
    with open(file_path, "rb") as f:
        video_bytes = f.read()
    
    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(b'Content-Disposition: form-data; name="access_token"\r\n\r\n')
    body.extend(TOK.encode() + b"\r\n")
    
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(b'Content-Disposition: form-data; name="title"\r\n\r\n')
    body.extend(title.encode("utf-8") + b"\r\n")
    
    filename = os.path.basename(file_path)
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="source"; filename="{filename}"\r\n'.encode())
    body.extend(b"Content-Type: video/mp4\r\n\r\n")
    body.extend(video_bytes + b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode())
    
    req = urllib.request.Request(url, data=bytes(body), method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            res = json.loads(r.read().decode())
            return res.get("id")
    except urllib.error.HTTPError as e:
        print(f"❌ 上傳失敗: {e.read().decode()[:300].replace(TOK, '<TOKEN>')}")
        return None
    except Exception as e:
        print(f"❌ 上傳例外: {e}")
        return None

# 完整 10 檔影片規格與精準受眾投放配置
CAMPAIGN_CONFIGS = [
    {
        "id": "V01",
        "file": "maplab_V01_Zhuazhou_15s_9x16_MK-001.mp4",
        "target_adset": "52726886828730", # V1週歲影片
        "ad_name": "MAPLAB 14 V01週歲抓周15s實拍影片 (MK-001)",
        "headline": "台南抓周外燴・一手抱娃一手吃飽",
        "message": "辦抓周親友都在拍照，只有媽媽整天沒吃一口飯？\nMAPLAB Kitchen 專屬台南外燴，一手抱孩子一手拿得動，不必放孩子也能優雅吃飽，長輩稱讚、氛圍感直接拉滿！\n\n・檔期預約與精緻菜單：https://www.maplabkitchen.com/"
    },
    {
        "id": "V02",
        "file": "maplab_V02_Wedding_15s_9x16_MK-002.mp4",
        "target_adset": "52726886668930", # TA-2婚禮冷層
        "ad_name": "MAPLAB 15 V02浪漫證婚15s實拍影片 (MK-002)",
        "headline": "台南戶外婚禮外燴・新人優雅不餓肚子",
        "message": "證婚結束新人第一句話是：「好餓，剛剛吃了什麼？」\nMAPLAB Kitchen 不沾唇膏、不掉粉屑，一口優雅飽足，親友舉杯祝福的夢想婚禮。\n\n・檔期預約與精緻菜單：https://www.maplabkitchen.com/"
    },
    {
        "id": "V03",
        "file": "maplab_V03_TechCorporate_15s_9x16_MK-003.mp4",
        "target_adset": "52726886708930", # TA-3HR茶會冷層
        "ad_name": "MAPLAB 16 V03企業南科15s實拍影片 (MK-003)",
        "headline": "南科商務茶會外燴・主管說隨便訂但要體面",
        "message": "「吃麥當勞如何？」福委群組一片死寂。主管說隨便訂但絕不能隨便！\n告別冷便當！松露厚蛋、迷你黑牛堡，連工程師都停下鍵盤，主管稱讚有品味。\n\n・企業商務外燴預約：https://www.maplabkitchen.com/"
    },
    {
        "id": "V04",
        "file": "maplab_V04_StoreOpening_15s_9x16_MK-004.mp4",
        "existing_video_id": "1378090934063959",
        "existing_creative_id": "1685520889661645",
        "target_adset": "52726886720930", # B4公關開幕冷層
        "ad_name": "MAPLAB 17 V04門市開幕15s實拍影片 (MK-004)",
        "headline": "品牌門市開幕外燴・法式一口甜點桌",
        "message": "花兩百萬裝潢新門市，開幕茶會你真的打算叫大披薩滴油在木地板上？\nMAPLAB Kitchen 專屬台南外燴，法式一口小點、精緻擺盤，幫妳把品牌面子做足！\n\n・門市開幕檔期諮詢：https://www.maplabkitchen.com/"
    },
    {
        "id": "V05",
        "file": "maplab_V05_MansionVIP_15s_9x16_MK-005.mp4",
        "target_adset": "52726886778130", # 建商案場活動冷層
        "ad_name": "MAPLAB 18 V05建商案場15s實拍影片 (MK-005)",
        "headline": "頂級接待中心VIP外燴・奢華低調品味",
        "message": "接待億級豪宅買家，茶點若用普通餐盒，整個格局都掉了！\nMAPLAB Kitchen 專屬建商 VIP 招待外燴，當季頂級食材，讓客戶在味蕾上感受低調奢華。\n\n・建商案場活動洽詢：https://www.maplabkitchen.com/"
    },
    {
        "id": "V06",
        "file": "maplab_V06_GenderReveal_15s_9x16_MK-006.mp4",
        "target_adset": "52726886656930", # TA-1週歲溫層-P0輪替
        "ad_name": "MAPLAB 21 V06性別揭曉15s實拍影片 (MK-006)",
        "headline": "寶寶性別揭曉派對・浪漫驚喜外燴",
        "message": "藍色還是粉紅色？戳破氣球那刻，連甜點都在為妳揭曉幸福！\nMAPLAB Kitchen 寶寶性別揭曉專屬甜點桌，高顏值粉藍雙色法式小點，親友歡呼不斷！\n\n・性別派對預約洽詢：https://www.maplabkitchen.com/"
    },
    {
        "id": "V07",
        "file": "maplab_V07_FamilyFeast_15s_9x16_MK-007.mp4",
        "target_adset": "52726886800730", # C2入厝派對冷層
        "ad_name": "MAPLAB 19 V07家庭聚會15s實拍影片 (MK-007)",
        "headline": "家庭聚會入厝外燴・放過媽媽整桌送到府",
        "message": "今年親友聚會，媽媽說「隨便煮幾道家常菜就好」……大家心裡其實都在暗自發抖！\n今年放過媽媽，整桌精緻外燴直接送到府！媽媽坐下來喝熱茶，全家都輕鬆。\n\n・入厝與私廚到府預約：https://www.maplabkitchen.com/"
    },
    {
        "id": "V08",
        "file": "maplab_V08_ArtCurator_15s_9x16_MK-008.mp4",
        "target_adset": "52726886734930", # B5研討會會議冷層
        "ad_name": "MAPLAB 20 V08藝文展會15s實拍影片 (MK-008)",
        "headline": "藝文展覽國際論壇茶點・美學延伸的幾何茶點",
        "message": "設計展覽辦國際交流論壇，桌上若擺著傳統便當餐盒，整個展覽都哭了。\n食物本身就是展覽美學的延伸！台南當季食材化身幾何極簡藝術品。\n\n・學術會議與展覽茶點諮詢：https://www.maplabkitchen.com/"
    },
    {
        "id": "V09",
        "file": "maplab_V09_PartyAfterparty_15s_9x16_MK-009.mp4",
        "target_adset": "52726886540530", # C3壽宴冷層 / 私人派對
        "ad_name": "MAPLAB 22 V09私人派對15s實拍影片 (MK-009)",
        "headline": "私人派對慶生外燴・奢華微醺調酒吧台",
        "message": "歡聚慶生、年度私人派對，音樂響起，杯觥交錯！\nMAPLAB Kitchen 專屬外燴酒吧與精緻 Finger Food，無拘無束的味覺狂歡，為今夜刻下難忘回憶。\n\n・私人派對與調酒吧預約：https://www.maplabkitchen.com/"
    },
    {
        "id": "V10",
        "file": "maplab_V10_PicnicSnacks_15s_9x16_MK-010.mp4",
        "target_adset": "52644997254930", # 策略一-冷受眾-台南高雄25-40歲媽媽 (舊0504)
        "ad_name": "MAPLAB 23 V10野餐外帶15s實拍影片 (MK-010)",
        "headline": "台南頂級戶外野餐餐盒・法式一口甜鹹點",
        "message": "陽光、草地、微風！戶外聚會不用再狼狽打包塑膠袋。\nMAPLAB Kitchen 專屬精緻外帶餐盒，法式手工鹹派、一口馬卡龍，輕鬆提著走，隨處都是妳的私廚野餐。\n\n・戶外餐盒預訂：https://www.maplabkitchen.com/"
    }
]

# 590 TWD / 日 預算配置表 (全帳號日上限 616 TWD，安全保留 26 TWD 餘裕)
BUDGET_UPDATES = [
    ("52726886720930", 80, "B4公關開幕 (V04 秋季門市開幕旺季首選)"),
    ("52726886734930", 80, "B5研討會 (V08 開學研討會國際論壇)"),
    ("52726886708930", 70, "TA-3HR企業茶會 (V03 南科高客單主力)"),
    ("52726886828730", 58, "V1週歲影片 (V01 抓周影片主力)"),
    ("52726886668930", 58, "TA-2婚禮冷層 (V02 年底婚禮黃金檔期)"),
    ("52726886778130", 58, "建商案場VIP (V05 頂級案場招待)"),
    ("52726886800730", 44, "C2入厝派對 (V07 私廚到府聚會)"),
    ("52726886540530", 44, "C3長輩壽宴 (V09 私人微醺派對)"),
    ("52726886656930", 34, "TA-1週歲溫層 (V06 寶寶性別揭曉)"),
    ("52644997254930", 32, "TA-1頂層認知-舊0504 (V10 精緻野餐外帶)"),
    ("52645018404530", 32, "TA-1高收入媽媽-舊0511 (CBO最低日限)") # Campaign level
]

def main():
    print("=" * 70)
    print("🚀 MAPLAB Meta Ads 10 檔影片全面上線與預算重拆工程")
    print("=" * 70)
    
    deployed_results = []
    
    # 步驟 1: 上傳影片並生成 AdCreative
    for cfg in CAMPAIGN_CONFIGS:
        cid = cfg["id"]
        v_path = os.path.join(DESKTOP_DIR, cfg["file"])
        print(f"\n🎬 處理 [{cid}] {cfg['headline']}...")
        
        video_id = cfg.get("existing_video_id")
        creative_id = cfg.get("existing_creative_id")
        
        if not video_id:
            if not os.path.exists(v_path):
                print(f"  ⚠️ 找不到檔案: {v_path}")
                continue
            print(f"  [1/4] 上傳影片至 Meta: {cfg['file']}...")
            video_id = upload_video_file(v_path, f"MAPLAB {cid} 15s 9x16")
            if not video_id:
                print(f"  ❌ [{cid}] 上傳失敗，跳過")
                continue
            print(f"  ✅ 影片上傳成功: video_id={video_id}")
            cfg["video_id"] = video_id
        else:
            print(f"  ℹ️ 使用既有影片: video_id={video_id}")
        
        if not creative_id:
            print("  [2/4] 等待 Meta 轉檔完成...")
            ready = False
            for attempt in range(25):
                code, vinfo = get(f"{video_id}", {"fields": "status"})
                vstatus = vinfo.get("status", {}).get("video_status")
                if vstatus == "ready":
                    ready = True
                    break
                time.sleep(3)
            
            if not ready:
                print(f"  ⚠️ 轉檔逾時或尚未 ready (狀態: {vstatus})，重試取縮圖...")
            
            print("  [3/4] 取得縮圖 URI...")
            thumb_url = None
            for attempt in range(10):
                code, th = get(f"{video_id}/thumbnails", {"fields": "uri"})
                tdata = th.get("data", [])
                if tdata and tdata[0].get("uri"):
                    thumb_url = tdata[0].get("uri")
                    break
                time.sleep(2)
            
            if not thumb_url:
                print(f"  ❌ 找不到縮圖，跳過此素材")
                continue
            
            print("  [4/4] 建立 AdCreative...")
            spec = {
                "page_id": PAGE_ID,
                "video_data": {
                    "video_id": video_id,
                    "image_url": thumb_url,
                    "message": cfg["message"],
                    "title": cfg["headline"],
                    "call_to_action": {
                        "type": "LEARN_MORE",
                        "value": {
                            "link": "https://www.maplabkitchen.com/"
                        }
                    }
                }
            }
            c_data = {
                "name": f"UTM-{cfg['ad_name']}",
                "object_story_spec": json.dumps(spec),
                "url_tags": UTM_TEMPLATE
            }
            code, c_resp = post(f"{ACT}/adcreatives", c_data)
            if code == 200 and "id" in c_resp:
                creative_id = c_resp["id"]
                print(f"  ✅ 成功建立 Creative: {creative_id}")
            else:
                print(f"  ❌ 建立 Creative 失敗 (http={code}): {c_resp}")
                continue
        else:
            print(f"  ℹ️ 使用既有 Creative: {creative_id}")
        
        deployed_results.append({
            "config": cfg,
            "video_id": video_id,
            "creative_id": creative_id
        })
        time.sleep(1)

    print("\n" + "=" * 70)
    print("🎯 將影片 AdCreative 連結至 AdSet 並設為 ACTIVE...")
    print("=" * 70)
    
    ad_deploy_records = []
    for item in deployed_results:
        cfg = item["config"]
        cr_id = item["creative_id"]
        adset_id = cfg["target_adset"]
        
        # 檢查該 adset 是否已存在此 ad
        code, cur_ads = get(f"{adset_id}/ads", {"fields": "id,name,status", "limit": "20"})
        existing_ad = next((a for a in cur_ads.get("data", []) if cfg["id"] in a.get("name", "")), None)
        
        ad_id = None
        if existing_ad:
            ad_id = existing_ad["id"]
            print(f"  🔄 更新既有廣告 {ad_id} ({existing_ad['name']}) -> creative {cr_id}...")
            code, upd = post(ad_id, {
                "creative": json.dumps({"creative_id": cr_id}),
                "status": "ACTIVE"
            })
            print(f"  {'✅' if code == 200 else '❌'} 更新結果: {code}")
        else:
            print(f"  ➕ 在 AdSet {adset_id} 建立新影片廣告: {cfg['ad_name']}...")
            code, ad_resp = post(f"{ACT}/ads", {
                "name": cfg["ad_name"],
                "adset_id": adset_id,
                "creative": json.dumps({"creative_id": cr_id}),
                "status": "ACTIVE"
            })
            if code == 200 and "id" in ad_resp:
                ad_id = ad_resp["id"]
                print(f"  ✅ 建立成功: ad_id={ad_id}")
            else:
                print(f"  ❌ 建立失敗: {code} -> {ad_resp}")
        
        ad_deploy_records.append({
            "video_code": cfg["id"],
            "adset_id": adset_id,
            "ad_id": ad_id,
            "creative_id": cr_id,
            "status": "ACTIVE"
        })
        time.sleep(1)

    print("\n" + "=" * 70)
    print("💰 依指示拆預算（總日預算精確控制在 590 TWD，嚴格符合上限 616 TWD）...")
    print("=" * 70)
    
    total_budget = sum(b[1] for b in BUDGET_UPDATES)
    print(f"📋 目標日預算總額: {total_budget} TWD / 日 (上限: 616 TWD)\n")
    
    budget_records = []
    for oid, db_amount, note in BUDGET_UPDATES:
        code, resp = post(oid, {"daily_budget": str(db_amount)})
        good = code == 200 and resp.get("success", True)
        budget_records.append({
            "target_id": oid,
            "amount_twd": db_amount,
            "note": note,
            "success": good
        })
        print(f"  {'✅' if good else '❌'} ID {oid} | {note} -> {db_amount} TWD/日 (http={code})")
        time.sleep(1)

    print("\n" + "=" * 70)
    print("🔍 最終帳號 LIVE 狀態讀回驗證")
    print("=" * 70)
    
    code, active_sets = get(f"{ACT}/adsets", {
        "fields": "id,name,effective_status,daily_budget",
        "filtering": json.dumps([{"field": "adset.effective_status", "operator": "IN", "value": ["ACTIVE"]}])
    })
    
    live_adset_total = 0
    print("【活躍廣告組 (AdSets)】")
    for s in active_sets.get("data", []):
        db = int(s.get("daily_budget") or 0)
        live_adset_total += db
        print(f"  ADSET {s['id']} | {s.get('effective_status')} | db={db:3d} TWD | {s.get('name')}")
    
    # 讀取 CBO 活動
    code, cbo_camps = get(f"{ACT}/campaigns", {
        "fields": "id,name,effective_status,daily_budget",
        "filtering": json.dumps([{"field": "campaign.effective_status", "operator": "IN", "value": ["ACTIVE"]}])
    })
    live_cbo_total = 0
    print("\n【活躍活動 (Campaigns CBO)】")
    for c in cbo_camps.get("data", []):
        cdb = c.get("daily_budget")
        if cdb:
            live_cbo_total += int(cdb)
            print(f"  CAMP  {c['id']} | {c.get('effective_status')} | db={int(cdb):3d} TWD | {c.get('name')}")

    total_account_live = live_adset_total + live_cbo_total
    print(f"\n  🎯 最終全帳號日預算總實數: {total_account_live} TWD / 日 (上限: 616 TWD)")

    # 匯出結果報表
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "account_id": ACT,
        "total_budget_daily_twd": total_account_live,
        "budget_cap_twd": 616,
        "deployed_ads": ad_deploy_records,
        "budget_allocations": budget_records
    }
    
    out_file = "/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/meta_video_suite_deployment_live.json"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n📄 完整部署記錄已寫入: {out_file}")

if __name__ == "__main__":
    main()

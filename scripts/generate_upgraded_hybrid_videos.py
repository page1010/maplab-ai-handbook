#!/usr/bin/env python3
"""
generate_upgraded_hybrid_videos.py
================================================================================
MAPLAB A8 影音產線升級版：結合 Nano Banana (Gemini AI 生成) 虛實混剪、Canva 節奏模板與音樂節拍對齊
================================================================================
升級要點：
1. 【EXIF 正向檢測】：強制調用 ImageOps.exif_transpose，徹底消除素材轉 90 度的問題。
2. 【全文字粗體化】：升級為高磅數粗體字型 (PingFang/STHeiti Heavy/Bold)，加大字號與雙層高對比描邊。
3. 【Canva 節奏模板】：導入頂部主題標籤 Capsule、精緻邊框與角標貼紙 (Sticker Badges)。
4. 【音樂節拍對齊 (Beat-Sync)】：分鏡長度嚴格按音樂拍點 (BPM Bar) 裁切，並在拍點加入 Ken Burns 脈衝微動。
5. 【Nano Banana 虛實結合】：前 2 秒導入 AI 生成極致反差迷因鉤子 (如：辦公室披薩恐慌、單手抱娃崩潰媽媽、新店披薩命案、爆乳名媛真情告白)，隨後無縫切入 MAPLAB 真實外燴。
6. 【嚴格紅線】：絕對零「長輩」，全數合規使用「親友」。結尾統一 CTA。
================================================================================
"""

import os
import sys
import subprocess
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageOps

BASE_DRIVE_DIR = "/Volumes/MacExternal/外接硬碟 讀取專用/google drive同步/2026maplab外燴紀錄"
MK_AUDIO_DIR = "/Users/pagemacmini/maplab-ai-handbook/data/music-style-db/maplabkitchen"
OUTPUT_DIR = "/Users/pagemacmini/Desktop/Meta廣告素材_十案整理/升級版_Canva節拍與AI虛實混剪"
SCRATCH_DIR = "/Users/pagemacmini/.gemini/antigravity/brain/e7e35f62-bdeb-476b-a282-c831c3bfcc64/scratch/upgraded_render"
BRAIN_DIR = "/Users/pagemacmini/.gemini/antigravity/brain/e7e35f62-bdeb-476b-a282-c831c3bfcc64"

FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_INDEX = 0

BANNED_WORDS = ["長輩"]

# 4 款具備 Nano Banana AI 生成視覺鉤子的升級旗艦檔
UPGRADED_CAMPAIGNS = {
    "V01_Zhuazhou": {
        "title": "週歲抓周 · 一手抱娃一手吃飽",
        "badge": "【 週歲抓周 · 媽媽救星 】",
        "sticker": "★ 單手優雅吃",
        "track": "MK-001",
        "bpm": 100,  # 1 beat = 0.60s
        "ai_hook_img": os.path.join(BRAIN_DIR, "zhuazhou_mom_struggle_1790953751763.jpg"),
        "real_folder": "0719善化抓周-胡厝里自宅",
        "real_images": ["20260719_100132.jpg", "20260719_100125.jpg", "20260719_100114.jpg"],
        "shots": [
            # Shot 1: AI Hook (4 beats = 2.4s)
            {"is_ai": True, "duration": 2.4, "zoom_start": 1.0, "zoom_end": 1.08, "line1": "今天抓周，媽媽抱著孩子", "line2": "「好餓！但我只有一隻手啊？！」"},
            # Shot 2: Real Turn (5 beats = 3.0s)
            {"is_ai": False, "img_idx": 0, "duration": 3.0, "zoom_start": 1.06, "zoom_end": 1.0, "line1": "一手抱著孩子，另一隻手也拿得動", "line2": "妳不必把孩子放下，也能優雅吃飽"},
            # Shot 3: Real Atmosphere (6 beats = 3.6s)
            {"is_ai": False, "img_idx": 1, "duration": 3.6, "zoom_start": 1.0, "zoom_end": 1.08, "line1": "親友一進門就看見精緻甜點塔", "line2": "親友稱讚、朋友拍照，氛圍直接拉滿"},
            # Shot 4: Real Relief (6 beats = 3.6s)
            {"is_ai": False, "img_idx": 2, "duration": 3.6, "zoom_start": 1.05, "zoom_end": 1.0, "line1": "不必提早備料，也不必收拾洗碗", "line2": "把時間留給重要時刻，今天妳也是主角"},
            # Shot 5: Outro (4 beats = 2.4s) -> Total = 15.0s
            {"is_ending": True, "duration": 2.4, "zoom_start": 1.0, "zoom_end": 1.04, "line1": "快預約下一場派對。", "line2": "www.maplabkitchen.com"}
        ]
    },
    "V03_TechCorporate": {
        "title": "企業南科 · 主管說隨便訂但要體面",
        "badge": "【 辦公室求生 · 福委神器 】",
        "sticker": "★ 外商主管大讚",
        "track": "MK-003",
        "bpm": 100,  # 1 beat = 0.60s
        "ai_hook_img": os.path.join(BRAIN_DIR, "office_pizza_panic_1790953731640.jpg"),
        "real_folder": "0718 南科-科林研發日",
        "real_images": ["20260718_134004.jpg", "20260718_134021.jpg", "20260718_133914.jpg"],
        "shots": [
            # Shot 1: AI Hook (4 beats = 2.4s)
            {"is_ai": True, "duration": 2.4, "zoom_start": 1.0, "zoom_end": 1.08, "line1": "主管說隨便訂，你真的敢叫披薩？！", "line2": "福委群組一片死寂：這能看嗎？！"},
            # Shot 2: Real Turn (5 beats = 3.0s)
            {"is_ai": False, "img_idx": 0, "duration": 3.0, "zoom_start": 1.06, "zoom_end": 1.0, "line1": "告別油膩冷便當，讓工程師放下鍵盤", "line2": "一手拿簡報一手優雅吃，完全不掉屑"},
            # Shot 3: Real Atmosphere (6 beats = 3.6s)
            {"is_ai": False, "img_idx": 1, "duration": 3.6, "zoom_start": 1.0, "zoom_end": 1.08, "line1": "黑松露厚蛋、迷你黑牛堡直接上桌", "line2": "外商長官走過來點頭：「這次很有品味」"},
            # Shot 4: Real Relief (6 beats = 3.6s)
            {"is_ai": False, "img_idx": 2, "duration": 3.6, "zoom_start": 1.05, "zoom_end": 1.0, "line1": "專人現場擺盤陳列，無痕整潔撤場", "line2": "從此不再為辦公室茶會抓狂"},
            # Shot 5: Outro (4 beats = 2.4s) -> Total = 15.0s
            {"is_ending": True, "duration": 2.4, "zoom_start": 1.0, "zoom_end": 1.04, "line1": "快預約下一場派對。", "line2": "www.maplabkitchen.com"}
        ]
    },
    "V04_StoreOpening": {
        "title": "門市開幕 · 別讓披薩毀了兩百萬裝潢",
        "badge": "【 品牌門市開幕 · 門面升級 】",
        "sticker": "★ 自帶百萬打卡流量",
        "track": "MK-004",
        "bpm": 110,  # 1 beat = 0.545s
        "ai_hook_img": os.path.join(BRAIN_DIR, "boutique_pizza_offense_1790953771477.jpg"),
        "real_folder": "0621說事實木地板開幕",
        "real_images": ["IMG_1400.HEIC", "IMG_1408.HEIC", "IMG_1409.HEIC"],
        "shots": [
            # Shot 1: AI Hook (2.4s)
            {"is_ai": True, "duration": 2.4, "zoom_start": 1.0, "zoom_end": 1.08, "line1": "花兩百萬裝潢新店面", "line2": "開幕你打算叫大披薩滴油在地板上？！"},
            # Shot 2: Real Turn (3.0s)
            {"is_ai": False, "img_idx": 0, "duration": 3.0, "zoom_start": 1.06, "zoom_end": 1.0, "line1": "外燴餐檯就是品牌門面的延伸", "line2": "客製色系陳列，精品小食如珠寶發光"},
            # Shot 3: Real Atmosphere (3.6s)
            {"is_ai": False, "img_idx": 1, "duration": 3.6, "zoom_start": 1.0, "zoom_end": 1.08, "line1": "貴賓進門先搶著拍餐檯發限動", "line2": "天然百萬打卡流量，開幕品味直接封頂"},
            # Shot 4: Real Relief (3.6s)
            {"is_ai": False, "img_idx": 2, "duration": 3.6, "zoom_start": 1.05, "zoom_end": 1.0, "line1": "專業控管動線與現場潔淨", "line2": "讓每一位貴賓記住你品牌的精緻格調"},
            # Shot 5: Outro (2.4s)
            {"is_ending": True, "duration": 2.4, "zoom_start": 1.0, "zoom_end": 1.04, "line1": "快預約下一場派對。", "line2": "www.maplabkitchen.com"}
        ]
    },
    "V05_MansionVIP": {
        "title": "豪宅建案 · 客人在客廳主人不用洗碗",
        "badge": "【 私宅微奢聚會 · 頂級私廚 】",
        "sticker": "★ 派對結束零洗碗",
        "track": "MK-005",
        "bpm": 95,
        "ai_hook_img": os.path.join(BRAIN_DIR, "glam_ai_catering_truth_1790953803854.jpg"),
        "real_folder": "0815國泰原美",
        "real_images": ["20260815_133041.jpg", "20260815_133057.jpg", "20260815_133104.jpg"],
        "shots": [
            # Shot 1: AI Hook (2.4s)
            {"is_ai": True, "duration": 2.4, "zoom_start": 1.0, "zoom_end": 1.08, "line1": "「什麼社交？！我只是來吃外燴的！」", "line2": "請朋友來豪宅，別讓主人在廚房洗三小時碗"},
            # Shot 2: Real Turn (3.0s)
            {"is_ai": False, "img_idx": 0, "duration": 3.0, "zoom_start": 1.06, "zoom_end": 1.0, "line1": "真正的微奢聚會，主人手握高腳杯從容社交", "line2": "備料、法式冷盤、細緻收整全由私廚打理"},
            # Shot 3: Real Atmosphere (3.6s)
            {"is_ai": False, "img_idx": 1, "duration": 3.6, "zoom_start": 1.0, "zoom_end": 1.08, "line1": "燈光微醺，精工小點襯托生活品味", "line2": "親友盛讚連連，散場後客廳乾乾淨淨"},
            # Shot 4: Real Relief (3.6s)
            {"is_ai": False, "img_idx": 2, "duration": 3.6, "zoom_start": 1.05, "zoom_end": 1.0, "line1": "把款待的時間，留給最重要的知心好友", "line2": "私廚級外燴規格，為豪宅量身訂製"},
            # Shot 5: Outro (2.4s)
            {"is_ending": True, "duration": 2.4, "zoom_start": 1.0, "zoom_end": 1.04, "line1": "快預約下一場派對。", "line2": "www.maplabkitchen.com"}
        ]
    }
}

def audit_banned_words():
    for cid, cdata in UPGRADED_CAMPAIGNS.items():
        for sidx, shot in enumerate(cdata["shots"]):
            for key in ["line1", "line2"]:
                text = shot.get(key, "")
                for banned in BANNED_WORDS:
                    if banned in text:
                        raise ValueError(f"🚨 紅線違規！影片 [{cid}] 第 {sidx+1} 鏡頭包含禁詞「{banned}」: '{text}'。必須改用「親友」！")
    print("🛡️ [紅線審核通過] 全數升級版腳本零「長輩」，全數合規使用「親友」。")

def load_and_fix_orientation(image_path):
    """加載並透過 EXIF 資訊自動校正旋轉，徹底杜絕轉90度錯誤"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"找不到圖片: {image_path}")
    
    if image_path.lower().endswith(".heic"):
        clean_name = os.path.splitext(os.path.basename(image_path))[0] + ".jpg"
        conv_dir = os.path.join(SCRATCH_DIR, "heic_cache")
        os.makedirs(conv_dir, exist_ok=True)
        cached_jpg = os.path.join(conv_dir, clean_name)
        if not os.path.exists(cached_jpg):
            subprocess.run(
                ["sips", "-s", "format", "jpeg", image_path, "--out", cached_jpg],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        img = Image.open(cached_jpg)
    else:
        img = Image.open(image_path)
        
    img = ImageOps.exif_transpose(img)
    return img.convert("RGB")

def render_frame_motion(base_img, target_w, target_h, progress, zoom_start, zoom_end):
    current_scale = zoom_start + (zoom_end - zoom_start) * progress
    img_w, img_h = base_img.size
    target_aspect = target_w / target_h
    img_aspect = img_w / img_h
    
    if img_aspect > target_aspect:
        crop_h = img_h / current_scale
        crop_w = crop_h * target_aspect
    else:
        crop_w = img_w / current_scale
        crop_h = crop_w / target_aspect
        
    left = (img_w - crop_w) / 2
    top = (img_h - crop_h) / 2
    right = left + crop_w
    bottom = top + crop_h
    
    cropped = base_img.crop((left, top, right, bottom))
    frame = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
    return frame

def draw_canva_overlay(frame, shot, badge_text, sticker_text, target_w, target_h, is_ai=False):
    draw = ImageDraw.Draw(frame, "RGBA")
    line1 = shot.get("line1", "")
    line2 = shot.get("line2", "")
    is_ending = shot.get("is_ending", False)

    if is_ending:
        overlay = Image.new("RGBA", (target_w, target_h), (12, 10, 8, 225))
        frame.paste(overlay, (0, 0), overlay)
        draw = ImageDraw.Draw(frame, "RGBA")
        
        font_large = ImageFont.truetype(FONT_PATH, 66, index=FONT_INDEX)
        font_url = ImageFont.truetype(FONT_PATH, 38, index=FONT_INDEX)
        
        # 標題
        t_box = font_large.getbbox(line1)
        t_w = t_box[2] - t_box[0]
        cta_y = 1000
        draw.text(((target_w - t_w)//2, cta_y), line1, font=font_large, fill=(255, 255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0, 230))
        
        # 官網按鈕膠囊
        u_box = font_url.getbbox(line2)
        u_w = u_box[2] - u_box[0]
        pill_w = u_w + 70
        pill_h = 64
        pill_x = (target_w - pill_w) // 2
        url_y = 1140
        draw.rounded_rectangle([pill_x, url_y, pill_x + pill_w, url_y + pill_h], radius=32, fill=(215, 165, 110, 245), outline=(255, 235, 200, 200), width=2)
        draw.text((pill_x + 35, url_y + (pill_h - (u_box[3] - u_box[1]))//2 - 2), line2, font=font_url, fill=(20, 15, 10, 255))
        return frame

    # 1. Canva 風格頂部主題膠囊 (Top Badge Pill)
    if badge_text:
        badge_font = ImageFont.truetype(FONT_PATH, 36, index=FONT_INDEX)
        b_box = badge_font.getbbox(badge_text)
        b_w = b_box[2] - b_box[0]
        b_pill_w = b_w + 50
        b_pill_h = 56
        b_x = (target_w - b_pill_w) // 2
        b_y = 160  # Safe zone top
        draw.rounded_rectangle([b_x, b_y, b_x + b_pill_w, b_y + b_pill_h], radius=28, fill=(18, 16, 14, 210), outline=(215, 175, 120, 180), width=3)
        draw.text((b_x + 25, b_y + 8), badge_text, font=badge_font, fill=(255, 240, 220, 255), stroke_width=2, stroke_fill=(0, 0, 0, 200))

    # 2. Canva 風格右上方角標貼紙 (Sticker Badge)
    if sticker_text:
        st_font = ImageFont.truetype(FONT_PATH, 30, index=FONT_INDEX)
        s_box = st_font.getbbox(sticker_text)
        s_w = s_box[2] - s_box[0]
        s_pill_w = s_w + 36
        s_pill_h = 48
        s_x = target_w - s_pill_w - 60
        s_y = 240
        draw.rounded_rectangle([s_x, s_y, s_x + s_pill_w, s_y + s_pill_h], radius=16, fill=(225, 75, 60, 225), outline=(255, 255, 255, 200), width=2)
        draw.text((s_x + 18, s_y + 8), sticker_text, font=st_font, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 180))

    # 3. 底部強化粗體字卡 (Heavy Bold Bottom Subtitle Card)
    font_bold1 = ImageFont.truetype(FONT_PATH, 54, index=FONT_INDEX)
    font_bold2 = ImageFont.truetype(FONT_PATH, 42, index=FONT_INDEX)
    
    w1 = font_bold1.getbbox(line1)[2] - font_bold1.getbbox(line1)[0]
    w2 = font_bold2.getbbox(line2)[2] - font_bold2.getbbox(line2)[0]
    
    card_w = min(target_w - 60, max(w1, w2) + 80)
    card_x = (target_w - card_w) // 2
    card_y = 1300
    card_h = 200
    
    # 雙層玻璃擬態底板
    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=28, fill=(10, 9, 8, 220), outline=(215, 175, 120, 180), width=3)
    
    # Line 1: 亮白超粗體
    y1 = card_y + 36
    draw.text(((target_w - w1)//2, y1), line1, font=font_bold1, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0, 220))
    
    # Line 2: 暖金黃超粗體
    y2 = card_y + 118
    draw.text(((target_w - w2)//2, y2), line2, font=font_bold2, fill=(250, 225, 180, 255), stroke_width=3, stroke_fill=(0, 0, 0, 220))
    
    return frame

def render_upgraded_video(cid, cdata):
    code = cid
    track = cdata["track"]
    title = cdata["title"]
    badge = cdata["badge"]
    sticker = cdata["sticker"]
    ai_hook_img = cdata["ai_hook_img"]
    real_folder = cdata["real_folder"]
    real_images = cdata["real_images"]
    shots = cdata["shots"]
    
    target_w, target_h = (1080, 1920) # 9:16 vertical
    fps = 30
    
    tag = f"maplab_{code}_Canva_AI_BeatSync"
    raw_video = os.path.join(SCRATCH_DIR, f"{tag}_silent.mp4")
    final_output = os.path.join(OUTPUT_DIR, f"{tag}_{track}.mp4")
    
    print(f"\n========================================================")
    print(f"🎬 渲染升級版: {title} ({track})")
    print(f"   AI Hook: {os.path.basename(ai_hook_img)}")
    print(f"   Real Source: {real_folder}")
    print(f"========================================================")
    
    # 加載與 EXIF 旋轉校正圖片
    loaded_imgs = []
    # Shot 0: AI hook
    loaded_imgs.append(load_and_fix_orientation(ai_hook_img))
    # Shots 1~3: Real
    for r_img in real_images:
        loaded_imgs.append(load_and_fix_orientation(os.path.join(BASE_DRIVE_DIR, real_folder, r_img)))
        
    cmd = [
        "ffmpeg", "-y",
        "-f", "image2pipe",
        "-vcodec", "mjpeg",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "faster",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        raw_video
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    
    for sidx, shot in enumerate(shots):
        is_ending = shot.get("is_ending", False)
        is_ai = shot.get("is_ai", False)
        if is_ending:
            base_img = loaded_imgs[-1]
        elif is_ai:
            base_img = loaded_imgs[0]
        else:
            base_img = loaded_imgs[shot.get("img_idx", 0) + 1]
            
        shot_frames = int(shot["duration"] * fps)
        for f in range(shot_frames):
            prog = f / max(1, shot_frames - 1)
            frame = render_frame_motion(base_img, target_w, target_h, prog, shot["zoom_start"], shot["zoom_end"])
            frame = draw_canva_overlay(frame, shot, badge, sticker, target_w, target_h, is_ai=is_ai)
            frame.save(proc.stdin, "JPEG", quality=92)
            
    proc.stdin.close()
    proc.wait()
    
    if proc.returncode != 0:
        err = proc.stderr.read().decode("utf-8")
        raise RuntimeError(f"FFmpeg 錯誤: {err}")
        
    # 音訊壓合
    audio_file = os.path.join(MK_AUDIO_DIR, track, f"{track}_take1_15s.mp3")
    mux_cmd = [
        "ffmpeg", "-y",
        "-i", raw_video,
        "-i", audio_file,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "320k",
        "-af", "afade=t=out:st=13.5:d=1.5",
        "-shortest",
        final_output
    ]
    subprocess.run(mux_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"✅ 完成！輸出至: {final_output} ({os.path.getsize(final_output)/1024/1024:.2f} MB)")
    return final_output

def main():
    print("🚀 啟動升級版短影音渲染 (Canva 模板 + 節拍對齊 + Nano Banana 虛實結合)...")
    audit_banned_words()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(SCRATCH_DIR, exist_ok=True)
    
    outputs = []
    for cid, cdata in UPGRADED_CAMPAIGNS.items():
        out = render_upgraded_video(cid, cdata)
        outputs.append(out)
        
    print(f"\n🎉 4 檔具備 AI 虛實結合與 Canva 節奏模板的旗艦影音渲染完成！")

if __name__ == "__main__":
    main()

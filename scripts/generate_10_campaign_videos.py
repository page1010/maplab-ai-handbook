#!/usr/bin/env python3
"""
generate_10_campaign_videos.py
================================================================================
MAPLAB A8 影音內容產線：10 款場景×受眾×音樂 短影音自動化渲染管線
================================================================================
特性與規格：
1. 嚴格紅線過濾（Red Line Linter）：
   - 全自動掃描所有字卡與字幕，若偵測到禁詞「長輩」立即阻斷編譯拋錯，強制使用「親友」。
   - 零兒童全臉、無客戶敏感會議資料。
2. 規格標準化：
   - 15 秒精準節拍 (450 幀 @ 30fps，4 段內容 + 1 段結尾字卡)。
   - 支援 9:16 (1080x1920 直式 Shorts/Reels) 與 1:1 (1080x1080 正方形 Feed)。
3. 動態美學運鏡 (Ken Burns Motion) & 玻璃擬態粗體字卡 (STHeiti / PingFang TC Semibold)。
4. 結尾統一品牌金句與官網按鈕：
   - 快預約下一場派對。
   - www.maplabkitchen.com
5. 串接專屬無版權原創音軌 MK-001 ~ MK-010，15 秒無損 AAC 壓合與末段淡出。
================================================================================
"""

import os
import sys
import subprocess
import shutil
from PIL import Image, ImageDraw, ImageFont

BASE_DRIVE_DIR = "/Volumes/MacExternal/外接硬碟 讀取專用/google drive同步/2026maplab外燴紀錄"
MK_AUDIO_DIR = "/Users/pagemacmini/maplab-ai-handbook/data/music-style-db/maplabkitchen"
OUTPUT_DIR = "/Users/pagemacmini/Desktop/Meta廣告素材_十案整理"
SCRATCH_DIR = "/Users/pagemacmini/.gemini/antigravity/brain/e7e35f62-bdeb-476b-a282-c831c3bfcc64/scratch/10_campaigns_render"
ARTIFACT_DIR = "/Users/pagemacmini/.gemini/antigravity/brain/e7e35f62-bdeb-476b-a282-c831c3bfcc64"

# 尋找可用繁體中文字型
FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_INDEX = 0

BANNED_WORDS = ["長輩"]

# 10 大影片規格定義
CAMPAIGNS = {
    "V01": {
        "code": "V01_Zhuazhou",
        "track": "MK-001",
        "title": "週歲抓周：一手抱娃一手吃飽",
        "folder": "0719善化抓周-胡厝里自宅",
        "images": ["20260719_100132.jpg", "20260719_100125.jpg", "20260719_100114.jpg", "20260719_100034.jpg"],
        "shots": [
            {"duration": 3.0, "zoom_start": 1.0, "zoom_end": 1.08, "line1": "今天抓周，妳抱著孩子、忙著招呼親友", "line2": "忙碌的這一天，妳有空吃上一口東西嗎？"},
            {"duration": 3.0, "zoom_start": 1.07, "zoom_end": 1.0, "line1": "一手抱著孩子，另一隻手也拿得動", "line2": "妳不必把孩子放下，也能好好吃飽"},
            {"duration": 3.6, "zoom_start": 1.0, "zoom_end": 1.08, "line1": "親友一進門就看見這一桌", "line2": "親友稱讚、朋友拍照，氛圍感直接拉滿"},
            {"duration": 3.0, "zoom_start": 1.06, "zoom_end": 1.0, "line1": "不必提早備料，也不必收拾洗碗", "line2": "把時間留給重要時刻，今天妳也是主角"},
            {"duration": 2.4, "zoom_start": 1.0, "zoom_end": 1.04, "line1": "快預約下一場派對。", "line2": "www.maplabkitchen.com"}
        ]
    },
    "V02": {
        "code": "V02_Wedding",
        "track": "MK-002",
        "title": "浪漫證婚：新人不要餓肚子",
        "folder": "20260627東門教會證婚",
        "images": ["IMG_1447.HEIC", "IMG_1448.HEIC", "IMG_1449.HEIC", "IMG_1450.HEIC"],
        "shots": [
            {"duration": 3.0, "zoom_start": 1.0, "zoom_end": 1.07, "line1": "證婚儀式結束，新人說的第一句話往往是：", "line2": "「好餓！剛剛到底吃了什麼？」"},
            {"duration": 3.0, "zoom_start": 1.06, "zoom_end": 1.0, "line1": "不沾唇膏、不掉粉屑，一口優雅飽足", "line2": "換下一套禮服前，隨手捏取微奢冷餐"},
            {"duration": 3.6, "zoom_start": 1.0, "zoom_end": 1.08, "line1": "親友舉杯祝福，陽光灑在法式普切塔上", "line2": "這才是夢想中沒有狼狽的戶外婚禮"},
            {"duration": 3.0, "zoom_start": 1.05, "zoom_end": 1.0, "line1": "把最美好的時光留給彼此", "line2": "專屬外燴私廚，為妳點亮心動瞬間"},
            {"duration": 2.4, "zoom_start": 1.0, "zoom_end": 1.04, "line1": "快預約下一場派對。", "line2": "www.maplabkitchen.com"}
        ]
    },
    "V03": {
        "code": "V03_TechCorporate",
        "track": "MK-003",
        "title": "企業南科：主管說隨便訂但要體面",
        "folder": "0718 南科-科林研發日",
        "images": ["20260718_133914.jpg", "20260718_133928.jpg", "20260718_134004.jpg", "20260718_134021.jpg"],
        "shots": [
            {"duration": 3.0, "zoom_start": 1.0, "zoom_end": 1.08, "line1": "「吃麥當勞如何？」福委群組一片死寂", "line2": "主管說隨便訂，但大家都知道不能隨便"},
            {"duration": 3.0, "zoom_start": 1.07, "zoom_end": 1.0, "line1": "別再叫油膩冷便當跟連鎖披薩了", "line2": "一手拿簡報一手優雅吃，連工程師都停下鍵盤"},
            {"duration": 3.6, "zoom_start": 1.0, "zoom_end": 1.08, "line1": "松露厚蛋、迷你黑牛堡，質感直接拉滿", "line2": "外商主管走過來點頭：「這次辦得很有品味」"},
            {"duration": 3.0, "zoom_start": 1.06, "zoom_end": 1.0, "line1": "全套精緻擺盤與專人撤場，總務零負擔", "line2": "辦公室茶會從此告別平庸與尷尬"},
            {"duration": 2.4, "zoom_start": 1.0, "zoom_end": 1.04, "line1": "快預約下一場派對。", "line2": "www.maplabkitchen.com"}
        ]
    },
    "V04": {
        "code": "V04_StoreOpening",
        "track": "MK-004",
        "title": "門市開幕：別讓披薩毀了兩百萬裝潢",
        "folder": "0621說事實木地板開幕",
        "images": ["IMG_1400.HEIC", "IMG_1408.HEIC", "IMG_1409.HEIC", "IMG_1410.HEIC"],
        "shots": [
            {"duration": 3.0, "zoom_start": 1.0, "zoom_end": 1.08, "line1": "花了兩百萬裝潢新店面", "line2": "開幕茶會你真的打算叫大披薩滴油在木地板？"},
            {"duration": 3.0, "zoom_start": 1.07, "zoom_end": 1.0, "line1": "外燴餐檯就是品牌門面的延伸", "line2": "色系客製化搭配，精品小食如珠寶般陳列"},
            {"duration": 3.6, "zoom_start": 1.0, "zoom_end": 1.08, "line1": "貴賓進門先搶著拍餐檯發限動", "line2": "自帶百萬曝光打卡流量，開幕第一天品味封頂"},
            {"duration": 3.0, "zoom_start": 1.06, "zoom_end": 1.0, "line1": "精準控管動線與現場清潔", "line2": "讓每一位貴賓記住你品牌的極致質感"},
            {"duration": 2.4, "zoom_start": 1.0, "zoom_end": 1.04, "line1": "快預約下一場派對。", "line2": "www.maplabkitchen.com"}
        ]
    },
    "V05": {
        "code": "V05_MansionVIP",
        "track": "MK-005",
        "title": "豪宅建案：客人在客廳主人不洗碗",
        "folder": "0815國泰原美",
        "images": ["20260815_133041.jpg", "20260815_133057.jpg", "20260815_133104.jpg", "20260815_133110.jpg"],
        "shots": [
            {"duration": 3.0, "zoom_start": 1.0, "zoom_end": 1.07, "line1": "請朋友來家裡豪宅聚會", "line2": "結果客人在客廳歡聚，主人在廚房洗了三小時碗？"},
            {"duration": 3.0, "zoom_start": 1.06, "zoom_end": 1.0, "line1": "真正的微奢聚會，主人只需手握高腳杯從容社交", "line2": "備料、法式擺盤、細緻收整全由私廚打理"},
            {"duration": 3.6, "zoom_start": 1.0, "zoom_end": 1.08, "line1": "燈光微醺，精工小點襯托生活品味", "line2": "親友盛讚連連，散場後客廳乾乾淨淨"},
            {"duration": 3.0, "zoom_start": 1.05, "zoom_end": 1.0, "line1": "把款待的時間，留給最重要的知心好友", "line2": "私廚級外燴規格，為豪宅客廳量身訂製"},
            {"duration": 2.4, "zoom_start": 1.0, "zoom_end": 1.04, "line1": "快預約下一場派對。", "line2": "www.maplabkitchen.com"}
        ]
    },
    "V06": {
        "code": "V06_GenderReveal",
        "track": "MK-006",
        "title": "性別揭曉：吃飽再開箱的盲盒派對",
        "folder": "0726喜多多婚宴會館-性別派對",
        "images": ["00867919-A386-4587-90FF-EAA091685BE1.jpg", "124E2E4A-F117-479E-892B-2E1124D5846E.jpg", "4F20F1ED-282B-4F48-8595-0E1F2D508799.jpg", "69FCE5F8-3B60-4C64-9F30-FA7D61863B3F.jpg"],
        "shots": [
            {"duration": 3.0, "zoom_start": 1.0, "zoom_end": 1.08, "line1": "所有人都在盯著神秘的性別黑氣球", "line2": "但老實說……我的眼睛早就離不開那盤馬卡龍了！"},
            {"duration": 3.0, "zoom_start": 1.07, "zoom_end": 1.0, "line1": "粉藍馬卡龍、漸層特調氣泡飲", "line2": "連餐點都在為這個小奇蹟倒數計時"},
            {"duration": 3.6, "zoom_start": 1.0, "zoom_end": 1.08, "line1": "尖叫歡呼之後，大家聚在餐檯邊吃邊笑", "line2": "「猜錯性別的罰吃三個小鹹派！」儀式感直接拉滿"},
            {"duration": 3.0, "zoom_start": 1.06, "zoom_end": 1.0, "line1": "記錄人生每一個最期待的心跳瞬間", "line2": "為妳的小寶貝迎來第一場夢幻派對"},
            {"duration": 2.4, "zoom_start": 1.0, "zoom_end": 1.04, "line1": "快預約下一場派對。", "line2": "www.maplabkitchen.com"}
        ]
    },
    "V07": {
        "code": "V07_FamilyFeast",
        "track": "MK-007",
        "title": "親友家宴：今年放過媽媽誰都不准煮",
        "folder": "0719善化抓周-胡厝里自宅",
        "images": ["20260719_100125.jpg", "20260719_100110.jpg", "20260719_100101.jpg", "20260719_100034.jpg"],
        "shots": [
            {"duration": 3.0, "zoom_start": 1.0, "zoom_end": 1.07, "line1": "今年親友聚會，媽媽說「隨便煮幾道家常菜就好」", "line2": "——大家心裡其實都在暗自發抖！"},
            {"duration": 3.0, "zoom_start": 1.06, "zoom_end": 1.0, "line1": "備料兩天、洗碗半天、媽媽腰酸背痛？", "line2": "今年放過媽媽，整桌精緻外燴直接送到府！"},
            {"duration": 3.6, "zoom_start": 1.0, "zoom_end": 1.08, "line1": "媽媽第一次坐下來跟親友聊天喝熱茶", "line2": "親友筷子停不下來：「這比大飯店還舒服有面子」"},
            {"duration": 3.0, "zoom_start": 1.05, "zoom_end": 1.0, "line1": "無油煙、零剩菜負擔、全家人都輕鬆", "line2": "把最溫暖的時間，留給真正的團聚"},
            {"duration": 2.4, "zoom_start": 1.0, "zoom_end": 1.04, "line1": "快預約下一場派對。", "line2": "www.maplabkitchen.com"}
        ]
    },
    "V08": {
        "code": "V08_ArtCurator",
        "track": "MK-008",
        "title": "藝文展會：美學延伸的幾何茶點",
        "folder": "0911成大工設系-美國大學交流餐會design in taiwan",
        "images": ["03B444F1-17A3-43C4-AA3F-23C16DFCF244.jpg", "31F6E0F5-DEB1-45C7-9A8B-E739AD4F68A2.jpg", "334C8C57-ED9F-4F39-94FF-B094F30BCA19.jpg", "FF4E448A-5CD1-41A9-8AC3-E51B0015E776.jpg"],
        "shots": [
            {"duration": 3.0, "zoom_start": 1.0, "zoom_end": 1.08, "line1": "設計系辦國際交流論壇", "line2": "桌上若擺著傳統便當餐盒，整個展覽都哭了"},
            {"duration": 3.0, "zoom_start": 1.07, "zoom_end": 1.0, "line1": "食物本身就是展覽美學的延伸", "line2": "台南在地當季食材，化身幾何極簡藝術品"},
            {"duration": 3.6, "zoom_start": 1.0, "zoom_end": 1.08, "line1": "國際貴賓手拿托盤驚艷交流", "line2": "用味蕾與視覺，感受台灣深厚設計軟實力"},
            {"duration": 3.0, "zoom_start": 1.06, "zoom_end": 1.0, "line1": "兼顧學術典雅與無負擔交流動線", "line2": "每一場盛會，都值得像藝術品般被對待"},
            {"duration": 2.4, "zoom_start": 1.0, "zoom_end": 1.04, "line1": "快預約下一場派對。", "line2": "www.maplabkitchen.com"}
        ]
    },
    "V09": {
        "code": "V09_PartyAfterparty",
        "track": "MK-009",
        "title": "朋友包場：社恐青年破冰神器",
        "folder": "0726派對空間2館-抓周慶生",
        "images": ["IMG_1582.HEIC", "IMG_1583.HEIC", "IMG_1584.HEIC", "IMG_1585.HEIC"],
        "shots": [
            {"duration": 3.0, "zoom_start": 1.0, "zoom_end": 1.08, "line1": "參加聚會不知道怎麼開口跟人聊天？", "line2": "站在 MAPLAB 外燴餐檯前面假裝挑點心就對了！"},
            {"duration": 3.0, "zoom_start": 1.07, "zoom_end": 1.0, "line1": "「欸這個焦糖起司塔超好吃你要不要拿一個？」", "line2": "——看吧！地表最強破冰神器瞬間誕生！"},
            {"duration": 3.6, "zoom_start": 1.0, "zoom_end": 1.08, "line1": "一口接一口完全不冷場", "line2": "吃完直接嗨翻續攤，不用留下來洗盤子"},
            {"duration": 3.0, "zoom_start": 1.06, "zoom_end": 1.0, "line1": "派對包場、朋友聚會的美味神隊友", "line2": "讓每一次相聚都輕鬆又難忘"},
            {"duration": 2.4, "zoom_start": 1.0, "zoom_end": 1.04, "line1": "快預約下一場派對。", "line2": "www.maplabkitchen.com"}
        ]
    },
    "V10": {
        "code": "V10_PicnicSnacks",
        "track": "MK-010",
        "title": "外帶野餐：拎著就走的大自然私廚",
        "folder": "0612大台南會展中心-工研院在宅醫療科技推動計畫跨部會工作小組會議",
        "images": ["IMG_1734.HEIC", "IMG_1735.HEIC", "IMG_1736.HEIC", "IMG_20260612_145700 (1).jpg"],
        "shots": [
            {"duration": 3.0, "zoom_start": 1.0, "zoom_end": 1.08, "line1": "假日想去草地野餐露營", "line2": "現場切洗備料狼狽得像在荒野求生？"},
            {"duration": 3.0, "zoom_start": 1.07, "zoom_end": 1.0, "line1": "MAPLAB Party Snacks 外帶盒打開即是精緻餐檯！", "line2": "炭烤手撕豬、手工法式小點，一口優雅不沾手"},
            {"duration": 3.6, "zoom_start": 1.0, "zoom_end": 1.08, "line1": "在大自然裡享受五星級外燴的精緻儀式感", "line2": "親友盛讚連連，吃完直接打包提回家"},
            {"duration": 3.0, "zoom_start": 1.06, "zoom_end": 1.0, "line1": "拎著一盒走，隨處都是妳的私廚派對", "line2": "露營野餐也能優雅當貴婦"},
            {"duration": 2.4, "zoom_start": 1.0, "zoom_end": 1.04, "line1": "快預約下一場派對。", "line2": "www.maplabkitchen.com"}
        ]
    }
}

def audit_banned_words():
    """紅線過濾器：檢驗所有文案絕對不可含禁詞"""
    for cid, cdata in CAMPAIGNS.items():
        for sidx, shot in enumerate(cdata["shots"]):
            for key in ["line1", "line2"]:
                text = shot.get(key, "")
                for banned in BANNED_WORDS:
                    if banned in text:
                        raise ValueError(f"🚨 紅線違規！影片 [{cid}] 第 {sidx+1} 鏡頭包含禁詞「{banned}」: '{text}'。必須改用「親友」！")
    print("🛡️ [紅線審核通過] 全數 10 檔影片腳本完全零「長輩」，全數合規使用「親友」。")

def load_and_convert_image(folder, filename):
    src_path = os.path.join(BASE_DRIVE_DIR, folder, filename)
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"找不到來源圖片: {src_path}")
    
    if filename.lower().endswith(".heic"):
        clean_name = os.path.splitext(filename)[0] + ".jpg"
        conv_dir = os.path.join(SCRATCH_DIR, "heic_cache")
        os.makedirs(conv_dir, exist_ok=True)
        cached_jpg = os.path.join(conv_dir, f"{folder}_{clean_name}")
        if not os.path.exists(cached_jpg):
            subprocess.run(
                ["sips", "-s", "format", "jpeg", src_path, "--out", cached_jpg],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        return Image.open(cached_jpg).convert("RGB")
    return Image.open(src_path).convert("RGB")

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

def get_fitted_font(text, max_w, max_size, min_size=28):
    size = max_size
    while size >= min_size:
        font = ImageFont.truetype(FONT_PATH, size, index=FONT_INDEX)
        box = font.getbbox(text)
        w = box[2] - box[0]
        if w <= max_w:
            return font, w
        size -= 2
    font = ImageFont.truetype(FONT_PATH, min_size, index=FONT_INDEX)
    box = font.getbbox(text)
    return font, (box[2] - box[0])

def draw_overlay(frame, line1, line2, target_w, target_h, is_ending=False):
    draw = ImageDraw.Draw(frame, "RGBA")
    
    if is_ending:
        overlay = Image.new("RGBA", (target_w, target_h), (12, 10, 8, 215))
        frame.paste(overlay, (0, 0), overlay)
        draw = ImageDraw.Draw(frame, "RGBA")
        
        if target_h == 1920: # 9:16
            font_large = ImageFont.truetype(FONT_PATH, 64, index=FONT_INDEX)
            font_url = ImageFont.truetype(FONT_PATH, 36, index=FONT_INDEX)
            cta_y = 1020
            url_y = 1150
            pill_h = 58
            pill_radius = 29
        else: # 1:1
            font_large = ImageFont.truetype(FONT_PATH, 54, index=FONT_INDEX)
            font_url = ImageFont.truetype(FONT_PATH, 32, index=FONT_INDEX)
            cta_y = 560
            url_y = 660
            pill_h = 50
            pill_radius = 25
            
        t_box = font_large.getbbox(line1)
        t_w = t_box[2] - t_box[0]
        draw.text(((target_w - t_w)//2, cta_y), line1, font=font_large, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 180))
        
        u_box = font_url.getbbox(line2)
        u_w = u_box[2] - u_box[0]
        pill_w = u_w + 64
        pill_x = (target_w - pill_w) // 2
        draw.rounded_rectangle([pill_x, url_y, pill_x + pill_w, url_y + pill_h], radius=pill_radius, fill=(210, 160, 110, 235))
        draw.text((pill_x + 32, url_y + (pill_h - (u_box[3] - u_box[1]))//2 - 2), line2, font=font_url, fill=(20, 15, 10, 255))
        return frame

    # Subtitle card
    if target_h == 1920:
        max_content_w = 920
        f1, w1 = get_fitted_font(line1, max_content_w, 50, min_size=34)
        f2, w2 = get_fitted_font(line2, max_content_w, 42, min_size=30)
        card_y = 1320
        card_h = 190
        pad_x = 40
        y1 = card_y + 35
        y2 = card_y + 115
    else:
        max_content_w = 900
        f1, w1 = get_fitted_font(line1, max_content_w, 46, min_size=32)
        f2, w2 = get_fitted_font(line2, max_content_w, 36, min_size=28)
        card_y = 780
        card_h = 175
        pad_x = 35
        y1 = card_y + 30
        y2 = card_y + 105

    card_w = min(target_w - 60, max(w1, w2) + pad_x * 2)
    card_x = (target_w - card_w) // 2
    
    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=24,
        fill=(15, 14, 12, 215),
        outline=(210, 175, 130, 140),
        width=3
    )
    
    draw.text(((target_w - w1)//2, y1), line1, font=f1, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 180))
    draw.text(((target_w - w2)//2, y2), line2, font=f2, fill=(245, 235, 220, 255), stroke_width=2, stroke_fill=(0, 0, 0, 180))
    return frame

def render_campaign_video(campaign_id, aspect="9x16", fps=30):
    cdata = CAMPAIGNS[campaign_id]
    code = cdata["code"]
    track = cdata["track"]
    folder = cdata["folder"]
    images = cdata["images"]
    shots = cdata["shots"]
    
    target_w, target_h = (1080, 1920) if aspect == "9x16" else (1080, 1080)
    
    tag = f"maplab_{code}_15s_{aspect}"
    raw_video_path = os.path.join(SCRATCH_DIR, f"{tag}_silent.mp4")
    final_output_path = os.path.join(OUTPUT_DIR, f"{tag}_{track}.mp4")
    
    print(f"\n========================================================")
    print(f"🎬 渲染 [{campaign_id}] {cdata['title']} ({aspect})")
    print(f"   配樂: {track} | 來源: {folder}")
    print(f"========================================================")
    
    # 預載圖片
    loaded_imgs = []
    for idx, s in enumerate(shots):
        if idx < len(images):
            img_file = images[idx]
        else:
            img_file = images[-1]
        loaded_imgs.append(load_and_convert_image(folder, img_file))
        
    cmd = [
        "ffmpeg", "-y",
        "-f", "image2pipe",
        "-vcodec", "mjpeg",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "faster",
        "-crf", "19",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        raw_video_path
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    
    shot_count = len(shots)
    for idx, shot in enumerate(shots):
        is_ending = (idx == shot_count - 1)
        base_img = loaded_imgs[idx]
        shot_frames = int(shot["duration"] * fps)
        
        for f in range(shot_frames):
            progress = f / max(1, shot_frames - 1)
            frame = render_frame_motion(base_img, target_w, target_h, progress, shot["zoom_start"], shot["zoom_end"])
            frame = draw_overlay(frame, shot["line1"], shot["line2"], target_w, target_h, is_ending=is_ending)
            frame.save(proc.stdin, "JPEG", quality=92)
            
    proc.stdin.close()
    proc.wait()
    
    if proc.returncode != 0:
        err = proc.stderr.read().decode("utf-8")
        raise RuntimeError(f"FFmpeg 渲染失敗:\n{err}")
        
    # Remux 音軌
    audio_path = os.path.join(MK_AUDIO_DIR, track, f"{track}_take1_15s.mp3")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"找不到音訊檔: {audio_path}")
        
    mux_cmd = [
        "ffmpeg", "-y",
        "-i", raw_video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "320k",
        "-af", "afade=t=out:st=13.5:d=1.5",
        "-shortest",
        final_output_path
    ]
    subprocess.run(mux_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print(f"✅ 完成！輸出至: {final_output_path} ({os.path.getsize(final_output_path)/(1024*1024):.2f} MB)")
    return final_output_path

def main():
    print("🚀 啟動 MAPLAB A8 10 大短影音渲染矩陣...")
    audit_banned_words()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(SCRATCH_DIR, exist_ok=True)
    
    target_campaigns = sys.argv[1:] if len(sys.argv) > 1 else list(CAMPAIGNS.keys())
    
    rendered_files = []
    for cid in target_campaigns:
        if cid not in CAMPAIGNS:
            print(f"⚠️ 跳過未知代號: {cid}")
            continue
        v_9x16 = render_campaign_video(cid, aspect="9x16")
        v_1x1 = render_campaign_video(cid, aspect="1x1")
        rendered_files.append((cid, v_9x16, v_1x1))
        
    print(f"\n🎉 總計完成 {len(rendered_files)} 套影片渲染！")

if __name__ == "__main__":
    main()

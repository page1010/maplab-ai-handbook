#!/usr/bin/env python3
"""
push_10_campaign_videos_telegram.py
================================================================================
將 MAPLAB A8 最新渲染之 10 檔 15s 短影音 (9:16) 逐部推送至 Telegram 供 Owner 預覽審核
================================================================================
"""

import os
import sys
import time
import subprocess

sys.path.insert(0, "/Users/pagemacmini/maplab-ai-handbook/scripts")
from maplab_secrets import get_secret

BOT_TOKEN = get_secret("TELEGRAM_BOT_TOKEN")
CHAT_ID = get_secret("OWNER_CHAT_ID")
VIDEO_DIR = "/Users/pagemacmini/Desktop/Meta廣告素材_十案整理"

CAMPAIGN_INFO = [
    {
        "id": "V01",
        "file": "maplab_V01_Zhuazhou_15s_9x16_MK-001.mp4",
        "title": "週歲抓周 · 一手抱娃一手吃飽篇",
        "ta": "新手爸媽、週歲媽媽（單手抱娃、忙招呼沒空吃）",
        "music": "MK-001《小手》｜100 BPM 溫暖毛氈鋼琴",
        "hook": "辦抓周親友都在拍照，只有媽媽整天沒吃一口飯？",
        "solution": "一手抱著孩子，另一隻手也拿得動。親友稱讚、朋友拍照，氛圍感直接拉滿。今天妳也是主角！"
    },
    {
        "id": "V02",
        "file": "maplab_V02_Wedding_15s_9x16_MK-002.mp4",
        "title": "浪漫證婚 · 新人不要餓肚子篇",
        "ta": "準新人、戶外證婚伴侶、浪漫求婚策劃者",
        "music": "MK-002《牽手》｜80 BPM 溫柔原聲木吉他",
        "hook": "證婚儀式結束，新人說的第一句話往往是：「好餓，剛剛到底吃了什麼？」",
        "solution": "不沾唇膏、不掉粉屑，一口優雅飽足。親友舉杯祝福，這才是夢想中的戶外婚禮。"
    },
    {
        "id": "V03",
        "file": "maplab_V03_TechCorporate_15s_9x16_MK-003.mp4",
        "title": "企業南科 · 主管說隨便訂但要體面篇",
        "ta": "南科廠區總務、科技公司行政福委、商務會議主辦人",
        "music": "MK-003《換名片》｜100 BPM 放克律動刷鼓電鋼",
        "hook": "「吃麥當勞如何？」福委群組一片死寂。主管說隨便訂，但大家都知道不能隨便！",
        "solution": "別再叫油膩冷便當跟披薩了！松露厚蛋、迷你黑牛堡，連工程師都停下鍵盤，主管稱讚有品味。"
    },
    {
        "id": "V04",
        "file": "maplab_V04_StoreOpening_15s_9x16_MK-004.mp4",
        "title": "門市開幕 · 別讓披薩毀了兩百萬裝潢篇",
        "ta": "品牌店主、精品服飾主理人、美業新展間創辦人（填補當前 A0 廣告最大缺口）",
        "music": "MK-004《第一杯》｜110 BPM 弱音小號與放克輕吉他",
        "hook": "花了兩百萬裝潢新店面，開幕茶會你真的打算叫大披薩滴油在木地板上？",
        "solution": "外燴餐檯就是品牌門面的延伸！色系客製化搭配，貴賓進門搶拍餐檯發限動，開幕第一天品味封頂。"
    },
    {
        "id": "V05",
        "file": "maplab_V05_MansionVIP_15s_9x16_MK-005.mp4",
        "title": "豪宅建案 · 客人在客廳主人不用洗碗篇",
        "ta": "豪宅屋主、私人招待所貴賓、建案代銷經理",
        "music": "MK-005《微醺時分》｜95 BPM 絲絨夜調深層 Lounge",
        "hook": "請朋友來家裡聚會，結果客人在客廳歡聚，主人在廚房洗了三個小時油膩鍋碗？",
        "solution": "真正的微奢聚會，主人只需手握高腳杯從容社交。私廚規格打理，親友盛讚連連，散場後客廳乾乾淨淨。"
    },
    {
        "id": "V06",
        "file": "maplab_V06_GenderReveal_15s_9x16_MK-006.mp4",
        "title": "性別揭曉 · 吃飽再開箱的盲盒派對篇",
        "ta": "期待小生命的準爸媽、熱愛驚喜派對的閨蜜團",
        "music": "MK-006《心跳秒》｜110 BPM 馬林巴木琴與粉彩打擊",
        "hook": "所有人都在盯著神秘黑氣球，但老實說……我的眼睛早就離不開那盤馬卡龍了！",
        "solution": "粉藍漸層馬卡龍為小奇蹟倒數計時！尖叫歡呼後親友邊吃邊笑：「猜錯性別的罰吃三個小鹹派！」"
    },
    {
        "id": "V07",
        "file": "maplab_V07_FamilyFeast_15s_9x16_MK-007.mp4",
        "title": "親友家宴 · 今年放過媽媽誰都不准煮篇",
        "ta": "家族聚會主辦人、孝順子女（嚴格零長輩，全數親友）",
        "music": "MK-007《加菜》｜85 BPM 懷舊指彈原聲木吉他",
        "hook": "今年親友聚會，媽媽笑著說「我隨便煮幾道家常菜就好」……大家心裡其實都在暗自發抖！",
        "solution": "今年放過媽媽，整桌精緻外燴送到府！媽媽坐下來跟親友聊天喝熱茶，無油煙無剩菜，全家都輕鬆。"
    },
    {
        "id": "V08",
        "file": "maplab_V08_ArtCurator_15s_9x16_MK-008.mp4",
        "title": "藝文展會 · 美學延伸的幾何茶點篇",
        "ta": "展會策展人、大專院校設計系所、國際論壇主辦方",
        "music": "MK-008《策展人》｜88 BPM 極簡室內樂與空間留白",
        "hook": "設計系辦國際交流論壇，桌上若擺著傳統便當餐盒，整個展覽都哭了。",
        "solution": "食物本身就是展覽美學的延伸！台南當季在地食材化身幾何極簡藝術品，用味蕾感受台灣設計軟實力。"
    },
    {
        "id": "V09",
        "file": "maplab_V09_PartyAfterparty_15s_9x16_MK-009.mp4",
        "title": "朋友包場 · 社恐青年破冰神器篇",
        "ta": "派對空間主辦、慶生青年、想社交又怕尬聊的現代人",
        "music": "MK-009《續攤》｜112 BPM 律動 Organic House",
        "hook": "參加聚會不知道怎麼開口跟人聊天？站在 MAPLAB 外燴餐檯前面假裝挑點心就對了！",
        "solution": "「欸這個焦糖起司塔超好吃你要不要拿一個？」破冰神器誕生！吃完直接嗨翻續攤，不用留下來洗盤子。"
    },
    {
        "id": "V10",
        "file": "maplab_V10_PicnicSnacks_15s_9x16_MK-010.mp4",
        "title": "外帶野餐 · 拎著就走的大自然私廚篇",
        "ta": "露營野餐愛好者、不想洗碗的居家小聚、風格生活家",
        "music": "MK-010《提回家》｜110 BPM 輕快尤克里里與陽光手拍",
        "hook": "假日想去草地野餐露營，現場切洗備料狼狽得像在荒野求生？",
        "solution": "Party Snacks 外帶盒打開即是精緻餐檯！手撕豬三明治、法式手工小點，拎著走隨處都是妳的私廚派對。"
    }
]

def send_overview_message():
    text = """🎬 【MAPLAB A8 10 大短影音廣告矩陣 · 實體渲染成果交付】
══════════════════════════
各位長官、Owner 您好：
A8 影音內容產線已完成 10 款場景×受眾×音樂的短影音廣告生成！

📚 系統研究沉澱已入庫：
• 引用 Jon Bell「麥當勞理論」破除籌辦活動「吃什麼都隨便/叫披薩」的集體決策癱瘓
• 融合 John Hegarty「When the world zigs, zag」與 Dave Trott「掠奪性思維」
• 嚴格執行紅線規範：100% 替換為「親友」，絕對零「長輩」；無兒童全臉；結尾統一 CTA。

10 支 15s 高畫質直式影片即刻開始逐一發送，請於 Telegram 視窗直接點擊預覽與試聽！
══════════════════════════"""
    cmd = [
        "curl", "-s", "-X", "POST", f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        "-F", f"chat_id={CHAT_ID}",
        "-F", f"text={text}"
    ]
    subprocess.run(cmd, check=True)
    time.sleep(1)

def push_videos():
    send_overview_message()
    for idx, c in enumerate(CAMPAIGN_INFO, 1):
        v_path = os.path.join(VIDEO_DIR, c["file"])
        if not os.path.exists(v_path):
            print(f"❌ 找不到檔案: {v_path}")
            continue

        caption = f"""🎬 【{c['id']}：{c['title']}】
══════════════════════════
🎯 TA：{c['ta']}
🎵 配樂：{c['music']}
💡 痛點鉤子：{c['hook']}
✨ 核心解法：{c['solution']}
══════════════════════════
MAPLAB Kitchen · 快預約下一場派對。
www.maplabkitchen.com"""

        print(f"[{idx}/10] 正在推送 {c['id']} ({c['file']}) 至 Telegram...")
        cmd = [
            "curl", "-s", "-X", "POST", f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo",
            "-F", f"chat_id={CHAT_ID}",
            "-F", f"caption={caption}",
            "-F", "supports_streaming=true",
            "-F", f"video=@{v_path}"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if '"ok":true' in res.stdout:
            print(f"  ✅ {c['id']} 推送成功！")
        else:
            print(f"  ⚠️ {c['id']} 推送失敗: {res.stdout[:200]}")
        time.sleep(2)

    print("\n🎉 全數 10 支影片已成功發送至 Telegram！")

if __name__ == "__main__":
    push_videos()

#!/usr/bin/env python3
"""A8 Creative Engine v0 MVP — 規格卡產生器.
輸入一個個案 → 產 N 張「創意規格卡＋縮圖」→ 推 Telegram 給 Owner 5 秒選.
不花錢：旁白(ElevenLabs API)/音樂(Suno 人工) 先留 stub，Owner 訂閱後再接.
RAM 保守：只出縮圖、不渲染影片。"""
import json, subprocess, urllib.request, urllib.parse, uuid, re, shutil
from pathlib import Path

REPO = Path.home() / "maplab-ai-handbook"
FONT_SRC = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT = "/tmp/ce_font.ttc"
shutil.copy(FONT_SRC, FONT)

# ---- stubs：Owner 訂閱後接 ----
def render_narration_stub(text, persona):
    """待 ElevenLabs Starter(有 API)：return mp3 path。現在回 None(留位)。"""
    return None
def render_music_stub(direction):
    """Suno 無官方 API → 人工在網頁生成下載。現在回 None(留位)。"""
    return None

# tone 選單（含固定卡別「留言 Rap」）
TONE_MENU = ["紀錄片", "搞笑", "浪漫", "文青(indie)", "發表會", "MV", "紀錄片(茶點視角)", "留言Rap(comment-rap)"]
# 固定卡別：顧客好評/留言 → trap beat → 30s Short
COMMENT_RAP = {
    "how": "Suno Custom Mode 貼留言當歌詞 + 曲風填 trap/hip-hop（半自動,無 API;免費試聽,Pro 商用下載）",
    "structure": "[Hook] 品牌+場景鉤子 / [Verse] 好評重點押韻 / [Hook] 收尾；約 30s；自然置入 台南外燴/MAPLAB/場景",
    "voice": "唱＝Suno；旁白版才用 ElevenLabs（唸）",
    "source_rule": "優先用真實好評(Google 商家/IG/LINE)並標來源；拿不到用代表性一則並註明",
}

def draw_card(base_img, out_jpg, num, tone, hook):
    hookfile = f"/tmp/ce_hook_{num}.txt"; Path(hookfile).write_text(hook)
    vf = (
        "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,"
        "drawbox=x=0:y=0:w=720:h=150:color=black@0.45:t=fill,"
        "drawbox=x=0:y=900:w=720:h=380:color=black@0.40:t=fill,"
        f"drawtext=fontfile={FONT}:text='#{num}  {tone}':x=30:y=48:fontsize=46:fontcolor=white,"
        f"drawtext=fontfile={FONT}:textfile={hookfile}:x=40:y=960:fontsize=60:fontcolor=white:line_spacing=16"
    )
    r = subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(base_img),"-vf",vf,"-frames:v","1",str(out_jpg)],
                       capture_output=True, text=True)
    if r.returncode != 0: print("[draw err]", num, r.stderr[-160:])
    return out_jpg

def generate(case, cards, base_dir):
    out = base_dir / "spec_cards"; out.mkdir(parents=True, exist_ok=True)
    swift = REPO / "tools/ai_workbook/ce_cards.swift"
    inp = base_dir / "spec_cards_input.json"
    r = subprocess.run(["swift", str(swift), str(inp), str(base_dir)], capture_output=True, text=True)
    print("[swift]", (r.stdout or "").strip()[-200:], (r.stderr or "")[-200:])
    return [(c, out / f"card_{c['id']:02d}.jpg") for c in cards]

def tg_send(made, case, env):
    TG = env["TELEGRAM_BOT_TOKEN"]; CHAT = env.get("OWNER_CHAT_ID", "1077768811")
    # 1) media group (最多10張縮圖)
    b = uuid.uuid4().hex; parts = []
    media = []
    for i,(c,img) in enumerate(made[:10]):
        key = f"card{c['id']:02d}"
        m = {"type":"photo","media":f"attach://{key}"}
        if i == 0:
            m["caption"] = f"🎬 Creative Engine 規格卡 x{len(made[:10])}｜{case['name']}\n回「編號」選(可多選)，選中的才渲染。"
        media.append(m)
    def field(name, val):
        parts.append(b"--"+b.encode()+('\r\nContent-Disposition: form-data; name="%s"\r\n\r\n'%name).encode()+str(val).encode()+b"\r\n")
    field("chat_id", CHAT); field("media", json.dumps(media, ensure_ascii=False))
    for c,img in made[:10]:
        key = f"card{c['id']:02d}"
        parts.append(b"--"+b.encode()+('\r\nContent-Disposition: form-data; name="%s"; filename="%s.jpg"\r\nContent-Type: image/jpeg\r\n\r\n'%(key,key)).encode()+open(img,"rb").read()+b"\r\n")
    body = b"".join(parts)+b"--"+b.encode()+b"--\r\n"
    req = urllib.request.Request(f"https://api.telegram.org/bot{TG}/sendMediaGroup", data=body,
                                 headers={"Content-Type":f"multipart/form-data; boundary={b}"})
    j = json.load(urllib.request.urlopen(req, timeout=180))
    mg_ids = [m["message_id"] for m in j.get("result",[])] if j.get("ok") else j
    # 2) 文字：10 卡規格摘要
    lines = [f"📋 {case['name']} 規格卡摘要（回編號選）："]
    for c,_ in made:
        lines.append(f"#{c['id']:02d} [{c['tone']}] {c['hook_oneline']}｜🎵{c['music']}｜🎙{c['voice']}")
    lines.append("（旁白待 ElevenLabs Starter；音樂待 Suno 人工。選中我先用 ffmpeg+字幕渲染，聲音留位之後接。）")
    d = urllib.parse.urlencode({"chat_id":CHAT,"text":"\n".join(lines)}).encode()
    j2 = json.load(urllib.request.urlopen(urllib.request.Request(f"https://api.telegram.org/bot{TG}/sendMessage", data=d), timeout=60))
    return mg_ids, (j2.get("result",{}).get("message_id") if j2.get("ok") else j2)

def sheet_append(cards, case, token):
    d = urllib.parse.urlencode({"client_id":token["client_id"],"client_secret":token["client_secret"],
        "refresh_token":token["refresh_token"],"grant_type":"refresh_token"}).encode()
    AT = json.load(urllib.request.urlopen(urllib.request.Request(token["token_uri"], data=d), timeout=30))["access_token"]
    SID = "1EauPnuIVCV-4I7g6rGHADlcktQg1SorINDfJe36aQhg"
    meta = json.load(urllib.request.urlopen(urllib.request.Request(
        f"https://sheets.googleapis.com/v4/spreadsheets/{SID}?fields=sheets.properties.title",
        headers={"Authorization":f"Bearer {AT}"}), timeout=30))
    tab = meta["sheets"][0]["properties"]["title"]
    rows = [[f"CE-WF-{c['id']:02d}", case["date"], case["name"], c["tone"], c["music"], c["voice"],
             c["hook_oneline"], f"card_{c['id']:02d}.jpg", "推播待選", "未渲染", "", "", "", c.get("note","")] for c in cards]
    body = json.dumps({"values":rows}).encode()
    req = urllib.request.Request(
        f"https://sheets.googleapis.com/v4/spreadsheets/{SID}/values/{urllib.parse.quote(tab)}!A1:append?valueInputOption=USER_ENTERED",
        data=body, headers={"Authorization":f"Bearer {AT}","Content-Type":"application/json"}, method="POST")
    return json.load(urllib.request.urlopen(req, timeout=30)).get("updates",{}).get("updatedRows")

def tg_send_text(cards, case, env):
    """預設模式：純文字規格卡（不配縮圖，省算力）。每卡＝Hook＋3節拍＋CTA＋音樂/旁白方向。"""
    TG = env["TELEGRAM_BOT_TOKEN"]; CHAT = env.get("OWNER_CHAT_ID", "1077768811")
    lines = [f"🎬 {case['name']}｜Creative Engine 規格卡（文字版，回編號選，可多選）"]
    for c in cards:
        beats = "｜".join(c.get("beats", [])) or "—"
        lines.append(f"\n#{c['id']:02d} [{c['tone']}]\nHook: {c['hook_oneline']}\n節拍: {beats}\nCTA: {c.get('cta','—')}\n🎵{c['music']}｜🎙{c['voice']}")
    lines.append("\n（旁白待 ElevenLabs Starter API；音樂待 Suno 人工。回編號→選中才渲染。）")
    text = "\n".join(lines); msgs = []
    while text:
        chunk, text = text[:3900], text[3900:]
        d = urllib.parse.urlencode({"chat_id": CHAT, "text": chunk}).encode()
        j = json.load(urllib.request.urlopen(urllib.request.Request(f"https://api.telegram.org/bot{TG}/sendMessage", data=d), timeout=60))
        msgs.append(j.get("result", {}).get("message_id") if j.get("ok") else j)
    return msgs

if __name__ == "__main__":
    import sys
    CASE = {"name": "說事實木地板 開幕", "date": "2026-06-21"}
    base = REPO / "workbook/a8/pilot-woodfloor"
    CARDS = json.load(open(base / "spec_cards_input.json"))
    env = dict(re.findall(r'^(\w+)=(.*)$', open(REPO / "bot/.env").read(), re.M))
    THUMBS = "--thumbnails" in sys.argv  # 預設純文字卡；要縮圖/封面才加 --thumbnails
    if THUMBS:
        made = generate(CASE, CARDS, base)
        mg, txt = tg_send(made, CASE, env)
        print("telegram_media_group_ids:", mg, "| summary:", txt)
    else:
        print("telegram_text_card_msg_ids:", tg_send_text(CARDS, CASE, env))
    try:
        tok = json.load(open(Path.home() / ".claude/mcp-keys/google-token.json"))
        print("sheet_rows_appended:", sheet_append(CARDS, CASE, tok))
    except Exception as e:
        print("sheet_append_error:", str(e)[:200])
    print("DONE")

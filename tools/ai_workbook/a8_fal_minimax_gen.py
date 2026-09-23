#!/usr/bin/env python3
"""A8 備援：fal.ai 上的 MiniMax Music（同模型、$0.035/首、新註冊送免費 credits、有 API、商用）.
金鑰 FAL_KEY 只從本機 bot/.env 讀、遮罩、不外流。用法：python3 a8_fal_minimax_gen.py
需 text-to-music 變體(prompt=曲風 + lyrics=歌詞,無需 reference audio)。
若 slug 不對 fal 會回清楚錯誤,依錯誤改 ENDPOINT。"""
import json, os, re, time, urllib.request
from pathlib import Path
REPO = Path.home() / "maplab-ai-handbook"

# text-to-music(2.6)：prompt(曲風10-2000)+lyrics(結構標籤,≤3500)+is_instrumental。若 404 換下列 slug 之一：
ENDPOINT = "fal-ai/minimax-music/text-to-music"
# 備選：fal-ai/minimax-music-2.6 / fal-ai/minimax-music-1.5 / fal-ai/minimax-music(需 reference_audio_url)

def load_key():
    k = os.environ.get("FAL_KEY", "") or os.environ.get("FAL_API_KEY", "")
    if not k:
        f = REPO/"bot/.env"
        if f.exists():
            # 容錯：export/空格/引號/FAL_API_KEY 皆可
            m = re.search(r'^\s*(?:export\s+)?FAL_(?:API_)?KEY\s*=\s*[\'"]?(.+?)[\'"]?\s*$', f.read_text(), re.M)
            if m: k = m.group(1).strip()
    return k
def mask(k): return (k[:5]+"…"+k[-4:]) if k and len(k)>12 else ("<set>" if k else "<none>")

LYRICS = ("[Chorus]\n邦尼兔 畢業啦 今天最神氣\n甜點桌 一擺開 全場都歡喜\n小小的手 抓一塊小酥皮\nMAPLAB 台南外燴 甜進心坎裡\n"
          "[Verse]\n畢業帽 歪歪戴 樣子超可愛\n蛋塔 杯子蛋糕 排排站好乖\n兔子餅乾 咬一口 喀滋脆到嗨\n小朋友 踮起腳 笑容藏不來\n"
          "[Outro]\n邦尼兔 畢業啦 記得這一天\nMAPLAB 陪你長大 甜甜的畫面")
STYLES = {
    "boom_bap": "Chinese hip-hop boom bap, playful and warm, male rap with sung hook, jazzy piano and vinyl, around 90 BPM",
    "trap":     "Chinese trap, warm, male rap, 808 bass and hi-hats, around 140 BPM",
    "lofi":     "Chinese lo-fi hip hop, cozy nostalgic, soft vocal, mellow keys and brushed drums, around 75 BPM",
}
def _req(url, key, data=None):
    r = urllib.request.Request(url, data=(json.dumps(data).encode() if data is not None else None),
        headers={"Authorization": f"Key {key}", "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r, timeout=180))
def generate(key, style):
    try:
        sub = _req(f"https://queue.fal.run/{ENDPOINT}", key,
                   {"prompt": style, "lyrics": LYRICS, "is_instrumental": False})
    except urllib.error.HTTPError as e:
        return {"http_error": e.code, "body": e.read()[:200].decode(errors="ignore")}
    surl = sub.get("status_url"); rurl = sub.get("response_url")
    for _ in range(60):
        st = _req(surl, key)
        if st.get("status") == "COMPLETED": break
        if st.get("status") in ("FAILED","ERROR"): return {"failed": st}
        time.sleep(5)
    res = _req(rurl, key)
    a = res.get("audio") or {}
    return {"url": a.get("url") if isinstance(a, dict) else a}
def tg(text):
    env = dict(re.findall(r'^(\w+)=(.*)$', (REPO/"bot/.env").read_text(), re.M)); import urllib.parse
    urllib.request.urlopen(urllib.request.Request(
        f"https://api.telegram.org/bot{env['TELEGRAM_BOT_TOKEN']}/sendMessage",
        data=urllib.parse.urlencode({"chat_id":env.get("OWNER_CHAT_ID","1077768811"),"text":text}).encode()), timeout=60)

if __name__ == "__main__":
    key = load_key(); print("FAL key:", mask(key), "| endpoint:", ENDPOINT)
    if not key:
        print("NEEDS_KEY: 註冊 fal.ai(送免費 credits)→取 FAL_KEY→加一行 FAL_KEY=... 進 bot/.env 再跑。"); raise SystemExit(0)
    lines = ["🎵 fal.ai×MiniMax 邦尼兔 v1 × 3 曲風 試聽（新註冊免費 credits，$0.035/首）"]
    for name, style in STYLES.items():
        r = generate(key, style); print(name, json.dumps(r, ensure_ascii=False))
        lines.append(f"[{name}] {r['url']}" if r.get("url") else f"[{name}] ❌ {r.get('http_error') or r.get('failed') or r.get('body','')[:100]}")
    tg("\n".join(lines)); print("TG_SENT")

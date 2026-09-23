#!/usr/bin/env python3
"""A8 MiniMax Music 生成（Mac-side，secret 不外流）.
金鑰只從本機讀（bot/.env 的 MINIMAX_API_KEY 或環境變數），不印全值、不回傳給 Claude。
用法：python3 a8_minimax_gen.py            # 跑邦尼兔 v1 × 3 曲風(music-3.0-free)，URL 推 Telegram
輸出：只印 masked key + 每首 status/url + 錯誤碼。"""
import json, os, re, urllib.request
from pathlib import Path
REPO = Path.home() / "maplab-ai-handbook"

def load_key():
    k = os.environ.get("MINIMAX_API_KEY", "")
    if not k:
        envf = REPO / "bot/.env"
        if envf.exists():
            m = re.search(r'^MINIMAX_API_KEY=(.+)$', envf.read_text(), re.M)
            if m: k = m.group(1).strip()
    return k

def mask(k): return (k[:6] + "…" + k[-4:]) if k and len(k) > 12 else ("<set>" if k else "<none>")

# 歌詞（已過 a8_lyrics_engine 審查）→ MiniMax 格式（[Verse]/[Chorus]/[Outro] + 換行）
LYRICS = """[Chorus]
邦尼兔 畢業啦 今天最神氣
甜點桌 一擺開 全場都歡喜
小小的手 抓一塊小酥皮
MAPLAB 台南外燴 甜進心坎裡
[Verse]
畢業帽 歪歪戴 樣子超可愛
蛋塔 杯子蛋糕 排排站好乖
兔子餅乾 咬一口 喀滋脆到嗨
小朋友 踮起腳 笑容藏不來
[Outro]
邦尼兔 畢業啦 記得這一天
MAPLAB 陪你長大 甜甜的畫面"""

STYLES = {
    "boom_bap": "Chinese hip-hop boom bap, playful and warm, male rap with sung hook, jazzy piano, vinyl, ~90 BPM",
    "trap":     "Chinese trap, warm, male rap, 808 bass and hi-hats, ~140 BPM",
    "lofi":     "Chinese lo-fi hip hop, cozy nostalgic, soft vocal, mellow keys and brushed drums, ~75 BPM",
}

def generate(key, style_prompt):
    body = json.dumps({
        "model": "music-3.0-free",
        "prompt": style_prompt,
        "lyrics": LYRICS,
        "audio_setting": {"sample_rate": 44100, "bitrate": 256000, "format": "mp3"},
        "output_format": "url",
    }).encode()
    req = urllib.request.Request("https://api.minimax.io/v1/music_generation", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        j = json.load(urllib.request.urlopen(req, timeout=180))
    except urllib.error.HTTPError as e:
        return {"http_error": e.code, "body": e.read()[:200].decode(errors="ignore")}
    br = j.get("base_resp", {})
    audio = (j.get("data") or {}).get("audio") or (j.get("data") or {}).get("audio_url")
    return {"status_code": br.get("status_code"), "status_msg": br.get("status_msg"), "url": audio}

def tg(text):
    env = dict(re.findall(r'^(\w+)=(.*)$', (REPO/"bot/.env").read_text(), re.M))
    import urllib.parse
    d = urllib.parse.urlencode({"chat_id": env.get("OWNER_CHAT_ID","1077768811"), "text": text}).encode()
    urllib.request.urlopen(urllib.request.Request(
        f"https://api.telegram.org/bot{env['TELEGRAM_BOT_TOKEN']}/sendMessage", data=d), timeout=60)

if __name__ == "__main__":
    key = load_key()
    print("MINIMAX key:", mask(key))
    if not key:
        print("NEEDS_KEY: 請把一行 `MINIMAX_API_KEY=你的key` 加進 ~/maplab-ai-handbook/bot/.env（本機、不外流），再跑一次。")
        raise SystemExit(0)
    results, lines = {}, ["🎵 MiniMax 邦尼兔 v1 × 3 曲風 試聽（music-3.0-free，0 成本，24h 內下載）"]
    for name, prompt in STYLES.items():
        r = generate(key, prompt); results[name] = r
        print(name, json.dumps(r, ensure_ascii=False))
        if r.get("url"): lines.append(f"[{name}] {r['url']}")
        else: lines.append(f"[{name}] ❌ {r.get('status_code') or r.get('http_error')} {r.get('status_msg') or r.get('body','')[:80]}")
    tg("\n".join(lines))
    print("TG_SENT")

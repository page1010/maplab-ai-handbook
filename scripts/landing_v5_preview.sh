#!/bin/bash
# landing_v5_preview.sh — landing 草稿手機/桌機全頁截圖 + Drive anyone-reader 連結。
# 實測可行組合(2026-09-14):系統 /usr/bin/python3 有 playwright,驅動已安裝的 Chrome(channel=chrome)。
# 兩個教訓:1) 大窗截圖會讓 86vh hero 變 5300px→必須真視口+full_page;
#          2) loading=lazy 圖在 full_page 截圖不觸發→先逐步捲動到底再截。
# 安全邊界:token 只 source 不回顯;只讀 repo 內 index.html,不碰正式站後台。
set -u
HB="/Users/pagemacmini/maplab-ai-handbook"
PAGE="${1:-$HB/handoff/landing-draft-v2-20260911/index.html}"
OUTDIR="$HB/handoff/landing-draft-v2-20260911/qa"
mkdir -p "$OUTDIR"
TODAY=$(date +%Y%m%d)

/usr/bin/python3 - "$PAGE" "$OUTDIR" "$TODAY" <<'PYEOF'
import sys
from playwright.sync_api import sync_playwright

page_path, outdir, today = sys.argv[1], sys.argv[2], sys.argv[3]
url = "file://" + page_path

SCROLL_JS = """
async () => {
  await new Promise(resolve => {
    let y = 0;
    const timer = setInterval(() => {
      y += 500;
      window.scrollTo(0, y);
      if (y >= document.body.scrollHeight) { clearInterval(timer); resolve(); }
    }, 150);
  });
  window.scrollTo(0, 0);
}
"""

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    for name, vw, vh, dsf in (("mobile", 390, 844, 2), ("desktop", 1280, 800, 1)):
        ctx = browser.new_context(viewport={"width": vw, "height": vh}, device_scale_factor=dsf)
        pg = ctx.new_page()
        pg.goto(url, wait_until="networkidle", timeout=60000)
        pg.evaluate(SCROLL_JS)
        try:
            pg.wait_for_load_state("networkidle", timeout=30000)
        except Exception:
            pass
        pg.wait_for_timeout(2000)
        pg.screenshot(path=f"{outdir}/landing_v5_{name}_{today}.png", full_page=True)
        print(f"[ok] {name} -> {outdir}/landing_v5_{name}_{today}.png")
        ctx.close()
    browser.close()
PYEOF

# 上 Drive:固定更新同一組 file id(連結不變,Owner 手上舊連結永遠開到最新版;token 不回顯)
"$HB/bot/venv/bin/python" - "$OUTDIR/landing_v5_mobile_$TODAY.png" "$OUTDIR/landing_v5_desktop_$TODAY.png" <<'PYEOF' 2>&1 | grep -v FutureWarning
import json, os, socket, sys, time
socket.setdefaulttimeout(300)
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

info = json.load(open("/Users/pagemacmini/.claude/mcp-keys/google-token.json"))
info.pop("expiry", None)
creds = Credentials.from_authorized_user_info(info)
drive = build("drive", "v3", credentials=creds)

def retry(fn, n=3):
    for i in range(n):
        try:
            return fn()
        except Exception:
            if i == n - 1:
                raise
            time.sleep(5)

FIDS = {
    "mobile": "1BSptKalvaAho9qTZQG36nw3zPOisJA0p",
    "desktop": "1PCo73QhVfDeGpDIj7EUY0sRh5bUNIAFK",
}
for path in sys.argv[1:]:
    if not os.path.exists(path):
        continue
    name = path.split("/")[-1]
    kind = "mobile" if "mobile" in name else "desktop"
    fid = FIDS[kind]
    media = MediaFileUpload(path, mimetype="image/png", resumable=True)
    retry(lambda: drive.files().update(fileId=fid, media_body=media, body={"name": name}).execute())
    print(f"[drive-updated] {name} https://drive.google.com/file/d/{fid}/view")
PYEOF
echo "[done] landing_v5_preview $TODAY"

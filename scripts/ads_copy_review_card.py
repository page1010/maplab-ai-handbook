# -*- coding: utf-8 -*-
"""ads_copy_review_card.py — 把線上文案表畫成「Telegram 看得見」的驗收圖卡

由來:Owner msg 2026-10-01T18:07:33「sheet連結有一個問題,我看不到縮圖,
telegram 呈現的驗收方式要在討論一下如何優化」。

為什麼要自己畫圖:Google Sheet 要登入才看得到,Telegram 的連結預覽爬蟲拿到的是
登入頁,所以不論連結怎麼貼都不會有縮圖——這是結構性的,不是連結打錯。
要讓 Owner 在 Telegram 裡直接看到字,只能把內容畫成圖送過去。

用法:
  python3 scripts/ads_copy_review_card.py <快照TSV> <v7檔> <輸出目錄> [只畫這個廣告的關鍵字]

一張圖 = 一支廣告。每一則畫三段:現在帳號上的字(灰)、建議換成(黑)、閘門命中(紅)。
底部固定印驗收指令,讓 Owner 在 Telegram 裡直接回字就能定稿。
"""
import io
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W = 1080
PAD = 44
BG = (255, 255, 255)
INK = (24, 24, 27)
GREY = (134, 134, 142)
RED = (198, 40, 40)
GREEN = (27, 122, 68)
LINE = (226, 226, 230)

FONT_CANDIDATES = [
    '/System/Library/Fonts/PingFang.ttc',
    '/System/Library/Fonts/STHeiti Medium.ttc',
    '/System/Library/Fonts/Hiragino Sans GB.ttc',
    '/System/Library/Fonts/Supplemental/Songti.ttc',
]


def font(size):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


F_TITLE = font(40)
F_SUB = font(25)
F_LABEL = font(23)
F_BODY = font(31)
F_SMALL = font(23)


def wrap(draw, text, fnt, maxw):
    """逐字量寬換行。中文沒有空白可切,只能一個字一個字量。"""
    lines, cur = [], ''
    for ch in text:
        if ch == '\n':
            lines.append(cur)
            cur = ''
            continue
        if draw.textlength(cur + ch, font=fnt) > maxw and cur:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines or ['']


def load(snap, v7path):
    rows = [l.rstrip('\n').split('\t') for l in io.open(snap, encoding='utf-8')]
    hdr = rows[0]
    w = len(hdr)
    ix = {k: [i for i, h in enumerate(hdr) if h.startswith(k)][0]
          for k in ('編號', '廣告', '版位', '欄位', '現行文案', '閘門命中')}
    body = [(r + [''] * (w - len(r)))[:w] for r in rows[1:] if r and r[0].strip()]
    v7 = {}
    for l in io.open(v7path, encoding='utf-8'):
        l = l.rstrip('\n')
        if not l or l.startswith('#'):
            continue
        no, txt = l.split('\t', 1)
        v7[no.strip()] = txt.strip()
    return ix, body, v7


def render_ad(ad, items, outdir):
    """items = [(編號, 版位, 欄位, 現行, 建議, 閘門)]"""
    img = Image.new('RGB', (W, 4000), BG)
    d = ImageDraw.Draw(img)
    maxw = W - PAD * 2
    y = PAD

    d.text((PAD, y), ad, font=F_TITLE, fill=INK)
    y += 54
    d.text((PAD, y), '線上文案表驗收卡 / 現在帳號上的字 vs 建議換成的字', font=F_SUB, fill=GREY)
    y += 44
    d.line([(PAD, y), (W - PAD, y)], fill=INK, width=3)
    y += 28

    for no, pos, col, cur, sug, hit in items:
        # 分隔符只用 ASCII:STHeiti 沒有「・」這個字,會畫成豆腐格
        d.text((PAD, y), '編號 %s / %s / %s' % (no, pos, col), font=F_LABEL, fill=INK)
        y += 36

        d.text((PAD, y), '現在帳號上', font=F_SMALL, fill=GREY)
        y += 30
        for ln in wrap(d, cur or '(空白)', F_BODY, maxw):
            d.text((PAD, y), ln, font=F_BODY, fill=GREY)
            y += 42
        y += 8

        d.text((PAD, y), '建議換成', font=F_SMALL, fill=GREEN)
        y += 30
        for ln in wrap(d, sug or '(本次不建議動)', F_BODY, maxw):
            d.text((PAD, y), ln, font=F_BODY, fill=INK)
            y += 42
        y += 8

        if hit and hit not in ('通過', '不適用'):
            for ln in wrap(d, '閘門命中:' + hit, F_SMALL, maxw):
                d.text((PAD, y), ln, font=F_SMALL, fill=RED)
                y += 30
        y += 18
        d.line([(PAD, y), (W - PAD, y)], fill=LINE, width=2)
        y += 26

    y += 6
    for ln in wrap(d, '要改哪一則,直接回「編號＋新字」;照建議就回「編號 OK」;'
                      '整支都可以就回「廣告編號 全可」。回完這邊寫進線上表,不必自己開 sheet。',
                   F_SMALL, maxw):
        d.text((PAD, y), ln, font=F_SMALL, fill=GREY)
        y += 32
    y += PAD

    return img.crop((0, 0, W, y))


def main():
    snap, v7path, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
    only = sys.argv[4] if len(sys.argv) > 4 else None
    os.makedirs(outdir, exist_ok=True)
    ix, body, v7 = load(snap, v7path)

    groups = {}
    for r in body:
        no = r[ix['編號']].strip()
        if no not in v7:
            continue
        groups.setdefault(r[ix['廣告']].strip(), []).append(
            (no, r[ix['版位']].strip(), r[ix['欄位']].strip(),
             r[ix['現行文案']].strip(), v7[no], r[ix['閘門命中']].strip()))

    made = []
    for ad, items in groups.items():
        if only and only not in ad:
            continue
        img = render_ad(ad, items, outdir)
        safe = ad.split()[1] if len(ad.split()) > 1 else ad.replace(' ', '_')
        p = os.path.join(outdir, 'review_%s.png' % safe)
        img.save(p)
        made.append((ad, len(items), p, img.size))
    for ad, n, p, size in made:
        print('%s | %d 則 | %dx%d | %s' % (ad, n, size[0], size[1], os.path.basename(p)))
    print('共', len(made), '張,存在', outdir)


if __name__ == '__main__':
    main()

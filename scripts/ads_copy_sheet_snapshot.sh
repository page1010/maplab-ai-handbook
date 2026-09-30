#!/usr/bin/env bash
# ads_copy_sheet_snapshot.sh — 線上文案定稿表:留存快照 + 對比抓差別
#
# 由來:Owner msg 6430(2026-09-30T22:40:19)「你自己留存對比抓差別」。
# Owner 會直接在線上表的「Owner 定稿」欄改字。只把改完的字抄上帳號,學不到東西;
# 本腳本每次跑都留一份快照,並跟上一份逐格比對,把 Owner 動過的字單獨抓出來,
# 再拿 Owner 的字回頭跑自家口氣閘門——Owner 的字被自家閘門判 FAIL,錯的是閘門不是 Owner。
#
# 用法:bash scripts/ads_copy_sheet_snapshot.sh
# 產出:handoff/ads_copy_sheet_snapshots/<YYYYMMDD_HHMM>/<頁籤>.tsv(每次一份,只進不退)
#       handoff/ADS_COPY_OWNER_EDIT_LEDGER.md(Owner 改字帳本,逐次追加)
#       /tmp/a0_owner_final_lines.txt(Owner 定稿欄抽出的字,供閘門回跑)
#       /tmp/a0_sheet_diff_report.txt(本次逐格差異全文)
#
# 安全:金鑰只在本腳本內部流動,不 echo、不寫進快照、不入 commit;對外只印 HTTP 狀態碼。
set -uo pipefail

REPO=/Users/pagemacmini/maplab-ai-handbook

/usr/bin/python3 - <<'PY'
# -*- coding: utf-8 -*-
import json, os, glob, time, urllib.request, urllib.parse

REPO='/Users/pagemacmini/maplab-ai-handbook'
# 自測用:A0_SNAP_ROOT / A0_SNAP_LEDGER 可把快照與帳本改指到 /tmp,
# 這樣驗「對比抓差別」這段邏輯時不會污染正式快照序列(讀表仍是唯讀)。
SNAPROOT=os.environ.get('A0_SNAP_ROOT') or os.path.join(REPO,'handoff/ads_copy_sheet_snapshots')
LEDGER=os.environ.get('A0_SNAP_LEDGER') or os.path.join(REPO,'handoff/ADS_COPY_OWNER_EDIT_LEDGER.md')
SID='1v-3HYH79aTEnaOBYWRzjGM5TERQe_HQ0UgBTF0FH7MM'
TABS=['廣告文案','影片疊字','說明與實數']
os.makedirs(SNAPROOT,exist_ok=True)

t=json.load(open(os.path.expanduser('~/.claude/mcp-keys/google-token.json')))
d=urllib.parse.urlencode({'client_id':t['client_id'],'client_secret':t['client_secret'],
 'refresh_token':t['refresh_token'],'grant_type':'refresh_token'}).encode()
with urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token',data=d)) as r:
    AT=json.load(r)['access_token']
H={'Authorization':'Bearer '+AT}

stamp=time.strftime('%Y%m%d_%H%M')
snapdir=os.path.join(SNAPROOT,stamp)
os.makedirs(snapdir,exist_ok=True)
prior=sorted(d_ for d_ in glob.glob(os.path.join(SNAPROOT,'*')) if os.path.isdir(d_) and os.path.basename(d_)!=stamp)

def cell(c): return c.replace('\t',' ').replace('\n','\\n')

diffs=[]; final=[]; counts={}
for tab in TABS:
    u='https://sheets.googleapis.com/v4/spreadsheets/%s/values/%s'%(SID,urllib.parse.quote(tab))
    with urllib.request.urlopen(urllib.request.Request(u,headers=H)) as r:
        print('GET',tab,'HTTP',r.status)
        rows=json.load(r).get('values',[])
    if not rows:
        print('  空頁籤,跳過'); continue
    W=max(len(x) for x in rows)
    norm=[(x+['']*(W-len(x)))[:W] for x in rows]
    hdr=norm[0]
    counts[tab]=len(norm)
    p=os.path.join(snapdir,tab+'.tsv')
    with open(p,'w',encoding='utf-8') as f:
        for x in norm:
            f.write('\t'.join(cell(c) for c in x)+'\n')
    print('  存檔',tab+'.tsv','列數',len(norm))

    # 逐格對比上一份快照的同名頁籤
    if prior:
        base=os.path.join(prior[-1],tab+'.tsv')
        if os.path.exists(base):
            old=[l.rstrip('\n').split('\t') for l in open(base,encoding='utf-8')]
            oldmap={x[0]:x for x in old[1:] if x}
            for x in norm[1:]:
                o=oldmap.get(x[0])
                if o is None:
                    diffs.append((tab,x[0],'(整列新增)','','')); continue
                o=(o+['']*(W-len(o)))[:W]
                for i in range(W):
                    if o[i]!=x[i]:
                        diffs.append((tab,x[0],hdr[i] if i<len(hdr) else '第%d欄'%(i+1),o[i],x[i]))

    # Owner 定稿欄
    ci=[i for i,h in enumerate(hdr) if 'Owner 定稿' in h]
    if ci:
        for x in norm[1:]:
            if x[ci[0]].strip():
                final.append((tab,x[0],x[ci[0]].strip()))

print('對比基準',os.path.basename(prior[-1]) if prior else '無(首份快照,只留存不比對)')
print('差異格數',len(diffs))
for x in diffs[:40]:
    print('  [%s %s] %s: %s => %s'%x)
print('Owner 定稿欄已填列數',len(final))

with open('/tmp/a0_owner_final_lines.txt','w',encoding='utf-8') as f:
    f.write('# Owner 在線上表定稿欄填的字(ads_copy_sheet_snapshot.sh 抽出,一行一則)\n')
    for tab,no,txt in final:
        f.write(txt+'\n')
with open('/tmp/a0_sheet_diff_report.txt','w',encoding='utf-8') as f:
    f.write('快照 %s / 差異格數 %d / Owner 定稿已填 %d 則\n'%(stamp,len(diffs),len(final)))
    for x in diffs:
        f.write('[%s %s] %s: %s => %s\n'%x)
    for tab,no,txt in final:
        f.write('定稿 [%s %s] %s\n'%(tab,no,txt))

row='| %s | %s | %s | %d | %d | %s |\n'%(
    time.strftime('%Y-%m-%d %H:%M'), stamp,
    '/'.join('%s %d列'%(k,v) for k,v in counts.items()),
    len(diffs), len(final),
    ('對比 '+os.path.basename(prior[-1]) if prior else '首份,無對比基準'))
if not os.path.exists(LEDGER):
    with open(LEDGER,'w',encoding='utf-8') as f:
        f.write('# 線上文案定稿表 — 留存與差別帳本\n\n')
        f.write('> 由來:Owner msg 6430(2026-09-30T22:40:19)「你自己留存對比抓差別」。\n')
        f.write('> 每次跑 `scripts/ads_copy_sheet_snapshot.sh` 追加一列;快照只進不退,不覆蓋、不刪舊。\n')
        f.write('> 表 ID 1v-3HYH79aTEnaOBYWRzjGM5TERQe_HQ0UgBTF0FH7MM。\n')
        f.write('> 規則:Owner 動過的字一律以 Owner 版為準;Owner 的字被自家閘門判 FAIL,改閘門不改 Owner 的字。\n\n')
        f.write('| 時間 | 快照 | 頁籤列數 | 差異格數 | Owner 定稿已填 | 對比基準 |\n|---|---|---|---|---|---|\n')
with open(LEDGER,'a',encoding='utf-8') as f:
    f.write(row)
print('帳本已追加',os.path.basename(LEDGER))
PY

echo "=== Owner 定稿字回頭跑自家口氣閘門(Owner 的字被判 FAIL=錯的是閘門) ==="
if [ "$(grep -vc '^#' /tmp/a0_owner_final_lines.txt)" -gt 0 ]; then
  bash "$REPO/scripts/ad_copy_voice_check.sh" /tmp/a0_owner_final_lines.txt ad
else
  echo "Owner 定稿欄目前是空的,沒有字可以跑。"
fi

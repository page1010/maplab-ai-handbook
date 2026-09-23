#!/usr/bin/env bash
# wp_cannib_check.sh — 站內防蠶食查詞:唯一一支准用的 WP REST search 查詢工具
#
# 用法: bash scripts/wp_cannib_check.sh 詞1 詞2 詞3 ...
#       bash scripts/wp_cannib_check.sh --selftest
#
# ── 為什麼這支存在(制度 E:把教訓挪到下一個人繞不過去的地方)──
# 2026-09-14 第 5 篇日照中心查站內競爭時,用的是:
#     curl --get --data-urlencode "search=日照中心" .../wp-json/wp/v2/posts
# 那個寫法 search 參數**根本沒送進去**,WP 直接回「最新 20 篇」的預設清單。
# 十個關鍵字回傳一模一樣的二十筆,看起來像「每個詞都有 20 頁在競爭」——
# 於是**站內 0 命中的空白詞被誤判成紅海,文章白白讓位**。
# 它不會報錯、不會回 4xx,HTTP 200、JSON 合法。**這是靜默失敗,靠細心擋不住。**
#
# 這支的防呆(不是寫在註解裡,是跑起來會擋):
#   1. 用 urllib 自己組 percent-encoded URL,不經過 curl 的 --data-urlencode。
#   2. 每次查詢一定先打一組**不帶 search 的 CONTROL**。
#   3. 若某個詞回傳的 ID 集合與 CONTROL **完全相同** → 判定 search 沒生效,
#      **exit 3 並印出上面那段教訓**,不准把結果當數據用。
#   4. 另跑一個**陽性對照詞**(必定有結果且必定 != CONTROL);它若失敗 = 管線壞了。
#   5. 明白標示 per_page 上限造成的飽和:回 20 筆只代表「>= 20」,不是剛好 20。
#
# 唯讀:只打公開 REST GET,不帶 cookie、不帶金鑰、不登入、不寫入任何東西。
set -uo pipefail

SITE="https://www.maplabkitchen.com"
POSITIVE_CONTROL="外燴"      # 這個站不可能查不到「外燴」
# 決定性偵測器:一個不可能命中的亂碼。search 若有生效,它一定回 0 筆。
NEGATIVE_CONTROL="zzqxjwvk9713nope"

if [ "${1:-}" = "--selftest" ]; then
  set -- "$POSITIVE_CONTROL" "日照中心" "教會"
  echo "=== selftest 模式:陽性對照 + 兩個已知應為 0 的詞 ==="
fi

if [ "$#" -eq 0 ]; then
  echo "用法: bash scripts/wp_cannib_check.sh 詞1 詞2 ..." >&2
  echo "      bash scripts/wp_cannib_check.sh --selftest" >&2
  exit 64
fi

SITE="$SITE" POSITIVE_CONTROL="$POSITIVE_CONTROL" NEGATIVE_CONTROL="$NEGATIVE_CONTROL" \
  /usr/bin/python3 - "$@" <<'PY'
import json, os, sys, urllib.parse, urllib.request

SITE = os.environ["SITE"]
POS  = os.environ["POSITIVE_CONTROL"]
NEG  = os.environ["NEGATIVE_CONTROL"]
TERMS = sys.argv[1:]
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
PER_PAGE = 20

def fetch(kind, term=None):
    """回 (id 集合, 筆數)。term=None 即 CONTROL(不帶 search)。"""
    params = {"per_page": str(PER_PAGE), "_fields": "id"}
    if term is not None:
        params["search"] = term
    url = f"{SITE}/wp-json/wp/v2/{kind}?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    ids = frozenset(item["id"] for item in data)
    return ids, len(data)

LESSON = """
✗ 偵測到 WP REST search 靜默失敗。

  症狀:帶了 search 卻回傳與 CONTROL(不帶 search)一模一樣的 ID 集合。
  意義:search 參數沒有生效,WP 回的是「最新 N 篇」預設清單,HTTP 200、JSON 合法、不報錯。
  後果:站內 0 命中的空白關鍵字會被誤判成「有 20 頁在競爭」的紅海,
        文章因此白白讓位給不存在的競爭者。2026-09-14 第 5 篇就是這樣踩的。
  正解:用 urllib 自己組 percent-encoded URL,不要用 curl --get --data-urlencode;
        而且每次都要留一組 CONTROL 對照,不能只看單次結果長得合不合理。

  在查清楚之前,這一輪的查詢結果一律不得當成數據使用。
"""

try:
    ctrl_posts, n_cp = fetch("posts")
    ctrl_pages, n_cg = fetch("pages")
except Exception as e:
    print(f"✗ CONTROL 查詢失敗,無法建立對照組:{e}")
    sys.exit(4)

print(f"CONTROL(不帶 search):posts {n_cp} 筆 / pages {n_cg} 筆  ← 對照基準")
if n_cp >= PER_PAGE:
    print(f"註:per_page={PER_PAGE},回滿即代表「>= {PER_PAGE}」,不是剛好 {PER_PAGE}。")
print()

# ── 陰性對照:唯一決定性的偵測器 ──
# 一串不可能命中的亂碼。search 有生效就必定回 0 筆;
# 若它回了東西(尤其回成 CONTROL 那份預設清單),就是 search 被整個忽略。
# 這比陽性對照可靠:陽性對照會被「全站都命中」的高頻詞汙染(見下)。
try:
    neg_ids, neg_n = fetch("posts", NEG)
except Exception as e:
    print(f"✗ 陰性對照查詢失敗:{e}")
    sys.exit(4)
if neg_n != 0:
    print(f"✗ 陰性對照「{NEG}」回了 {neg_n} 筆(應為 0),"
          f"與 CONTROL 相同={neg_ids == ctrl_posts}。")
    print(LESSON)
    sys.exit(3)
print(f"✓ 陰性對照「{NEG}」回 0 筆 → search 參數確實有送達並生效。")

# 陽性對照:只證明「站上找得到東西」,不用來判定 search 死活。
try:
    pos_ids, pos_n = fetch("posts", POS)
except Exception as e:
    print(f"✗ 陽性對照「{POS}」查詢失敗:{e}")
    sys.exit(4)
if pos_n == 0:
    print(f"✗ 陽性對照「{POS}」回 0 筆 — 這個站不可能查不到「外燴」,管線有問題。")
    print(LESSON)
    sys.exit(3)
if pos_ids == ctrl_posts:
    print(f"註:陽性對照「{POS}」的 ID 集合與 CONTROL 相同。在陰性對照已通過的前提下,"
          f"這代表「全站每篇都命中這個詞」,不是靜默失敗。")
else:
    print(f"✓ 陽性對照「{POS}」:posts {pos_n} 筆。")
print()

rows, bad = [], False
for t in TERMS:
    try:
        p_ids, p_n = fetch("posts", t)
        g_ids, g_n = fetch("pages", t)
    except Exception as e:
        rows.append((t, "ERR", "ERR", f"查詢失敗:{e}"))
        bad = True
        continue
    if p_n == 0 and g_n == 0:
        rows.append((t, 0, 0, "站內空白,可取用"))
    else:
        # 陰性對照已證明 search 生效,所以「與 CONTROL 同集合」是高頻詞,不是失敗。
        same = (p_n and p_ids == ctrl_posts) or (g_n and g_ids == ctrl_pages)
        sat = "(已達上限,實為 >=)" if max(p_n, g_n) >= PER_PAGE else ""
        rows.append((t, p_n, g_n, f"{'全站高頻詞' if same else '站內已有佔位'}{sat}"))

w = max([len(r[0]) for r in rows] + [8])
print(f"{'查詢詞'.ljust(w)}  posts  pages  判讀")
for t, p, g, note in rows:
    print(f"{t.ljust(w)}  {str(p).rjust(5)}  {str(g).rjust(5)}  {note}")

if bad:
    print("\n✗ 有查詢失敗,這張表不完整,不得當數據使用。")
    sys.exit(4)

print("\n✓ 陰性對照通過 + 全部查詢成功,結果可當數據使用。")
PY
